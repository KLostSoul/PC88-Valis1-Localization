# Direct-binary reproduction method

This is not an assembler build and does not derive source from a completed image at build time. The builder copies the reviewed original D88 and KANJI1, then applies literal, guarded byte records. Debugger/disassembly material records why a location is safe to change; it is not assembled or injected.

## Closed build path

```text
reviewed original D88 / KANJI1
  -> verify exact input SHA-256 and size
  -> apply final literal event, game-over, ending, logo, ERROR 07, and glyph records
  -> require the two final SHA-256 values
```

No command accepts a ZIP, IPS, completed D88, completed ROM, or a reference directory as a build input. `compare` is a separate local-only audit command.

## Source categories

| Category | Build source | Completion-archive evidence |
|---|---|---|
| Events 1–6 | `tables/events/block-*-raw-changes.csv`, original/translation JSONL | Block 1–6 translation and verification workbooks |
| Game-over | `text/gameover-*.jsonl`, hold table | fixed 1–15 and scroll 1–35 token-pair tables |
| Ending | `tables/ending/*`, `text/ending-24.jsonl` | 24-segment layout, correction, and verification tables |
| Logo / ERROR 07 | literal raw-change CSVs | logo decode map and ERROR 07 patch table |
| KANJI1 | 476 16×16 glyph files plus assignments | KANJI1 edit kit and slot table |
| Final component contract | `release-baseline.json` | closed v1.02 release verification |

There is no post-component reconciliation table. The component sources themselves are final original-to-release records: the logo table has 7,521 final raw-byte rows, game-over token pairs are the final physical stream values, and event/ERROR 07 rows carry their final raw bytes. Every literal raw-table row is checked against the supplied original byte.

## Debugger facts retained as reference

`source/accepted/asm/` is an observation record only. It records the event consumer at PC `0x02ED` (`5E 23`), stream terminators, and the distinction between runtime main/sub memory and D88 file data. There is deliberately no assembler invocation, object file, hook linker, or generated machine-code stage.
