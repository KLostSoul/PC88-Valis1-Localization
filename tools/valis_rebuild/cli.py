"""Safe staged CLI for the manually reviewed reproduction build."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from .d88 import D88Image
from .errors import BuildError
from .pipeline import build_disk, build_kanji
from .source_gate import lint_all, require_buildable
from .text_sources import lint_text_sources


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _reject_reference(path: Path) -> None:
    lowered = str(path).lower()
    if path.suffix.lower() in {".zip", ".ips", ".patch"}:
        raise BuildError(f"reference archive/patch is not a build input: {path}")
    forbidden = ("reference_work", "nested_extract", "completed", "final", "quarantine")
    if any(part in lowered for part in forbidden):
        raise BuildError(f"reference or quarantined material is not a build input: {path}")


def command_source_lint(args: argparse.Namespace) -> dict:
    return {"command": "source-lint", **lint_all(repo_root())}


def command_text_lint(args: argparse.Namespace) -> dict:
    return {"command": "text-lint", **lint_text_sources(repo_root())}


def command_export_original(args: argparse.Namespace) -> dict:
    source = Path(args.d88).resolve()
    _reject_reference(source)
    image = D88Image.read(source)
    output = Path(args.out).resolve()
    image.export(output)
    result = {
        "command": "export-original",
        "source_sha256": image.sha256(),
        "source_size": len(image.data),
        "sector_count": len(image.sectors),
        "flat_payload_size": len(image.flatten_payload()),
        "output": str(output),
        "source_rows_created": 0,
        "status": "OK",
    }
    _write_json(output / "export-report.json", result)
    return result


def command_build_d88(args: argparse.Namespace) -> dict:
    root = repo_root()
    source = Path(args.d88).resolve()
    _reject_reference(source)
    return {"command": "build-d88", **build_disk(root, source, Path(args.out).resolve())}


def command_build_rom(args: argparse.Namespace) -> dict:
    root = repo_root()
    source = Path(args.rom).resolve()
    _reject_reference(source)
    return {"command": "build-rom", **build_kanji(root, source, Path(args.out).resolve())}


def command_build(args: argparse.Namespace) -> dict:
    root = repo_root()
    d88_source = Path(args.d88).resolve()
    rom_source = Path(args.rom).resolve()
    _reject_reference(d88_source)
    _reject_reference(rom_source)
    output = Path(args.out).resolve()
    # Separate component directories keep the two component logs independent.
    disk = build_disk(root, d88_source, output / "d88")
    kanji = build_kanji(root, rom_source, output / "kanji")
    result = {
        "command": "build",
        "d88": disk,
        "kanji1": kanji,
        "output": str(output),
        "status": "OK",
    }
    _write_json(output / "build-log.json", result)
    return result


def command_verify(args: argparse.Namespace) -> dict:
    source = Path(args.d88).resolve()
    image = D88Image.read(source)
    result = {"command": "verify", "path": str(source), "sha256": image.sha256(),
              "size": len(image.data), "sector_count": len(image.sectors),
              "flat_payload_size": len(image.flatten_payload()), "status": "OK"}
    if args.rom:
        rom = Path(args.rom).resolve()
        _reject_reference(rom)
        rom_data = rom.read_bytes()
        if len(rom_data) != 0x20000:
            raise BuildError(f"KANJI1 must be exactly 0x20000 bytes, got {len(rom_data):#x}")
        result["kanji1"] = {
            "path": str(rom),
            "sha256": _sha256(rom),
            "size": len(rom_data),
        }
    if args.report:
        _write_json(Path(args.report).resolve(), result)
    return result


def command_compare(args: argparse.Namespace) -> dict:
    built = Path(args.built).resolve()
    reference = Path(args.reference).resolve()
    if reference.suffix.lower() != ".d88":
        raise BuildError("comparison reference must be a local D88")
    built_image = D88Image.read(built)
    reference_image = D88Image.read(reference)
    if len(built_image.data) != len(reference_image.data):
        raise BuildError("built/reference D88 sizes differ")
    changed = sum(a != b for a, b in zip(built_image.data, reference_image.data))
    result = {"command": "compare", "reference_role": "comparison_only",
              "built_sha256": built_image.sha256(), "reference_sha256": reference_image.sha256(),
              "different_file_bytes": changed, "status": "OK"}
    if args.fail_on_diff and changed:
        raise BuildError(f"reference comparison failed: {changed} differing bytes")
    if args.report:
        _write_json(Path(args.report).resolve(), result)
    return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="valis-rebuild")
    sub = parser.add_subparsers(dest="command", required=True)
    lint = sub.add_parser("source-lint")
    lint.set_defaults(handler=command_source_lint)
    text_lint = sub.add_parser("text-lint")
    text_lint.set_defaults(handler=command_text_lint)
    export = sub.add_parser("export-original")
    export.add_argument("--d88", required=True)
    export.add_argument("--out", default="build/export-original")
    export.set_defaults(handler=command_export_original)
    build_d88 = sub.add_parser("build-d88")
    build_d88.add_argument("--d88", required=True)
    build_d88.add_argument("--out", default="build/reproduction/d88")
    build_d88.set_defaults(handler=command_build_d88)
    build_rom = sub.add_parser("build-rom")
    build_rom.add_argument("--rom", required=True)
    build_rom.add_argument("--out", default="build/reproduction/kanji")
    build_rom.set_defaults(handler=command_build_rom)
    build = sub.add_parser("build")
    build.add_argument("--d88", required=True)
    build.add_argument("--rom", required=True)
    build.add_argument("--out", default="build/reproduction")
    build.set_defaults(handler=command_build)
    verify = sub.add_parser("verify")
    verify.add_argument("--d88", required=True)
    verify.add_argument("--rom")
    verify.add_argument("--report")
    verify.set_defaults(handler=command_verify)
    compare = sub.add_parser("compare")
    compare.add_argument("--built", required=True)
    compare.add_argument("--reference", required=True)
    compare.add_argument("--report")
    compare.add_argument("--fail-on-diff", action="store_true")
    compare.set_defaults(handler=command_compare)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        result = args.handler(args)
    except (BuildError, OSError, ValueError) as exc:
        parser.error(str(exc))
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
