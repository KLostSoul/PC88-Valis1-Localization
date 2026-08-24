# 재현 빌드 설계

## 프로젝트 영역

| 영역 | 내용 | 빌드 사용 |
|---|---|---|
| `analysis/` | 사람이 기록한 분석 근거와 검토 기록 | 근거 확인 |
| `source/accepted/` | 리터럴 바이트·토큰·주소·텍스트 원천표 | 사용 |
| 로컬 비교 영역 | 완료본·IPS·추출 이미지 | 사용하지 않음 |

## 처리 흐름

원본 D88/ROM을 읽기 전용으로 검사하고, 분석 근거와 원본 바이트를 대조한 뒤, 검토된 원천표만 직접 기록기에 전달합니다. 기록기는 원본 복사본에 명시된 old/new 바이트를 쓰고 결과를 다시 파싱·검증합니다.

## 원천 행의 계약

각 행은 컴포넌트, 실행 주소 또는 물리 위치, 이전 값, 새 값, 길이, 근거 위치, 검토 상태를 가져야 합니다. 이전 값 누락, 중복 오프셋, 모호한 주소, 추정 토큰은 빌드 오류입니다.

## 명령

```text
PYTHONPATH=. python -m tools.valis_rebuild source-lint
PYTHONPATH=. python -m tools.valis_rebuild text-lint
PYTHONPATH=. python -m tools.valis_rebuild build --d88 /path/to/original.d88 --rom /path/to/KANJI1.ROM
PYTHONPATH=. python -m tools.valis_rebuild verify --d88 build/reproduction/d88/valis_disk_a.d88 --rom build/reproduction/kanji/KANJI1.ROM
```

완료본 비교는 선택적 읽기 전용 작업이며, 비교 결과로 원천표를 자동 갱신하지 않습니다.
