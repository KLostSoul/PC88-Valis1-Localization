# Manual review protocol

The following order is mandatory for each component.

1. Read the applicable Project document and identify the exact table/row/page or section.
2. Read the original D88/ROM at the documented location and record the literal bytes and hash.
3. Interpret the record boundary: character pair, control sequence, branch, terminator, padding, or graphic data.
4. Calculate the runtime address, physical D88 data offset, length, and any reverse-storage arithmetic by hand from the documented values.
5. Compare the result to the completed output only as a check. A disagreement is a conflict entry, not an automatic correction.
6. Enter the reviewed literal source row and provenance into `source/accepted/`.
7. A second review closes the row as `confirmed`; otherwise it remains `blocked`.

No script may promote a row from `observed`, `derived`, or `conflict` to `confirmed`.

