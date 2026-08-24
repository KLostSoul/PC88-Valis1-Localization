# 수동 검토 절차

검토 기록은 한국어로 남기는 것을 기본으로 합니다. 원본 바이트, 결과 바이트, 주소·섹터 위치, 원문·한글 번역, 제어 토큰, 근거 문서 위치를 서로 대조하고 독립 검토를 거친 행만 `source/accepted/`에 둡니다. 자동 추출·자동 매핑 결과는 검토 완료 자료가 아닙니다.

---

The following order is mandatory for each component.

1. Read the applicable Project document and identify the exact table/row/page or section.
2. Read the original D88/ROM at the documented location and record the literal bytes and hash.
3. Interpret the record boundary: character pair, control sequence, branch, terminator, padding, or graphic data.
4. Calculate the runtime address, physical D88 data offset, length, and any reverse-storage arithmetic by hand from the documented values.
5. Compare the result to the completed output only as a check. A disagreement is a conflict entry, not an automatic correction.
6. Enter the reviewed literal source row and provenance into `source/accepted/`.
7. A second review closes the row as `confirmed`; otherwise it remains `blocked`.

No script may promote a row from `observed`, `derived`, or `conflict` to `confirmed`.
