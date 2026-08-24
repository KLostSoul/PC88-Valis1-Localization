# Evidence status

The repository is currently a `candidate_with_reference_conflicts` build.

- The original D88 geometry and KANJI1 geometry are closed and checked at build time.
- The event block 1~6 raw tables match the corresponding final component change CSVs by offset and new byte; their original/Japanese and Korean verification tables are stored separately.
- The ending source contains 24 literal segments, original/Korean text rows, base-code tokens, raw changes, and 24 terminators.
- Game-over, logo, and ERROR 07 sources are present as literal reviewed tables, but the dated component documents and later integrated comparison image do not form one version-locked baseline.
- The completed ZIP remains local comparison material only. Its binary, IPS, and extracted payload are not source inputs.
- A conflict or missing reverse map blocks exact-release status; it is never resolved by selecting whichever value makes a reference image match.

`source/accepted/source-manifest.json` gates structural source builds. The exact-release gate is recorded in `analysis/reproduction-status.json` and must remain blocked while its listed conflicts exist.
