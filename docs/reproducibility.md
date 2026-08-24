# Reproducibility protocol

Reproducibility begins only after source acceptance.

1. Hash the user-supplied original D88/ROM and record geometry with `export-original`.
2. Review the evidence ledger and accepted-source manifest.
3. Build from those accepted literal rows only.
4. Reparse the output and verify every old/new write, sector boundary, terminator, length, debugger-derived address, and round trip.
5. Build again from the same inputs and compare output hashes.
6. Optionally compare the local result with a local completed reference. That comparison is diagnostic only and cannot change source data.

`text-lint` is a separate stage. It verifies the fixed JSONL source index, the
original/translation columns, the Korean verification rows, and the exact
1~15, 1~35, and 1~24 numbering. It never extracts a document or derives a
token.

The current exact-release status is recorded in
`analysis/reproduction-status.json`. A structural build may be reproducible
from the supplied original media while exact byte equality with a later
comparison image remains blocked by a documented version conflict.

Before acceptance, the expected reproducibility result is a deliberate build failure. A successful build before manual source closure is a defect.
