# 재현 빌드 검증 절차

한국어 기준 절차는 [한국어 재현 빌드 검증 절차](ko/reproducibility.md)입니다. 아래 영문은 보조 참고본입니다. 원본 D88/ROM → 확정 소스 표 → Python 직접 기록 → 재파싱·해시·테스트 순서를 지키며, 완료본이나 IPS는 빌드 입력으로 사용하지 않습니다.

---

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
