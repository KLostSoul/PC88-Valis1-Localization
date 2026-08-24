# Mirror-repository comparison

검사 기준일: 2026-08-25

비교 대상: [Mistranger/mirrors_tools](https://github.com/Mistranger/mirrors_tools)

## 결론

현재 결과물은 **원본 미디어에서 출발하는 재현 빌드 후보**이지, 미러 저장소 수준의 **완료된 byte-identical 재현 빌드**는 아니다.

원본 D88/ROM을 입력으로 한 구조 검증과 소스 검증은 통과했지만, 로컬 비교 전용 완료본과의 exact 비교에서 6,397바이트가 다르므로 최종 릴리스 게이트는 차단 상태다.

## 미러 저장소와의 구조 대조

참조 저장소는 `Data`, `Export`, `GFX`, `Ghidra`, `Import`, `Ruby`, `Tools`를 최상위 작업 영역으로 두고 `Ruby/main.rb`를 빌드 진입점으로 사용한다.

| 역할 | 미러 저장소 | 현재 로컬 소스 | 판정 |
|---|---|---|---|
| 원본/분석 데이터 | `Data` | `source/accepted`, `analysis/evidence-ledger.json` | 대응됨 |
| export/import 단계 | `Export`, `Import` | `export-original`, `build-d88`, `build-rom`, `build` CLI | 기능 대응됨 |
| 그래픽/문자 데이터 | `GFX` | `source/accepted/kanji`, `source/accepted/text` | 대응됨 |
| 역분석/디버거 관찰 | `Ghidra`, `Ruby`, `Tools` | `source/accepted/asm`, `analysis/evidence-ledger.json` | 관찰 자료 대응 |
| 단일 빌드 진입점 | `Ruby/main.rb` | `python -m tools.valis_rebuild ...` | Python CLI 대응, 루트 래퍼는 없음 |
| 검증/재현 로그 | 저장소별 구현 | `build/reproduction/integrated/*-log.json`, verify/compare 보고서 | 대응됨 |
| Git 저장소 상태 | 커밋된 공개 저장소 | 현재 작업 디렉터리에 `.git`/remote/commit 없음 | 미완료 |

구조상 필요한 영역은 대부분 분리되어 있으나, 현재는 미러 저장소처럼 배포 가능한 Git 저장소 단위로 고정된 상태가 아니다.

## 실제 빌드 검증

입력 원본:

- D88: 414,992바이트, 422섹터, flat payload 407,552바이트
- KANJI1: 131,072바이트

통과한 항목:

- `source-lint`
- `text-lint`
- 통합 빌드 및 구조 verify
- unittest 9개
- KANJI1 476개 명시적 할당
- 엔딩 24개 스트림 비교
- 이벤트 블록 1~6 raw table과 컴포넌트 변경표 대조

Exact 비교:

```text
build:     a18c1c9549c7e95a762293f4677826f36058ab21be8bc84e8c8a499ee4e8ee36
reference: 18e274dc730902f90e4d3939ad3ac2853c927d19baf896cee88e5b22321427b8
different_file_bytes: 6397
```

실패가 남은 범위:

- gameover: 338바이트
- logo: 5,717바이트
- error07 tail: 11바이트
- event block 1~5: 각 2, 2, 2, 2, 3바이트
- event block 6, ending, hold: 0바이트

따라서 “빌드 명령이 실행되고 결과 파일이 구조적으로 유효하다”는 것은 확인되지만, “완료본을 소스에서 완전히 재현했다”는 판정은 현재 내릴 수 없다.

## 릴리스 판정

`candidate_with_reference_conflicts`.

미러 저장소와 같은 재현 빌드로 인정하려면 다음을 먼저 닫아야 한다.

1. gameover scroll 12~35의 날짜별 소스 테이블과 통합 비교 기준의 충돌 해소
2. logo 7,595행과 통합 기준 7,521바이트 변경량의 불일치 해소
3. error07 tail 0x316B~0x3175의 clear/non-zero 기준 확정
4. 모든 컴포넌트를 하나의 날짜 고정 baseline으로 잠금
5. Python 빌드 명령과 source-tree hash를 릴리스 문서에 고정

완료본의 바이트를 소스에 복사해 차이를 없애는 방식은 이 판정에서 허용하지 않는다. 현재 비교 이미지는 로컬에서만 사용되며 저장소 빌드 입력이 아니다.
