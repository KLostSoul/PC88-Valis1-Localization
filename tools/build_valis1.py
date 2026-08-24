#!/usr/bin/env python3
"""Build the Valis 1 localization from explicit source data.

This is a source-driven builder.  It requires the user's original Disk A and
KANJI1 ROM, then reads the completed source archive's CSV, DOCX tables, source
streams, reverse map, and VISUALTXT glyphs.  It does not read or apply IPS
files and never downloads or discovers copyrighted game images.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import struct
import sys
import zipfile
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


D88_SIZE = 414_992
KANJI_SIZE = 0x20000
GLYPH_SIZE = 32
D88_HEADER_SIZE = 0x2B0
D88_PAYLOAD_SIZE = 407_552
KNOWN_COMPLETION_BASE_SHA256 = "ae9e0d57219763cc575e66d38e92c78e7f3fc7a6acdeba0e5f13d7f7dd920a44"
KNOWN_LOGO_ONLY_SHA256 = "8e38dc6ca38a23feb68255bb6e99da45c2aef39ff5ed440dde517fddcf223227"

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
W_T = f"{{{W_NS}}}t"


def sha256(data: bytes | bytearray) -> str:
    return hashlib.sha256(bytes(data)).hexdigest()


def parse_hex_byte(value: str) -> int:
    return int(value.strip(), 16)


def compact_ranges(offsets: Iterable[int]) -> list[dict]:
    values = sorted(set(offsets))
    ranges: list[list[int]] = []
    for value in values:
        if not ranges or value != ranges[-1][-1] + 1:
            ranges.append([value])
        else:
            ranges[-1].append(value)
    return [{"start": f"0x{r[0]:05X}", "end": f"0x{r[-1]:05X}", "length": len(r)} for r in ranges]


def u16(data: bytes, offset: int) -> int:
    return struct.unpack_from("<H", data, offset)[0]


def u32(data: bytes, offset: int) -> int:
    return struct.unpack_from("<I", data, offset)[0]


def d88_report(data: bytes) -> dict:
    result = {
        "size": len(data),
        "sha256": sha256(data),
        "header_declared_size": None,
        "track_count": 0,
        "payload_size": 0,
        "structure_ok": False,
        "errors": [],
    }
    if len(data) < D88_HEADER_SIZE:
        result["errors"].append("file is shorter than the D88 header")
        return result
    result["header_declared_size"] = u32(data, 0x1C)
    pointers = [u32(data, 0x20 + i * 4) for i in range(164)]
    nonzero = [(i, p) for i, p in enumerate(pointers) if p]
    if [i for i, _ in nonzero] != list(range(80)):
        result["errors"].append("expected track pointers 0 through 79")
        return result
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
        result["errors"].append(str(exc))
        return result
    result["track_count"] = len(nonzero)
    result["payload_size"] = payload_size
    result["structure_ok"] = (
        len(data) == D88_SIZE
        and result["header_declared_size"] == len(data)
        and payload_size == D88_PAYLOAD_SIZE
    )
    if len(data) != D88_SIZE:
        result["errors"].append(f"expected file size {D88_SIZE}")
    if result["header_declared_size"] != len(data):
        result["errors"].append("D88 header size does not equal file size")
    if payload_size != D88_PAYLOAD_SIZE:
        result["errors"].append(f"expected payload size {D88_PAYLOAD_SIZE}")
    return result


@dataclass(frozen=True)
class Operation:
    stage: str
    source: str
    offset: int
    new: int
    old: int | None
    detail: str


class SourceArchive:
    def __init__(self, path: Path):
        self.path = path
        self.blob = path.read_bytes()
        self.zip = zipfile.ZipFile(io.BytesIO(self.blob))
        self.names = [n for n in self.zip.namelist() if not n.endswith("/")]

    def close(self) -> None:
        self.zip.close()

    def find_one(self, predicate, label: str) -> str:
        found = [n for n in self.names if predicate(n)]
        if len(found) != 1:
            raise ValueError(f"{label}: expected one source, found {len(found)}: {found[:5]}")
        return found[0]

    def read(self, name: str) -> bytes:
        return self.zip.read(name)

    def nested(self, outer_name: str) -> zipfile.ZipFile:
        return zipfile.ZipFile(io.BytesIO(self.read(outer_name)))


def parse_csv_blob(blob: bytes) -> list[dict[str, str]]:
    return list(csv.DictReader(io.StringIO(blob.decode("utf-8-sig"))))


def final_bundle_names(source: SourceArchive) -> list[str]:
    names = []
    for name in source.names:
        if not name.lower().endswith(".zip") or "patch_bundle" not in name.lower():
            continue
        if name.startswith("Block 1/4 ") or re.match(r"Block [2-6]/", name) or name.startswith("Ednding/"):
            names.append(name)
    expected = 7
    if len(names) != expected:
        raise ValueError(f"completed source archive: expected {expected} final bundles, found {len(names)}")
    return sorted(names)


def bundle_csv(source: SourceArchive, bundle_name: str, ending: bool = False) -> tuple[str, list[dict[str, str]]]:
    with source.nested(bundle_name) as bundle:
        candidates = [n for n in bundle.namelist() if n.lower().endswith(".csv")]
        if ending:
            candidates = [n for n in candidates if n.endswith("_changes.csv")]
        else:
            candidates = [n for n in candidates if "_changes_" in n]
        if len(candidates) != 1:
            raise ValueError(f"{bundle_name}: expected one final changes CSV, found {candidates}")
        member = candidates[0]
        return f"{bundle_name}::{member}", parse_csv_blob(bundle.read(member))


def collect_final_bundle_operations(source: SourceArchive) -> list[dict]:
    bundles = []
    for bundle in final_bundle_names(source):
        is_ending = bundle.startswith("Ednding/")
        label, rows = bundle_csv(source, bundle, ending=is_ending)
        operations = []
        for row in rows:
            if not row.get("disk_offset"):
                raise ValueError(f"{label}: row has no disk_offset")
            operations.append(Operation(
                "ending" if is_ending else "events",
                label,
                int(row["disk_offset"], 16),
                parse_hex_byte(row["raw_new"]),
                parse_hex_byte(row["raw_old"]),
                f"runtime={row.get('runtime_addr', row.get('SUB_addr', ''))} row={row.get('row', row.get('global_index', ''))}",
            ))
        bundles.append({
            "bundle": bundle,
            "member": label,
            "is_ending": is_ending,
            "operations": operations,
            "rows": len(rows),
        })
    return bundles


def collect_final_event_operations(source: SourceArchive) -> tuple[list[Operation], list[Operation], dict]:
    event_ops: list[Operation] = []
    ending_ops: list[Operation] = []
    sources = []
    for item in collect_final_bundle_operations(source):
        sources.append({"bundle": item["bundle"], "member": item["member"], "rows": item["rows"]})
        (ending_ops if item["is_ending"] else event_ops).extend(item["operations"])
    return event_ops, ending_ops, {
        "sources": sources,
        "event_rows": len(event_ops),
        "ending_rows": len(ending_ops),
        "operation_count": len(event_ops),
        "source_model": "final event bundles are independent baseline branches; selected stages form a composite union",
    }


def compare_final_bundles(source: SourceArchive, baseline: bytes, selected: set[str]) -> list[dict]:
    comparisons = []
    for item in collect_final_bundle_operations(source):
        stage = "ending" if item["is_ending"] else "events"
        if stage not in selected:
            continue
        candidate = bytearray(baseline)
        applied = apply_operations(candidate, item["operations"])
        with source.nested(item["bundle"]) as bundle:
            final_member = next(n for n in bundle.namelist() if n.lower().endswith(".d88"))
            reference = bundle.read(final_member)
        comparisons.append({
            "stage": stage,
            "bundle": item["bundle"],
            "source_member": item["member"],
            "operation_count": len(item["operations"]),
            "changed_bytes": applied["changed_bytes"],
            "reference_member": f"{item['bundle']}::{final_member}",
            "generated_sha256": sha256(candidate),
            "reference_sha256": sha256(reference),
            "match": bytes(candidate) == reference,
        })
    return comparisons


LOGO_TARGETS = (
    ("valis_logo", 0x2800, 0x4167, "build_user_edit/VALIS_LOGO_2800_4166_new_source.bin"),
    ("mugen_movement", 0x4167, 0x4405, "build_user_edit/MUGEN_MOVEMENT_4167_4404_new_source.bin"),
    ("mugen_final", 0x4405, 0x47E3, "build_user_edit/MUGEN_FINAL_4405_47E2_new_source.bin"),
)


def collect_logo_operations(source: SourceArchive) -> tuple[list[Operation], dict]:
    kit_name = source.find_one(lambda n: n.startswith("Logo/") and "original_user_editing_kit" in n and n.lower().endswith(".zip"), "logo editing kit")
    logo_ops: list[Operation] = []
    with source.nested(kit_name) as kit:
        map_name = "maps/ram_to_raw_reverse_map_2800_6159_verified.csv"
        rows = parse_csv_blob(kit.read(map_name))
        by_ram = {int(row["ram_addr"], 16): row for row in rows}
        target_reports = []
        for target, start, end, member in LOGO_TARGETS:
            stream = kit.read(member)
            if len(stream) != end - start:
                raise ValueError(f"{kit_name}:{member}: expected {end-start} bytes, got {len(stream)}")
            changed = 0
            for ram in range(start, end):
                row = by_ram[ram]
                raw_offset = int(row["raw_file_offset"], 16)
                raw_index = int(row["raw_index"], 16)
                d88_c = int(row["d88_c"], 16)
                de = 0x400 - raw_index
                correction = 0x40 - d88_c
                new_raw = (stream[ram - start] + (de >> 8) + (de & 0xFF) - correction) & 0xFF
                old_raw = parse_hex_byte(row["current_raw_byte"])
                if new_raw != old_raw:
                    changed += 1
                    logo_ops.append(Operation("logo", f"{kit_name}::{member}", raw_offset, new_raw, old_raw, f"ram=0x{ram:04X}"))
            target_reports.append({"name": target, "ram_range": f"0x{start:04X}-0x{end-1:04X}", "source_member": member, "stream_bytes": len(stream), "changed_raw_bytes": changed})
    return logo_ops, {"kit": kit_name, "targets": target_reports, "operation_count": len(logo_ops)}


def docx_tables(blob: bytes) -> list[list[list[str]]]:
    with zipfile.ZipFile(io.BytesIO(blob)) as document:
        xml = document.read("word/document.xml")
    root = ET.fromstring(xml)
    tables: list[list[list[str]]] = []
    for table in root.findall(f".//{{{W_NS}}}tbl"):
        rows = []
        for tr in table.findall(f"./{{{W_NS}}}tr"):
            cells = []
            for tc in tr.findall(f"./{{{W_NS}}}tc"):
                text = "".join(node.text or "" for node in tc.iter(W_T))
                cells.append(" ".join(text.split()))
            if cells:
                rows.append(cells)
        tables.append(rows)
    return tables


def token_pair_bytes(text: str) -> bytes:
    pairs = re.findall(r"(?<![0-9A-Fa-f])([0-9A-Fa-f]{4})(?![0-9A-Fa-f])", text)
    if not pairs:
        raise ValueError(f"token pair cell is empty: {text[:120]}")
    return b"".join(bytes((int(pair[:2], 16), int(pair[2:], 16))) for pair in pairs)


def parse_range(value: str) -> tuple[int, int]:
    values = [int(x, 16) for x in re.findall(r"0x([0-9A-Fa-f]+)", value)]
    if len(values) != 2:
        raise ValueError(f"address range is not two-ended: {value}")
    return values[0], values[1]


def sub_to_d88(sub_addr: int, decoded: int) -> tuple[int, int]:
    groups = (
        (0x4400, 0x4800, 0x7A10, 0x47FF),
        (0x4800, 0x4C00, 0x7E20, 0x4BFF),
        (0x4C00, 0x5000, 0x8230, 0x4FFF),
        (0x5000, 0x5400, 0x8640, 0x53FF),
    )
    for start, end, raw_base, reverse_end in groups:
        if start <= sub_addr < end:
            raw_offset = raw_base + (reverse_end - sub_addr)
            de = sub_addr - start + 1
            encoded = (decoded + (de >> 8) + (de & 0xFF) - 0x3A) & 0xFF
            return raw_offset, encoded
    raise ValueError(f"gameover SUB address outside mapped Disk A ranges: 0x{sub_addr:04X}")


def collect_gameover_operations(source: SourceArchive) -> tuple[list[Operation], dict]:
    doc_name = source.find_one(lambda n: n.startswith("Gameover/") and "original_SCROLL1-35" in n and n.lower().endswith(".docx"), "gameover token source")
    tables = docx_tables(source.read(doc_name))
    fixed_table = next((t for t in tables if t and t[0][:2] == ["Seg", "MAIN 본문"]), None)
    scroll_table = next((t for t in tables if t and t[0][:2] == ["Block", "MAIN 전체"]), None)
    if fixed_table is None or scroll_table is None:
        raise ValueError(f"{doc_name}: fixed/scroll token tables not found")
    ops: list[Operation] = []
    fixed_segments = 0
    scroll_blocks = 0
    for row in fixed_table[1:]:
        if len(row) < 9 or not row[0].isdigit():
            continue
        main_start, main_end = parse_range(row[1])
        sub_start, sub_end = parse_range(row[2])
        body = token_pair_bytes(row[8])
        if len(body) != main_end - main_start + 1 or sub_start + len(body) - 1 != sub_end:
            raise ValueError(f"{doc_name}: fixed segment {row[0]} token length/range mismatch")
        for i, decoded in enumerate(body):
            offset, new = sub_to_d88(sub_start + i, decoded)
            ops.append(Operation("gameover", doc_name, offset, new, None, f"fixed_segment={row[0]} sub=0x{sub_start+i:04X}"))
        marker_offset, marker_new = sub_to_d88(sub_end + 1, 0x0F)
        ops.append(Operation("gameover", doc_name, marker_offset, marker_new, None, f"fixed_segment={row[0]} marker"))
        fixed_segments += 1
    for row in scroll_table[1:]:
        if len(row) < 9 or not row[0].isdigit():
            continue
        marker = row[4].strip().upper() == "0F"
        main_start, main_end = parse_range(row[5])
        full_sub_start, full_sub_end = parse_range(row[2])
        sub_start = full_sub_start + (1 if marker else 0)
        sub_end = full_sub_end
        body = token_pair_bytes(row[8])
        if len(body) != main_end - main_start + 1 or sub_start + len(body) - 1 != sub_end:
            raise ValueError(f"{doc_name}: scroll block {row[0]} token length/range mismatch")
        if marker:
            marker_offset, marker_new = sub_to_d88(sub_start - 1, 0x0F)
            ops.append(Operation("gameover", doc_name, marker_offset, marker_new, None, f"scroll_block={row[0]} marker"))
        for i, decoded in enumerate(body):
            offset, new = sub_to_d88(sub_start + i, decoded)
            ops.append(Operation("gameover", doc_name, offset, new, None, f"scroll_block={row[0]} sub=0x{sub_start+i:04X}"))
        scroll_blocks += 1
    return ops, {"source": doc_name, "fixed_segments": fixed_segments, "scroll_blocks": scroll_blocks, "operation_count": len(ops), "encoding": "SUB->D88 reverse 0x3A correction"}


def collect_error_operations(source: SourceArchive) -> tuple[list[Operation], dict]:
    doc_name = source.find_one(lambda n: "ERROR_MESSAGE" in n and n.lower().endswith(".docx"), "error-message source")
    tables = docx_tables(source.read(doc_name))
    table = next((t for t in tables if t and t[0][:3] == ["순번", "세그", "종류"]), None)
    dynamic = next((t for t in tables if t and t[0][:2] == ["용도", "원본/실행 명령 주소"]), None)
    if table is None or dynamic is None:
        raise ValueError(f"{doc_name}: error byte tables not found")
    ops: list[Operation] = []
    warnings: list[str] = []
    for row in table[1:]:
        if len(row) < 9 or not row[0].isdigit():
            continue
        d88_cell = row[5]
        d88_values = [int(value, 16) for value in re.findall(r"0x([0-9A-Fa-f]+)", d88_cell)]
        if not d88_values:
            continue
        if "미사용" in row[2]:
            values = [0] * len(re.findall(r"(?<![0-9A-Fa-f])([0-9A-Fa-f]{2})(?![0-9A-Fa-f])", row[8]))
        else:
            values = [int(value, 16) for value in re.findall(r"(?<![0-9A-Fa-f])([0-9A-Fa-f]{2})(?![0-9A-Fa-f])", row[8])]
        if len(d88_values) == 2 and "→" in d88_cell:
            start, end = d88_values
            step = -1 if end < start else 1
            expanded = list(range(start, end + step, step))
            if len(expanded) != len(values):
                if "미사용" in row[2] and values:
                    # The completion table says 0x3178→0x316B but lists 11
                    # bytes.  Preserve the explicit end and byte count; this
                    # yields 0x3175..0x316B and records the source conflict.
                    expanded = [end - i if end < start else end + i for i in range(len(values))]
                    warnings.append(
                        f"row {row[0]} D88 range {d88_cell} spans {len(list(range(start, end + step, step)))} addresses "
                        f"but lists {len(values)} values; used explicit end plus value count"
                    )
                else:
                    raise ValueError(f"{doc_name}: error row {row[0]} offset/value count mismatch")
            offsets = expanded
        else:
            offsets = d88_values
        if len(values) != len(offsets):
            raise ValueError(f"{doc_name}: error row {row[0]} offset/value count mismatch")
        for offset, new in zip(offsets, values):
            ops.append(Operation("error", doc_name, offset, new, None, f"row={row[0]}"))
    for row in dynamic[1:]:
        if len(row) < 7:
            continue
        offsets = re.findall(r"0x([0-9A-Fa-f]+)", row[5])
        values = re.findall(r"[0-9A-Fa-f]{2}→([0-9A-Fa-f]{2})", row[6])
        if len(offsets) != 1 or len(values) != 1:
            continue
        ops.append(Operation("error", doc_name, int(offsets[0], 16), int(values[0], 16), None, f"dynamic={row[0]}"))
    return ops, {
        "source": doc_name,
        "operation_count": len(ops),
        "unique_offsets": len({op.offset for op in ops}),
        "document_claim": "73 D88 bytes",
        "warnings": warnings,
        "source_columns": {"d88_offsets": 5, "d88_values": 8},
    }


def visualtxt_glyph(text: str) -> bytes:
    rows = [line.strip() for line in text.splitlines() if line.strip() and not line.lstrip().startswith(";")]
    if len(rows) != 16 or any(len(row) != 16 or set(row) - {"■", "□"} for row in rows):
        raise ValueError("VISUALTXT glyph must contain exactly sixteen 16-pixel binary rows")
    encoded = []
    for row in rows:
        encoded.append(sum(0x80 >> x for x, char in enumerate(row[:8]) if char == "■"))
        encoded.append(sum(0x80 >> x for x, char in enumerate(row[8:]) if char == "■"))
    return bytes(encoded)


def collect_kanji_operations(source: SourceArchive) -> tuple[list[Operation], dict]:
    kit_name = source.find_one(lambda n: n.startswith("Kanjirom/") and "EDITKIT" in n and n.lower().endswith(".zip"), "KANJI edit kit")
    ops: list[Operation] = []
    glyph_names: list[str] = []
    with source.nested(kit_name) as kit:
        for name in sorted(kit.namelist()):
            if not name.startswith("glyphs_edit_16x16_txt_visual/") or not name.endswith(".txt"):
                continue
            match = re.search(r"_slot(\d+)_tok[0-9A-Fa-f]+_off([0-9A-Fa-f]+)\.txt$", name)
            if not match:
                raise ValueError(f"KANJI glyph filename has no slot/offset metadata: {name}")
            offset = int(match.group(2), 16)
            glyph = visualtxt_glyph(kit.read(name).decode("utf-8-sig"))
            if offset % GLYPH_SIZE or offset + GLYPH_SIZE > KANJI_SIZE:
                raise ValueError(f"KANJI glyph offset is not a 32-byte slot: 0x{offset:05X}")
            glyph_names.append(name)
            for i, value in enumerate(glyph):
                ops.append(Operation("kanji", f"{kit_name}::{name}", offset + i, value, None, f"slot={match.group(1)}"))
    if len(glyph_names) != 476 or len({op.offset // GLYPH_SIZE for op in ops}) != 476:
        raise ValueError(f"KANJI source must contain 476 unique glyph slots, found {len(glyph_names)}")
    return ops, {"kit": kit_name, "glyph_files": len(glyph_names), "glyph_slots": 476, "operation_count": len(ops), "source_format": "VISUALTXT 16x16 1bpp"}


def apply_operations(data: bytearray, operations: list[Operation]) -> dict:
    seen: dict[int, Operation] = {}
    changed: list[int] = []
    inferred_old = 0
    for op in operations:
        if not 0 <= op.offset < len(data):
            raise ValueError(f"{op.stage}: offset outside output: 0x{op.offset:06X}")
        if op.offset in seen and seen[op.offset].new != op.new:
            previous = seen[op.offset]
            raise ValueError(f"conflicting source bytes at 0x{op.offset:06X}: {previous.source} vs {op.source}")
        current = data[op.offset]
        if op.old is not None and current != op.old:
            raise ValueError(f"{op.stage}: source old-byte mismatch at 0x{op.offset:06X}: input={current:02X}, source={op.old:02X}, {op.source}")
        if op.old is None:
            inferred_old += 1
        if current != op.new:
            data[op.offset] = op.new
            changed.append(op.offset)
        seen[op.offset] = op
    return {"source_operations": len(operations), "changed_bytes": len(set(changed)), "inferred_old_bytes": inferred_old, "changed_ranges": compact_ranges(changed)}


def inspect_source_archive(source: SourceArchive) -> dict:
    events, ending, event_meta = collect_final_event_operations(source)
    logo, logo_meta = collect_logo_operations(source)
    gameover, gameover_meta = collect_gameover_operations(source)
    error, error_meta = collect_error_operations(source)
    kanji, kanji_meta = collect_kanji_operations(source)
    return {
        "archive": {"name": source.path.name, "size": len(source.blob), "sha256": sha256(source.blob)},
        "source_groups": {
            "events": {**event_meta, "operation_count": len(events)},
            "ending": {"operation_count": len(ending)},
            "logo": logo_meta,
            "gameover": gameover_meta,
            "error": error_meta,
            "kanji": kanji_meta,
        },
    }


def build(args: argparse.Namespace) -> dict:
    stage_names = [s.strip() for s in args.stages.split(",") if s.strip()]
    valid = {"events", "ending", "logo", "gameover", "error", "kanji"}
    unknown = set(stage_names) - valid
    if unknown:
        raise ValueError(f"unknown build stages: {sorted(unknown)}")
    source = SourceArchive(args.source_archive)
    try:
        disk = bytearray(args.original_disk.read_bytes())
        kanji = bytearray(args.original_kanji.read_bytes())
        base_disk_report = d88_report(bytes(disk))
        if not base_disk_report["structure_ok"]:
            raise ValueError("original Disk A does not pass the mixed-sector D88 structure check")
        if len(kanji) != KANJI_SIZE:
            raise ValueError(f"original KANJI1 ROM must be {KANJI_SIZE} bytes, got {len(kanji)}")

        event_ops, ending_ops, event_meta = collect_final_event_operations(source)
        logo_ops, logo_meta = collect_logo_operations(source)
        gameover_ops, gameover_meta = collect_gameover_operations(source)
        error_ops, error_meta = collect_error_operations(source)
        kanji_ops, kanji_meta = collect_kanji_operations(source)
        operation_groups = {
            "events": event_ops,
            "ending": ending_ops,
            "logo": logo_ops,
            "gameover": gameover_ops,
            "error": error_ops,
        }
        stage_reports = []
        for stage in stage_names:
            if stage == "kanji":
                result = apply_operations(kanji, kanji_ops)
                result.update({"stage": stage, "sha256": sha256(kanji), "size": len(kanji), "source": kanji_meta})
            else:
                result = apply_operations(disk, operation_groups[stage])
                result.update({"stage": stage, "sha256": sha256(disk), "size": len(disk)})
                if stage == "events":
                    result["source"] = event_meta
                elif stage == "ending":
                    result["source"] = {"operation_count": len(ending_ops)}
                elif stage == "logo":
                    result["source"] = logo_meta
                elif stage == "gameover":
                    result["source"] = gameover_meta
                elif stage == "error":
                    result["source"] = error_meta
                if stage != "kanji":
                    result["d88_structure"] = d88_report(bytes(disk))
            stage_reports.append(result)
        if not stage_names:
            raise ValueError("at least one build stage is required")

        disk_out = args.output_dir / "Valis_Disk_A_reproduced_from_sources.d88"
        kanji_out = args.output_dir / "KANJI1_reproduced_from_visualtxt.ROM"
        report = {
            "build": "PC-8801 Valis 1 source reproduction",
            "generation_rule": "original D88/KANJI1 + explicit completed-source CSV/DOCX/source-stream/VISUALTXT inputs; no patch-image application",
            "source_archive": {"path": str(args.source_archive), "size": len(source.blob), "sha256": sha256(source.blob)},
            "inputs": {
                "disk": {"path": str(args.original_disk), "size": len(disk), "sha256": sha256(args.original_disk.read_bytes()), "d88": base_disk_report},
                "kanji": {"path": str(args.original_kanji), "size": len(kanji), "sha256": sha256(args.original_kanji.read_bytes())},
            },
            "stages": stage_reports,
            "outputs": {
                "disk": {"path": str(disk_out), "size": len(disk), "sha256": sha256(disk)},
                "kanji": {"path": str(kanji_out), "size": len(kanji), "sha256": sha256(kanji)},
            },
            "reference_comparisons": [],
            "source_groups": {"logo": logo_meta, "gameover": gameover_meta, "error": error_meta, "kanji": kanji_meta},
        }
        if ("events" in stage_names or "ending" in stage_names) and sha256(args.original_disk.read_bytes()) == KNOWN_COMPLETION_BASE_SHA256:
            report["reference_comparisons"] = compare_final_bundles(source, args.original_disk.read_bytes(), set(stage_names))
            report["reference_scope"] = (
                "Each selected final bundle is rebuilt independently from the canonical baseline and compared "
                "with its own D88. The sequential stage output is an explicit composite union, not a claim that "
                "all independent event branches share one canonical final D88."
            )
        if stage_names == ["logo"] and sha256(args.original_disk.read_bytes()) == KNOWN_COMPLETION_BASE_SHA256:
            report["reference_comparisons"].append({"reference_sha256": KNOWN_LOGO_ONLY_SHA256, "match": sha256(disk) == KNOWN_LOGO_ONLY_SHA256, "reference": "Logo kit build_user_edit/report.json"})
        args.output_dir.mkdir(parents=True, exist_ok=True)
        disk_out.write_bytes(disk)
        kanji_out.write_bytes(kanji)
        (args.output_dir / "build-report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return report
    finally:
        source.close()


def cmd_build(args: argparse.Namespace) -> int:
    report = build(args)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


def cmd_inspect_source(args: argparse.Namespace) -> int:
    source = SourceArchive(args.source_archive)
    try:
        report = inspect_source_archive(source)
    finally:
        source.close()
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


def cmd_inspect_d88(args: argparse.Namespace) -> int:
    report = d88_report(args.image.read_bytes())
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["structure_ok"] else 2


def parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="command", required=True)
    build_parser = sub.add_parser("build", help="generate D88 and KANJI1 from source material")
    build_parser.add_argument("--original-disk", required=True, type=Path)
    build_parser.add_argument("--original-kanji", required=True, type=Path)
    build_parser.add_argument("--source-archive", required=True, type=Path)
    build_parser.add_argument("--output-dir", required=True, type=Path)
    build_parser.add_argument("--stages", default="events,ending,logo,gameover,error,kanji", help="comma-separated stages: events,ending,logo,gameover,error,kanji")
    build_parser.set_defaults(func=cmd_build)
    inspect = sub.add_parser("inspect-source", help="count and validate explicit source groups")
    inspect.add_argument("--source-archive", required=True, type=Path)
    inspect.add_argument("--output", type=Path)
    inspect.set_defaults(func=cmd_inspect_source)
    d88 = sub.add_parser("inspect-d88", help="validate a D88 structure")
    d88.add_argument("image", type=Path)
    d88.set_defaults(func=cmd_inspect_d88)
    return ap


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        return args.func(args)
    except (OSError, ValueError, zipfile.BadZipFile, ET.ParseError, struct.error) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
