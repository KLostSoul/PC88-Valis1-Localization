#!/usr/bin/env python3
"""Reproduce the integrated Valis 1 PC-8801 build from user-supplied originals.

The repository distributes only IPS deltas and this verifier.  It never searches
for, downloads, copies, or overwrites an original D88 or KANJI1 ROM.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import struct
import sys
import zipfile
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path


D88_SIZE = 414_992
D88_HEADER_SIZE = 0x2B0
D88_PAYLOAD_SIZE = 407_552
D88_BASE_SHA256 = "7404998ee7e94e14d065a11e55bc26f7f8733202eec6774610a20a6d0b5a1fdf"
D88_RESULT_SHA256 = "18e274dc730902f90e4d3939ad3ac2853c927d19baf896cee88e5b22321427b8"
D88_HOLD_OFFSET = 0x079AC

KANJI_SIZE = 0x20000
KANJI_BASE_SHA256 = "f6c1c5022fe5935f6dfa3eb919e51441e75191270b639edcb7938b3bce41f6a3"
KANJI_RESULT_SHA256 = "3a4ce60dc4a23d7918a8726b99c2192c9420313bab40c50880eea3a387243f45"
KANJI_GLYPH_SIZE = 0x20

IPS_FACTS = {
    "disk": {
        "sha256": "7f14c7b5d6961e234f702aa3e6007944ad3ec8231af225f6296ef3491e1eff53",
        "file_size": 29_748,
        "records": 1_282,
        "raw_records": 1_282,
        "rle_records": 0,
        "patched_bytes": 23_330,
        "min_offset": 0x316B,
        "max_offset_inclusive": 0x1DB54,
    },
    "kanji": {
        "sha256": "1cb66ed56faf20a29cf0ee860805a14fc7d9132f825c22fa846c3bb81a70bc7c",
        "file_size": 22_759,
        "records": 2_026,
        "raw_records": 2_026,
        "rle_records": 0,
        "patched_bytes": 12_621,
        "min_offset": 0x2F41,
        "max_offset_inclusive": 0x1FFFF,
    },
}


@dataclass(frozen=True)
class IPSRecord:
    offset: int
    data: bytes
    kind: str


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def parse_ips_blob(blob: bytes, label: str) -> tuple[bytes, list[IPSRecord]]:
    if blob[:5] != b"PATCH":
        raise ValueError(f"{label}: missing IPS PATCH header")
    cursor = 5
    records: list[IPSRecord] = []
    while True:
        if cursor + 3 > len(blob):
            raise ValueError(f"{label}: truncated IPS record or missing EOF")
        if blob[cursor:cursor + 3] == b"EOF":
            if cursor + 3 != len(blob):
                raise ValueError(f"{label}: bytes after IPS EOF")
            return blob, records
        if cursor + 5 > len(blob):
            raise ValueError(f"{label}: truncated IPS record header")
        offset = int.from_bytes(blob[cursor:cursor + 3], "big")
        size = int.from_bytes(blob[cursor + 3:cursor + 5], "big")
        cursor += 5
        if size:
            end = cursor + size
            if end > len(blob):
                raise ValueError(f"{label}: truncated raw record at 0x{offset:06X}")
            records.append(IPSRecord(offset, blob[cursor:end], "raw"))
            cursor = end
            continue
        if cursor + 3 > len(blob):
            raise ValueError(f"{label}: truncated RLE record at 0x{offset:06X}")
        repeat = int.from_bytes(blob[cursor:cursor + 2], "big")
        if repeat == 0:
            raise ValueError(f"{label}: zero-length RLE record at 0x{offset:06X}")
        value = blob[cursor + 2]
        records.append(IPSRecord(offset, bytes([value]) * repeat, "rle"))
        cursor += 3


def parse_ips(path: Path) -> tuple[bytes, list[IPSRecord]]:
    return parse_ips_blob(path.read_bytes(), str(path))


def ips_summary(blob: bytes, records: list[IPSRecord]) -> dict:
    if not records:
        raise ValueError("IPS contains no records")
    return {
        "file_size": len(blob),
        "sha256": sha256(blob),
        "records": len(records),
        "raw_records": sum(record.kind == "raw" for record in records),
        "rle_records": sum(record.kind == "rle" for record in records),
        "patched_bytes": sum(len(record.data) for record in records),
        "min_offset": min(record.offset for record in records),
        "max_offset_inclusive": max(record.offset + len(record.data) - 1 for record in records),
    }


def apply_ips(base: bytes, records: list[IPSRecord]) -> bytes:
    output = bytearray(base)
    for record in records:
        end = record.offset + len(record.data)
        if end > len(output):
            raise ValueError(f"IPS writes past input size at 0x{record.offset:06X}")
        output[record.offset:end] = record.data
    return bytes(output)


def u16(data: bytes, offset: int) -> int:
    return struct.unpack_from("<H", data, offset)[0]


def u32(data: bytes, offset: int) -> int:
    return struct.unpack_from("<I", data, offset)[0]


def d88_report(data: bytes) -> dict:
    report = {
        "size": len(data),
        "sha256": sha256(data),
        "header_declared_size": None,
        "track_count": 0,
        "payload_size": 0,
        "hold_byte": data[D88_HOLD_OFFSET] if len(data) > D88_HOLD_OFFSET else None,
        "structure_ok": False,
        "errors": [],
    }
    if len(data) < D88_HEADER_SIZE:
        report["errors"].append("file is shorter than the D88 header")
        return report
    report["header_declared_size"] = u32(data, 0x1C)
    pointers = [u32(data, 0x20 + index * 4) for index in range(164)]
    nonzero = [(index, pointer) for index, pointer in enumerate(pointers) if pointer]
    if [index for index, _ in nonzero] != list(range(80)):
        report["errors"].append("expected track pointers 0 through 79")
        return report
    payload_size = 0
    try:
        for position, (track, pointer) in enumerate(nonzero):
            limit = nonzero[position + 1][1] if position + 1 < len(nonzero) else len(data)
            if pointer < D88_HEADER_SIZE or pointer + 16 > limit or limit > len(data):
                raise ValueError(f"track {track}: invalid boundary")
            sector_count = u16(data, pointer + 4)
            expected_count = 16 if track < 2 else 5
            expected_size = 256 if track < 2 else 1024
            if sector_count != expected_count:
                raise ValueError(f"track {track}: expected {expected_count} sectors, got {sector_count}")
            cursor = pointer
            for _ in range(sector_count):
                if cursor + 16 > limit:
                    raise ValueError(f"track {track}: truncated sector header")
                declared_count = u16(data, cursor + 4)
                sector_size = u16(data, cursor + 14)
                data_end = cursor + 16 + sector_size
                if declared_count != sector_count or sector_size != expected_size or data_end > limit:
                    raise ValueError(f"track {track}: invalid sector metadata")
                payload_size += sector_size
                cursor = data_end
            if cursor != limit:
                raise ValueError(f"track {track}: unparsed bytes remain")
    except (IndexError, struct.error, ValueError) as exc:
        report["errors"].append(str(exc))
        return report
    report["track_count"] = len(nonzero)
    report["payload_size"] = payload_size
    report["structure_ok"] = (
        len(data) == D88_SIZE
        and report["header_declared_size"] == len(data)
        and payload_size == D88_PAYLOAD_SIZE
    )
    if len(data) != D88_SIZE:
        report["errors"].append(f"expected file size {D88_SIZE}")
    if report["header_declared_size"] != len(data):
        report["errors"].append("D88 header size does not equal file size")
    if payload_size != D88_PAYLOAD_SIZE:
        report["errors"].append(f"expected payload size {D88_PAYLOAD_SIZE}")
    return report


def require_hash(actual: str, expected: str, label: str, allow_unknown: bool) -> bool:
    if actual == expected:
        return True
    if not allow_unknown:
        raise ValueError(f"{label} SHA-256 mismatch: {actual} (expected {expected})")
    return False


def inspect_ips(kind: str, path: Path, allow_unknown: bool) -> dict:
    blob, records = parse_ips(path)
    summary = ips_summary(blob, records)
    expected = IPS_FACTS[kind]
    known = require_hash(summary["sha256"], expected["sha256"], f"{kind} IPS", allow_unknown)
    for key, value in expected.items():
        if key != "sha256" and summary[key] != value:
            if not allow_unknown:
                raise ValueError(f"{kind} IPS {key} mismatch: {summary[key]} (expected {value})")
            known = False
    summary["known_artifact"] = known
    if kind == "kanji":
        slots = {
            slot
            for record in records
            for slot in range(record.offset // KANJI_GLYPH_SIZE,
                              (record.offset + len(record.data) + KANJI_GLYPH_SIZE - 1) // KANJI_GLYPH_SIZE)
        }
        summary.update({"record_slots_touched": len(slots), "record_slot_min": min(slots), "record_slot_max": max(slots)})
    return summary


def build_one(kind: str, base_path: Path, ips_path: Path, output_path: Path, allow_unknown: bool) -> dict:
    base = base_path.read_bytes()
    blob, records = parse_ips(ips_path)
    if kind == "disk":
        size, base_hash, result_hash = D88_SIZE, D88_BASE_SHA256, D88_RESULT_SHA256
        base_structure = d88_report(base)
        if not base_structure["structure_ok"]:
            raise ValueError("Disk A base does not pass the expected D88 structure")
    else:
        size, base_hash, result_hash = KANJI_SIZE, KANJI_BASE_SHA256, KANJI_RESULT_SHA256
        base_structure = None
    if len(base) != size:
        raise ValueError(f"{kind} base must be {size} bytes")
    known_base = require_hash(sha256(base), base_hash, f"{kind} base", allow_unknown)
    ips = inspect_ips(kind, ips_path, allow_unknown)
    result = apply_ips(base, records)
    if len(result) != len(base):
        raise ValueError("IPS application changed file size")
    result_structure = d88_report(result) if kind == "disk" else None
    if kind == "disk" and not result_structure["structure_ok"]:
        raise ValueError("Disk A result does not pass the expected D88 structure")
    changed = [index for index, (left, right) in enumerate(zip(base, result)) if left != right]
    report = {
        "kind": kind,
        "base": {"path": str(base_path), "size": len(base), "sha256": sha256(base)},
        "ips": {"path": str(ips_path), **ips},
        "result": {"path": str(output_path), "size": len(result), "sha256": sha256(result)},
        "changed_bytes": len(changed),
        "known_base": known_base,
        "known_ips": ips["known_artifact"],
    }
    if kind == "disk":
        report["d88_structure"] = result_structure
        report["hold"] = {"offset": D88_HOLD_OFFSET, "base": base[D88_HOLD_OFFSET], "result": result[D88_HOLD_OFFSET]}
    else:
        report["changed_slots"] = len({index // KANJI_GLYPH_SIZE for index in changed})
    if known_base and ips["known_artifact"] and report["result"]["sha256"] != result_hash:
        raise ValueError(f"{kind} result SHA-256 mismatch: {report['result']['sha256']} (expected {result_hash})")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(result)
    return report


def _member_hash(blob: bytes) -> dict:
    return {"size": len(blob), "sha256": sha256(blob)}


def _docx_text_stats(blob: bytes) -> dict:
    """Read the complete document XML for audit counts without semantic remapping."""
    with zipfile.ZipFile(io.BytesIO(blob)) as document:
        xml_blob = document.read("word/document.xml")
    root = ET.fromstring(xml_blob)
    text_nodes = [node.text or "" for node in root.iter() if node.tag.rsplit("}", 1)[-1] == "t"]
    text = "".join(text_nodes)
    return {"text_runs": len(text_nodes), "codepoints": len(text), "utf8_bytes": len(text.encode("utf-8"))}


def _report_summary(report: dict) -> dict:
    """Keep only numerical/range audit facts; never copy translation rows."""
    allowed = (
        "runtime_range", "runtime_range_written", "body_runtime_range", "body_range",
        "terminator", "terminator_expected", "decoded_stream_bytes_written",
        "decoded_bytes_written", "changed_byte_count", "changed_record_count",
        "outside_change_count", "tail_changed_count", "payload_range", "stats",
        "document_validation", "verification", "row_counts",
    )
    return {key: report[key] for key in allowed if key in report}


def _audit_final_bundle(archive: zipfile.ZipFile, outer_name: str) -> dict:
    outer_blob = archive.read(outer_name)
    with zipfile.ZipFile(io.BytesIO(outer_blob)) as bundle:
        members = [info.filename for info in bundle.infolist() if not info.is_dir()]
        ips_names = [name for name in members if name.lower().endswith(".ips")]
        d88_names = [name for name in members if name.lower().endswith(".d88")]
        json_names = [name for name in members if name.lower().endswith(".json")]
        csv_names = [name for name in members if name.lower().endswith(".csv")]
        if len(ips_names) != 1 or len(d88_names) != 1 or not json_names or not csv_names:
            raise ValueError(f"{outer_name}: expected one IPS, one D88, JSON report, and CSV evidence")
        report_name = next((name for name in json_names if "report" in name.lower()), json_names[0])
        report = json.loads(bundle.read(report_name).decode("utf-8-sig"))
        ips_blob = bundle.read(ips_names[0])
        ips_blob, ips_records = parse_ips_blob(ips_blob, f"{outer_name}:{ips_names[0]}")
        member_audit = {
            name: _member_hash(bundle.read(name))
            for name in sorted(members)
            if not name.lower().endswith((".png", ".jpg", ".jpeg", ".psd"))
        }
        return {
            "outer_member": outer_name,
            "outer": _member_hash(outer_blob),
            "members": member_audit,
            "ips": {"path": ips_names[0], **ips_summary(ips_blob, ips_records)},
            "report": {"path": report_name, "summary": _report_summary(report)},
        }


def audit_source_archive(source_zip: Path) -> dict:
    """Audit final bundle structure and provenance without extracting game data."""
    source_blob = source_zip.read_bytes()
    with zipfile.ZipFile(io.BytesIO(source_blob)) as archive:
        names = [info.filename for info in archive.infolist() if not info.is_dir()]
        root_disk = "Valis_Korean_Disk_A_Patch_Ver_1.02.ips"
        root_kanji = "VALIS_KANJI1_ROM_Patch_Ver_1.02.ips"
        for required in (root_disk, root_kanji):
            if required not in names:
                raise ValueError(f"source archive is missing {required}")
        final_names = [
            name for name in names
            if (name.startswith("Block 1/4 ") or name.startswith("Block 2/")
                or name.startswith("Block 3/") or name.startswith("Block 4/")
                or name.startswith("Block 5/") or name.startswith("Block 6/")
                or name.startswith("Ednding/"))
            and "patch_bundle" in name.lower() and name.lower().endswith(".zip")
        ]
        expected_count = 7
        if len(final_names) != expected_count:
            raise ValueError(f"expected {expected_count} final bundles, found {len(final_names)}")
        nested_skill_names = [name for name in names if name.endswith("Valis1_PC88_Localization_Skills_IPS_Only_2026-08-09.zip")]
        if len(nested_skill_names) != 1:
            raise ValueError("expected one IPS-only reproduction skill archive")
        nested_skill_blob = archive.read(nested_skill_names[0])
        with zipfile.ZipFile(io.BytesIO(nested_skill_blob)) as skill_archive:
            disk_asset = "skills/reproduce-valis1-pc88-ko/assets/Valis_Korean_Disk_A_Patch_Ver_1.02.ips"
            kanji_asset = "skills/reproduce-valis1-pc88-ko/assets/VALIS_KANJI1_ROM_Patch_Ver_1.02.ips"
            for required in (disk_asset, kanji_asset):
                if required not in skill_archive.namelist():
                    raise ValueError(f"nested skill archive is missing {required}")
            root_disk_blob = archive.read(root_disk)
            root_kanji_blob = archive.read(root_kanji)
            if root_disk_blob != skill_archive.read(disk_asset) or root_kanji_blob != skill_archive.read(kanji_asset):
                raise ValueError("root IPS pair does not exactly match the nested reproduction skill assets")
        top_level_inventory = []
        for name in sorted(names):
            blob = archive.read(name)
            entry = {"path": name, **_member_hash(blob)}
            if name.lower().endswith(".zip"):
                with zipfile.ZipFile(io.BytesIO(blob)) as nested:
                    nested_names = [info.filename for info in nested.infolist() if not info.is_dir()]
                    entry["nested_file_count"] = len(nested_names)
                    entry["nested_name_manifest_sha256"] = sha256("\n".join(sorted(nested_names)).encode("utf-8"))
            top_level_inventory.append(entry)
        analysis_names = [name for name in names if name.startswith("Valis_Analysis_Documents_") and name.lower().endswith(".zip")]
        if len(analysis_names) != 1:
            raise ValueError("expected one 25-project/5-analysis document archive")
        analysis_blob = archive.read(analysis_names[0])
        with zipfile.ZipFile(io.BytesIO(analysis_blob)) as analysis_archive:
            doc_names = [name for name in analysis_archive.namelist() if name.lower().endswith(".docx")]
            project_docs = [name for name in doc_names if "project_analysis_documents/" in name]
            md_docs = [name for name in doc_names if "md_analysis_documents/" in name]
            if len(project_docs) != 25 or len(md_docs) != 5:
                raise ValueError(f"analysis archive must contain 25 project and 5 MD documents, found {len(project_docs)} and {len(md_docs)}")
            analysis_documents = []
            for name in sorted(doc_names):
                blob = analysis_archive.read(name)
                analysis_documents.append({"path": name, **_member_hash(blob), "text": _docx_text_stats(blob)})
        result = {
            "source_archive_inventory": {
                "file_count": len(names),
                "members": top_level_inventory,
            },
            "analysis_documents": {
                "archive": {"path": analysis_names[0], **_member_hash(analysis_blob)},
                "project_count": len(project_docs),
                "md_count": len(md_docs),
                "documents": analysis_documents,
            },
            "source_zip": {"name": source_zip.name, **_member_hash(source_blob)},
            "integrated_ips": {
                "disk": {"path": root_disk, **_member_hash(archive.read(root_disk)), **ips_summary(*parse_ips_blob(archive.read(root_disk), root_disk))},
                "kanji": {"path": root_kanji, **_member_hash(archive.read(root_kanji)), **ips_summary(*parse_ips_blob(archive.read(root_kanji), root_kanji))},
                "matches_nested_skill_assets": True,
            },
            "final_bundles": [_audit_final_bundle(archive, name) for name in sorted(final_names)],
            "reproduction_rule": "apply the integrated IPS pair to exact user-supplied originals; do not merge historical bundle streams",
            "copyright_scope": {
                "originals_extracted": False,
                "completed_images_published": False,
                "translation_rows_auto_mapped": False,
            },
        }
        return result


def cmd_inspect_d88(args: argparse.Namespace) -> int:
    report = d88_report(args.image.read_bytes())
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["structure_ok"] else 2


def cmd_inspect_ips(args: argparse.Namespace) -> int:
    print(json.dumps(inspect_ips(args.kind, args.ips, args.allow_unknown), ensure_ascii=False, indent=2))
    return 0


def cmd_audit_source(args: argparse.Namespace) -> int:
    report = audit_source_archive(args.source_zip)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


def cmd_build(args: argparse.Namespace) -> int:
    disk = build_one("disk", args.disk_base, args.disk_ips, args.output_dir / "Valis_Disk_A_reproduced.d88", args.allow_unknown)
    kanji = build_one("kanji", args.kanji_base, args.kanji_ips, args.output_dir / "KANJI1_Valis_reproduced.ROM", args.allow_unknown)
    report = {"build": "Valis 1 PC-8801 integrated 1.02", "disk": disk, "kanji": kanji}
    report_path = args.output_dir / "build-report.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    d88 = sub.add_parser("inspect-d88", help="validate D88 structure without changing it")
    d88.add_argument("image", type=Path)
    d88.set_defaults(func=cmd_inspect_d88)
    ips = sub.add_parser("inspect-ips", help="validate one repository IPS")
    ips.add_argument("kind", choices=("disk", "kanji"))
    ips.add_argument("ips", type=Path)
    ips.add_argument("--allow-unknown", action="store_true", help="inspect non-release IPS metadata")
    ips.set_defaults(func=cmd_inspect_ips)
    audit = sub.add_parser("audit-source", help="audit the complete source ZIP and final bundle provenance")
    audit.add_argument("--source-zip", required=True, type=Path)
    audit.add_argument("--output", required=True, type=Path)
    audit.set_defaults(func=cmd_audit_source)
    build = sub.add_parser("build", help="apply both IPS files to user-supplied originals")
    build.add_argument("--disk-base", required=True, type=Path)
    build.add_argument("--kanji-base", required=True, type=Path)
    build.add_argument("--disk-ips", type=Path, default=Path("patches/Valis_Korean_Disk_A_Patch_Ver_1.02.ips"))
    build.add_argument("--kanji-ips", type=Path, default=Path("patches/VALIS_KANJI1_ROM_Patch_Ver_1.02.ips"))
    build.add_argument("--output-dir", required=True, type=Path)
    build.add_argument("--allow-unknown", action="store_true", help="exploratory mode; not a release pass")
    build.set_defaults(func=cmd_build)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.func(args)
    except (OSError, ValueError, struct.error) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
