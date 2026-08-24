# 분석 계층 — 수동 근거만 사용

이 디렉터리의 작업 설명과 판단 기준은 한국어가 기본입니다. 아래 영문 내용은 구조를 확인하기 위한 보조 참고본입니다.

---

This directory is the boundary between investigation and build source.

`evidence-ledger.json` is a manually maintained ledger. Every fact that may become build input must identify the project document, section/table/row or binary location, the literal observed bytes, the address layer, and an independent review state.

The accepted source tree contains explicit original-text/Korean-translation
tables transcribed from the completion archive's analysis material. A parser
may help validate a fixed table transcription or inspect a user-supplied
original image, but it may not create an accepted source row, infer a token
mapping, select a correction constant, or promote a completed output into a
build input.

The previous automatic extraction attempt is quarantined under `analysis/quarantine/` and is ignored by Git. It is not part of the new build graph.
