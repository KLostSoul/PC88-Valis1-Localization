# Component review packages

Each package is a separate manual review unit. The package is not complete when a table has merely been extracted; it is complete only when its literal rows, provenance, address arithmetic, and original-byte checks have been independently reviewed.

| Package | Required manual outputs | Current state |
|---|---|---|
| original media | D88 sector map, ROM geometry, hashes | accepted and build-guarded |
| event blocks 1–6 | rows, controls, `0F`, runtime/storage map, old bytes | accepted; raw tables match six component CSVs |
| game-over fixed 1–15 | pair rows, terminators, raw spans, old bytes | accepted source; integrated baseline conflict remains |
| game-over scroll 1–35 | 20-pair bodies, markers, storage, old bytes | accepted source; blocks 12–35 baseline conflict remains |
| ending 1–24 | segment rows, lengths, terminators, correction ranges | accepted; 24 terminators/3622-byte stream |
| control registry | literal sequences and proven semantics | accepted |
| KANJI1 | glyph/token/slot assignments and ROM byte checks | accepted; 476 assignments |
| title/logo | source bitmap, encoder, RAM map, D88 reverse map | accepted source; exact-release conflict remains |
| Debugger observations | actual entrypoints, branches, free space, observed bytes | accepted inspection sources; never assembled |
