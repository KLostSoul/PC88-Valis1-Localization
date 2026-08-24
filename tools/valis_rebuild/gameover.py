"""Gameover fixed/scroll source serializer.

The source JSONL is a literal transcription of the completion archive's
original/translation/token-pair tables.  The four SUB-to-D88 block bases and
the 0x3A correction are explicit facts from the analysis document; there is
no global address search or token inference here.
"""

from __future__ import annotations

import json
from pathlib import Path

from .codec import encode_byte
from .d88 import D88Image
from .errors import BuildError


SUB_TO_D88_BASE = {
    0x4400: 0x7A10,
    0x4800: 0x7E20,
    0x4C00: 0x8230,
    0x5000: 0x8640,
}
CORRECTION = 0x3A


def _range(text: str) -> tuple[int, int]:
    try:
        left, right = text.split("~", 1)
        return int(left, 16), int(right, 16)
    except ValueError as exc:
        raise BuildError(f"invalid gameover range: {text!r}") from exc


def _ranges(text: str) -> list[tuple[int, int]]:
    return [_range(part.strip()) for part in text.split(",")]


def _records(path: Path) -> list[dict]:
    records = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise BuildError(f"invalid gameover JSONL at {path}:{line_number}") from exc
    if not records:
        raise BuildError(f"empty gameover source: {path}")
    return records


def _expected_raw_offsets(sub_start: int, length: int) -> list[int]:
    offsets = []
    for i in range(length):
        address = sub_start + i
        block = address & ~0x3FF
        if block not in SUB_TO_D88_BASE:
            raise BuildError(f"no explicit gameover D88 base for SUB 0x{block:04X}")
        offsets.append(SUB_TO_D88_BASE[block] + 0x3FF - (address - block))
    return offsets


def _declared_raw_offsets(text: str) -> set[int]:
    result: set[int] = set()
    for start, end in _ranges(text):
        if end < start:
            raise BuildError(f"descending gameover D88 range is not accepted: {text}")
        result.update(range(start, end + 1))
    return result


def _apply_records(image: D88Image, records: list[dict], component: str) -> dict:
    writes = 0
    changed = 0
    marker_relocations = 0
    for record in records:
        pairs = record["token_pairs"]
        decoded = bytes.fromhex("".join(pairs))
        sub_range_start, sub_range_end = _range(record["sub_range"])
        if "body_range" in record:
            main_body_start, main_body_end = _range(record["body_range"])
            sub_start = main_body_start + 0x3F00
            sub_end = main_body_end + 0x3F00
        else:
            sub_start, sub_end = sub_range_start, sub_range_end
        if len(decoded) != sub_end - sub_start + 1:
            raise BuildError(f"{component} {record.get('number')} token length/sub range mismatch")
        expected_offsets = _expected_raw_offsets(sub_start, len(decoded))
        declared_offsets = _declared_raw_offsets(record["d88_range"])
        all_expected_offsets = set(expected_offsets)
        if "body_range" in record and record.get("marker") == "0F":
            marker_offset = _expected_raw_offsets(sub_range_start, 1)[0]
            all_expected_offsets.add(marker_offset)
        if all_expected_offsets != declared_offsets:
            raise BuildError(
                f"{component} {record.get('number')} D88 span does not match explicit SUB map"
            )
        for index, value in enumerate(decoded):
            offset = expected_offsets[index]
            image.find_data_sector(offset)
            address = sub_start + index
            local = address - (address & ~0x3FF)
            raw_new = encode_byte(value, local, CORRECTION)
            actual = image.data[offset]
            image.data[offset] = raw_new
            writes += 1
            changed += int(actual != raw_new)
        if "body_range" in record and record.get("marker") == "0F":
            marker_offset = _expected_raw_offsets(sub_range_start, 1)[0]
            marker_raw = encode_byte(0x0F, sub_range_start - (sub_range_start & ~0x3FF), CORRECTION)
            marker_old = image.data[marker_offset]
            image.data[marker_offset] = marker_raw
            writes += 1
            changed += int(marker_old != marker_raw)
            marker_relocations += int(marker_old != marker_raw)
    return {"component": component, "records": len(records), "writes": writes,
            "changed": changed, "marker_relocations": marker_relocations}


def apply_gameover(image: D88Image, source_root: str | Path) -> list[dict]:
    root = Path(source_root)
    fixed = _records(root / "text" / "gameover-fixed.jsonl")
    scroll = _records(root / "text" / "gameover-scroll.jsonl")
    if [r["number"] for r in fixed] != list(range(1, 16)):
        raise BuildError("gameover fixed source must contain segments 1..15")
    if [r["number"] for r in scroll] != list(range(1, 36)):
        raise BuildError("gameover scroll source must contain blocks 1..35")
    return [
        _apply_records(image, fixed, "gameover_fixed_1_15"),
        _apply_records(image, scroll, "gameover_scroll_1_35"),
    ]
