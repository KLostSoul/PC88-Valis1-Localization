# PC-88 무겐전사 바리스 1 — 재현 빌드

이 저장소는 PC-88판 《무겐전사 바리스 1》 한글화 결과를 원본 매체에서 다시 만드는 Python 기반 직접 바이너리 수정 프로젝트입니다.

완료본을 입력으로 사용하거나 IPS 패치를 적용하는 방식이 아닙니다. 사용자가 별도로 보유한 원본 D88과 KANJI1 ROM을 읽고, 사람이 검토·확정한 바이트 기록을 원본 위치에 그대로 적용합니다. 역어셈블·디버거 분석은 수정 위치와 실행 경로를 설명하는 근거이며, 어셈블러 입력이나 자동 코드 생성 입력이 아닙니다.

## 저장소에 들어 있는 것

- `analysis/`: 분석 근거, 증거 장부, 영문 패치 저장소와의 구조 비교
- `source/accepted/`: 확정된 원문/한글 번역, 제어 토큰, 블록별 raw 바이트, 엔딩·게임오버·로고·ERROR 07 자료, KANJI1 글리프 표
- `tools/valis_rebuild/`: D88 파서, 원본 바이트 가드, 직접 바이너리 직렬화기, KANJI1 생성기, CLI
- `tests/`: 소스 장부·D88 구조·직렬화·최종 결과 검증
- `docs/ko/`: 한국어 작업 설명서

## 저장소에 들어 있지 않은 것

원본 D88/ROM, 완료본 ZIP, 완료 D88/ROM, IPS, PNG/BMP와 같은 저작권 자료는 저장하지 않습니다. 이 파일들은 사용자가 로컬에서 제공하고, 완료본은 로컬 비교용으로만 사용할 수 있습니다. `.gitignore`가 해당 확장자와 로컬 작업 디렉터리를 제외합니다.

## 빌드 흐름

```text
사용자 로컬 원본 D88/ROM
        ↓ 원본 해시·크기·구조 확인
확정된 리터럴 소스 테이블
        ↓ 원본 바이트 가드 후 직접 기록
재조립된 D88/ROM
        ↓ 재파싱·해시·통합 테스트
검증 로그와 로컬 비교 결과
```

빌드 시 완료본에서 문서를 자동 추출하거나 토큰을 자동 매핑하지 않습니다. 소스 테이블은 분석·디버거 관찰·수동 검토를 거쳐 확정된 자료만 사용합니다.

## 빠른 시작

```sh
PYTHONPATH=. python -m tools.valis_rebuild source-lint
PYTHONPATH=. python -m tools.valis_rebuild text-lint
PYTHONPATH=. python -m unittest discover -s tests -v

PYTHONPATH=. python -m tools.valis_rebuild build \
  --d88 /경로/원본.d88 \
  --rom /경로/KANJI1.ROM \
  --out build/reproduction

PYTHONPATH=. python -m tools.valis_rebuild verify \
  --d88 build/reproduction/d88/valis_disk_a.d88 \
  --rom build/reproduction/kanji/KANJI1.ROM
```

완료본과의 비교가 필요할 때만 비교 파일을 로컬 경로로 지정합니다.

```sh
PYTHONPATH=. python -m tools.valis_rebuild compare \
  --built build/reproduction/d88/valis_disk_a.d88 \
  --reference /로컬에만-있는-비교용-완료본.d88 \
  --fail-on-diff
```

비교 명령은 소스 테이블을 수정하지 않으며, 비교 파일을 빌드 입력으로 취급하지 않습니다.

자세한 설명은 [한국어 재현 빌드 안내서](docs/ko/direct-binary-build.md)와 [한국어 근거·바이트 대응표](docs/ko/evidence-and-source-map.md)를 참조하십시오.
