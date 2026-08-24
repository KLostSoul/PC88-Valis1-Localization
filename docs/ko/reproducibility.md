# 재현 빌드 검증 절차

## 목적

이 절차는 “완료본을 복사했는가”가 아니라, 원본 D88/ROM과 저장소에 공개된 확정 소스만으로 같은 결과를 다시 만들 수 있는지를 확인합니다.

## 실행 순서

```sh
PYTHONPATH=. python -m tools.valis_rebuild source-lint
PYTHONPATH=. python -m tools.valis_rebuild text-lint
PYTHONPATH=. python -m unittest discover -s tests -v
```

그 다음 사용자가 보유한 원본을 지정합니다.

```sh
PYTHONPATH=. python -m tools.valis_rebuild build \
  --d88 /경로/원본.d88 \
  --rom /경로/KANJI1.ROM \
  --out build/reproduction
```

출력 검증은 다음과 같습니다.

```sh
PYTHONPATH=. python -m tools.valis_rebuild verify \
  --d88 build/reproduction/d88/valis_disk_a.d88 \
  --rom build/reproduction/kanji/KANJI1.ROM
```

동일 명령을 별도 출력 디렉터리에 한 번 더 실행하고 두 결과의 SHA-256을 비교합니다. 완료본은 필요할 때만 다음처럼 비교합니다.

```sh
PYTHONPATH=. python -m tools.valis_rebuild compare \
  --built build/reproduction/d88/valis_disk_a.d88 \
  --reference /로컬-비교용-완료본.d88 \
  --fail-on-diff
```

## 검증 단계의 의미

| 단계 | 확인 내용 | 소스 변경 여부 |
|---|---|---|
| `source-lint` | 확정 표·경로·해시 계약 | 없음 |
| `text-lint` | 원문·번역·토큰·번호 체계 | 없음 |
| `export-original` | 원본 D88 트랙·섹터·payload 구조 | 없음 |
| `build-d88` | 원본 가드와 직접 raw 기록 | 출력 생성 |
| `build-rom` | 476개 글리프와 ROM 오프셋 | 출력 생성 |
| `verify` | 결과 구조·크기·해시·재파싱 | 없음 |
| `compare` | 로컬 완료본과의 차이 | 없음 |

자동 추출·자동 매핑·완료본 역입력은 어느 단계에도 포함되지 않습니다. 불일치가 나오면 소스 행과 분석 근거를 사람이 다시 검토해야 하며, 비교 결과를 자동으로 패치표로 승격하지 않습니다.

## 커밋·배포 경계

Git에는 Python 코드, 문서, 확정 텍스트/토큰 표, raw 변경표, KANJI 글리프 소스만 둡니다. 원본과 결과 바이너리, 완료본 압축파일, IPS, 로컬 로그·비교 산출물은 `.gitignore`로 제외합니다.
