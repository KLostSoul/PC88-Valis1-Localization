"""End-to-end source-driven reproduction pipeline."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from .d88 import D88Image
from .gameover import apply_gameover
from .kanji import build_rom, load_assignments
from .serializer import apply_hold_patch, apply_raw_tables
from .source_gate import require_buildable


def source_tree_hash(root: Path) -> str:
    digest = hashlib.sha256()
    source_root = root / "source" / "accepted"
    for path in sorted(p for p in source_root.rglob("*") if p.is_file()):
        digest.update(str(path.relative_to(root)).encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
    return digest.hexdigest()


def _write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _disk_tables(root: Path) -> list[tuple[str, Path]]:
    tables = [(f"event_block_{n}", root / f"source/accepted/tables/events/block-{n}-raw-changes.csv") for n in range(1, 7)]
    tables += [
        ("ending_1_24", root / "source/accepted/tables/ending/raw-changes.csv"),
        ("error07", root / "source/accepted/tables/error07/raw-changes.csv"),
        ("logo", root / "source/accepted/tables/logo/raw-changes.csv"),
    ]
    return tables


def build_disk(root: Path, input_path: Path, output_dir: Path) -> dict:
    require_buildable(root)
    image = D88Image.read(input_path)
    component_reports = []
    component_reports.extend(apply_gameover(image, root / "source/accepted"))
    component_reports.extend(apply_raw_tables(image, _disk_tables(root)))
    component_reports.append(apply_hold_patch(image, root / "source/accepted/tables/gameover/hold-34-35.json"))
    output_dir.mkdir(parents=True, exist_ok=True)
    output = output_dir / "valis_disk_a.d88"
    image.save(output)
    log = {
        "schema": "valis-reproduction-log/v1",
        "kind": "d88",
        "input": {"path": str(input_path), "sha256": hashlib.sha256(input_path.read_bytes()).hexdigest()},
        "source_tree_sha256": source_tree_hash(root),
        "component_reports": component_reports,
        "output": {"path": str(output), "sha256": image.sha256(), "size": len(image.data)},
        "structure": {"sectors": len(image.sectors), "flat_payload": len(image.flatten_payload())},
        "status": "OK",
    }
    _write_json(output_dir / "repro-log.json", log)
    return log


def build_kanji(root: Path, input_path: Path, output_dir: Path) -> dict:
    require_buildable(root)
    original = input_path.read_bytes()
    assignments = load_assignments(
        root / "source/accepted/tables/kanji/assignments.csv",
        root / "source/accepted/kanji",
    )
    output_bytes, glyph_report = build_rom(original, assignments)
    output_dir.mkdir(parents=True, exist_ok=True)
    output = output_dir / "KANJI1.ROM"
    output.write_bytes(output_bytes)
    log = {
        "schema": "valis-reproduction-log/v1",
        "kind": "kanji1",
        "input": {"path": str(input_path), "sha256": hashlib.sha256(original).hexdigest()},
        "source_tree_sha256": source_tree_hash(root),
        "assignments": len(assignments),
        "changed_slots": sum(item["changed"] for item in glyph_report),
        "output": {"path": str(output), "sha256": hashlib.sha256(output_bytes).hexdigest(), "size": len(output_bytes)},
        "status": "OK",
    }
    _write_json(output_dir / "repro-log.json", log)
    _write_json(output_dir / "glyph-report.json", {"schema": "valis-kanji-build-report/v1", "glyphs": glyph_report})
    return log
