# PC-88 Mugen Senshi Valis 1 — reproduction build design

This repository contains a source-first, manually reviewed reproduction build. The original D88 and KANJI1 ROM are supplied at build time; copyrighted completed binaries and patches are comparison-only inputs and are not stored here.

The target is a mirror-style reproduction repository:

```text
manual evidence ledger
        ↓ independent review
accepted literal source tables
        ↓ strict byte serializer
local D88/ROM output
        ↓ verify and optional comparison
local reference only
```

## Non-negotiable boundary

The completed ZIP, completed D88/ROM, IPS files, extracted BMP/PNG assets, and any other reference result are not build inputs and are not stored in GitHub. They may be consulted locally for comparison only.

Automatic document extraction, token mapping, address guessing, correction inference, and promotion of generated tables are forbidden. Tools may validate an explicitly authored row or serialize an already accepted row; they may not create accepted project data.

## Repository domains

- `analysis/evidence-ledger.json`: manually recorded observations with document locations, literal bytes, address layer, and review state.
- `analysis/reproduction-status.json`: source-table counts, local comparison hashes, and explicit unresolved version conflicts.
- `source/accepted/`: reviewed literal source data, including original-text/Korean-translation tables, token streams, raw byte tables, ASM observations, and 476 explicit KANJI glyph sources.
- `tools/valis_rebuild/`: D88 parser, low-level codec, strict source gate, literal byte serializer, and staged CLI.
- `tests/`: tests for gates, low-level invariants, source tables, and the integrated build.
- `analysis/quarantine/`: previous automatic-extraction attempt, ignored and excluded from the build graph.

## Commands

```sh
PYTHONPATH=. python -m tools.valis_rebuild source-lint
PYTHONPATH=. python -m tools.valis_rebuild text-lint
PYTHONPATH=. python -m tools.valis_rebuild export-original \
  --d88 /path/to/user-supplied/original.d88 --out build/export-original
PYTHONPATH=. python -m tools.valis_rebuild build-d88 \
  --d88 /path/to/user-supplied/original.d88
PYTHONPATH=. python -m tools.valis_rebuild build-rom \
  --rom /path/to/user-supplied/KANJI1.ROM
PYTHONPATH=. python -m tools.valis_rebuild build \
  --d88 /path/to/user-supplied/original.d88 \
  --rom /path/to/user-supplied/KANJI1.ROM
PYTHONPATH=. python -m tools.valis_rebuild verify \
  --d88 build/reproduction/d88/valis_disk_a.d88 \
  --rom build/reproduction/kanji/KANJI1.ROM
PYTHONPATH=. python -m tools.valis_rebuild compare \
  --built build/reproduction/result.d88 \
  --reference /local/only/reference.d88
# release comparison: fail unless byte-for-byte equal
PYTHONPATH=. python -m tools.valis_rebuild compare \
  --built build/reproduction/result.d88 \
  --reference /local/only/reference.d88 \
  --fail-on-diff
```

`source-lint` reports the review state and verifies every accepted path exists. `build-d88` and `build-rom` independently verify the original-byte guards; `build` runs both components and writes separate logs. `export-original` is read-only structural inspection of the user-supplied original image; it creates no translation source rows.

## Component acceptance order

1. Original D88/ROM geometry and hashes.
2. Main event blocks 1–6, including literal control-token boundaries and physical sector data ranges.
3. Game-over fixed segments 1–15 and scroll blocks 1–35, including marker handling.
4. Ending segments 1–24, terminators, lengths, correction arithmetic, and physical mapping.
5. Control-token registry and character/token table.
6. KANJI1 slot/ROM assignments and separately supplied glyph sources.
7. Debugger-derived entrypoints, branch targets, free-space observations, and literal byte changes.
8. D88/ROM serializer, round-trip verification, reproducibility logs, and integration tests.

No component may be silently accepted because a completed reference image happens to match it.
