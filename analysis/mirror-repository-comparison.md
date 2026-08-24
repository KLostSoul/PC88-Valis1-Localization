# 영문 패치 저장소와의 구조 비교

이 프로젝트의 기준 언어는 한국어입니다. 영문 패치 저장소는 구조만 참고하며 결과 바이너리나 소스를 복사하지 않습니다. 영문 설명은 이 문서 아래의 보조 참고 내용입니다.

---

Reference: `KLostSoul/PC88-Valis1-Localization` (read-only structural reference). It is not modified by this project and its code/data are not copied into this repository.

The useful comparison is methodological: preserve original-media inputs, keep analysis separate from authored patch data, provide deterministic build commands, and verify a locally produced result. This Korean reproduction uses Python rather than the reference project's implementation language, and it uses debugger-derived direct binary edits rather than an assembler pipeline.

| Requirement | This build |
|---|---|
| Original D88/ROM input gate | exact size and SHA-256 required |
| Direct edit data | literal guarded D88 spans and 476 ROM glyph slots |
| Text audit | Japanese original, Korean translation, tokens, and provenance are separate sources |
| Debugger rationale | observation files only; never assembled |
| Build entry point | `python -m tools.valis_rebuild build` |
| Verification | source lint, 10 tests, output hashes, optional local byte comparison |
| Completed media / IPS | local comparison-only; ignored and rejected as build inputs |

The completed v1.02 result is reproduced from the reviewed original inputs:

- D88 SHA-256: `18e274dc730902f90e4d3939ad3ac2853c927d19baf896cee88e5b22321427b8`
- KANJI1 SHA-256: `3a4ce60dc4a23d7918a8726b99c2192c9420313bab40c50880eea3a387243f45`
