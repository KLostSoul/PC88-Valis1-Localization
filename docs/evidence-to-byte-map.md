# Evidence → direct byte → verification map

This index lets a reviewer trace every accepted class of modification without placing copyrighted completed media in the repository. The completion archive is consulted locally; the repository stores only literal reviewed source, provenance paths/table-row references, and hashes.

| Evidence ID | Completion analysis material | Physical target | Applied by | Verification |
|---|---|---|---|---|
| D88-ORIGINAL-GEOMETRY | `reproduce-valis1-pc88-ko/references/verified-artifacts.md` | D88 container, 422 sectors / 407,552 payload bytes | `D88Image.read` | input SHA and D88 round-trip tests |
| EVENTS-RAW-OLD-GUARDS | Block 1–6 final verification/patch tables | literal D88 payload offsets | `apply_raw_tables` | per-row `raw_old` guard |
| GAMEOVER-STRUCTURE | Gameover fixed/scroll token-pair tables | SUB `0x4400–0x53FF` via explicit four-base map | `apply_gameover` | declared range/token-length checks and final D88 hash |
| ENDING-24-SEGMENTS | Ending layout/correction/token tables | runtime `0x9680` stream, 24 `0F` delimiters | `apply_raw_tables` | segment and terminator tests |
| KANJI-476-TXT | KANJI1 edit kit | 476 explicit 32-byte ROM slots | `build_rom` | glyph, slot, input/output hash checks |
| LOGO-RAW-MAP | Logo analysis and decoder map | direct D88 byte ranges; decoders `0x05CE`, `0x061F` | `apply_raw_tables` | `raw_old` guard and release hash |
| ERROR07-FINAL-TABLE | ERROR 07 final patch table | command stream `0xBE8A–0xBEDC` | `apply_raw_tables` | `raw_old` guard and release hash |
| REL-102-COMPONENT-CLOSURE | v1.02 closed-release verification | final component tables: game-over token pairs, 7,521 logo rows, 11 event-row updates, 11 ERROR 07 updates | component serializers | per-row original preimage and final D88 SHA |

## Text traceability

Original Japanese and Korean translation strings are source records, not generated output. `source/accepted/text/source-index.json` and the JSONL files retain original text, Korean text, token pairs, table/row provenance, and component membership. `text-lint` checks their declared counts before a binary build can run.

## Final release assertion

`source/accepted/release-baseline.json` requires these outputs from the reviewed original inputs:

- Disk A: `18e274dc730902f90e4d3939ad3ac2853c927d19baf896cee88e5b22321427b8`
- KANJI1: `3a4ce60dc4a23d7918a8726b99c2192c9420313bab40c50880eea3a387243f45`

The builder fails rather than emitting a successful release log if either result differs.
