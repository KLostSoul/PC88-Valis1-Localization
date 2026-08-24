# Evidence status

The repository is a closed `v1.02_direct_binary_reproduction` build.

- Original D88 geometry and KANJI1 geometry are verified at build time by size and SHA-256.
- Blocks 1–6 retain separate Japanese/original, Korean translation, token, and raw-byte sources.
- Game-over retains fixed 1–15, scroll 1–35, marker, and hold sources; ending retains 24 independently delimited segments.
- Logo, ERROR 07, token consumer, and KANJI1 direct-edit evidence remain explicit sources and debugger observations.
- The final v1.02 values are now in their owning component tables: game-over rows/tokens, logo raw bytes, ERROR 07 bytes, and event rows. No post-component reconciliation table remains.
- The completed ZIP and its binaries remain local comparison-only evidence.

`source-lint`, the ten tests, input preimage checks, final-output hash checks, and optional local `compare --fail-on-diff` together form the release gate.
