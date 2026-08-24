# PC-88 무겐전사 바리스 1 한글패치 재현 빌드

이 저장소는 PC-88판 《무겐전사 바리스 1》의 한국어 한글패치를 원본 매체에서 다시 만드는 Python 기반 재현 빌드입니다.

빌드는 사용자가 제공한 원본 D88과 `KANJI1.ROM`을 읽고, 분석과 디버거 확인을 거쳐 확정한 직접 바이트 표를 원본 복사본에 적용합니다.

## 빌드 구성

- `analysis/`: 분석 근거 장부와 디버거 관찰 자료
- `source/accepted/`: 원문·한글 번역·제어 토큰·직접 바이트·KANJI1 글리프 원천표
- `tools/valis_rebuild/`: D88 처리기, 원본 바이트 검사기, 직접 기록기, ROM 생성기
- `tests/`: 소스·구조·직렬화·통합 검증
- `docs/`: 작업 문서

## 빌드 원칙

```text
분석 근거와 디버거 확인
        ↓ 수동 검토
확정된 원문·한글 번역·토큰·직접 바이트 표
        ↓ 원본 바이트 대조
원본 D88/ROM 복사본에 직접 기록
        ↓ 구조·해시·테스트 검증
재현된 D88/ROM
```

빌더는 사람이 확정한 행을 검사하고 기록합니다.

## 실행

저장소 루트에서 실행합니다.

```sh
PYTHONPATH=. python -m tools.valis_rebuild source-lint
PYTHONPATH=. python -m tools.valis_rebuild text-lint
PYTHONPATH=. python -m unittest discover -s tests -v
```

원본 D88과 KANJI1 ROM을 지정해 빌드합니다.

```sh
PYTHONPATH=. python -m tools.valis_rebuild build \
  --d88 /path/to/original.d88 \
  --rom /path/to/KANJI1.ROM \
  --out build/reproduction
```

출력을 검증합니다.

```sh
PYTHONPATH=. python -m tools.valis_rebuild verify \
  --d88 build/reproduction/d88/valis_disk_a.d88 \
  --rom build/reproduction/kanji/KANJI1.ROM
```

결과를 기준 파일과 대조합니다.

```sh
PYTHONPATH=. python -m tools.valis_rebuild compare \
  --built build/reproduction/d88/valis_disk_a.d88 \
  --reference /path/to/reference.d88 \
  --fail-on-diff
```

## 결과물과 보관 범위

빌드 결과는 `build/` 아래에 생성합니다.

## 문서

- [직접 바이너리 재현 빌드 안내서](docs/direct-binary-build.md)
- [분석 근거와 빌드 소스 대응표](docs/evidence-and-source-map.md)
- [재현 빌드 검증 절차](docs/reproducibility.md)
