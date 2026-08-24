# PC-88 Valis 1 Localization

PC-8801판 《몽환전사 바리스 1》 한글화 자료를 원본 입력과 명시적 소스에서 재현하는 저장소다.

이 저장소의 빌드는 IPS를 적용하는 패치 배포물이 아니다. 사용자가 합법적으로 보유한 원본 Disk A D88과 KANJI1 ROM을 입력으로 받고, 완료 아카이브 안의 CSV·DOCX 표·로고 소스 스트림·D88 역변환표·16×16 VISUALTXT 글리프를 Python으로 읽어 결과를 생성한다.

## 재현 빌드

- 빌더: [`tools/build_valis1.py`](tools/build_valis1.py)
- 실행 절차와 소스 해석: [`docs/integrated-reproduction-build.md`](docs/integrated-reproduction-build.md)
- 소스/완료본 대조 manifest: [`manifests/integrated-build.json`](manifests/integrated-build.json)
- 전체 아카이브 소스 감사: [`manifests/full-archive-audit.json`](manifests/full-archive-audit.json)
- 30개 분석문서의 역사적 기록과 재빌드 승격 기준: [`manifests/analysis-content-reconciliation.json`](manifests/analysis-content-reconciliation.json)

기본 실행은 다음과 같다.

```bash
python3 tools/build_valis1.py build \
  --original-disk /path/to/legally-obtained/Valis_Disk_A_original.d88 \
  --original-kanji /path/to/legally-obtained/KANJI1_original.ROM \
  --source-archive /path/to/Valis\ 1\(1\).zip \
  --output-dir build/valis1-source
```

생성물은 `Valis_Disk_A_reproduced_from_sources.d88`, `KANJI1_reproduced_from_visualtxt.ROM`, `build-report.json`이다. `--stages`로 `events,ending,logo,gameover,error,kanji` 중 필요한 단계를 선택할 수 있다.

## 검증 기준

완료 아카이브의 Block 1~6과 엔딩 최종 D88은 각각 같은 기준 원본에서 만들어진 독립 번들이다. 따라서 빌더는 선택한 단계를 순서대로 합친 합성 출력도 만들지만, 이를 존재하지 않는 “단일 누적 완료본”이라고 주장하지 않는다. 기준 원본 해시가 일치할 때 각 최종 번들을 기준 원본에서 독립적으로 다시 만든 뒤 번들 내부 D88과 비교하며, 현재 7개 비교가 모두 일치한다.

검증된 소스 아카이브:

```text
Valis 1(1).zip
SHA-256 49f6f6a9c3a7f2e787200d7b9b12ca8de0dd31315ebbb8c81197fadb5dd3ec3d
```

기준 원본은 소스 아카이브에 포함된 검증용 사본과 대조할 수 있지만 저장소에는 넣지 않는다. 로고 역변환은 7,595개 변경 작업, KANJI 글리프 원천은 476개 슬롯·15,232바이트 작업으로 확인된다. Gameover는 15개 고정 세그먼트와 35개 스크롤 블록의 토큰표를 읽고, Error 표는 문서의 D88 열과 저장값 열을 읽는다. Error 표에는 73개 실제 변경 바이트와 97개 소스 쓰기 작업의 차이 및 한 행의 범위 표기 불일치가 보고서에 남는다.

원본 D88/ROM, 완료 이미지, 전체 번역표, 글리프 원천, 패치 번들은 저작권·재배포 범위 때문에 저장소에 포함하지 않는다. 로컬 완료 아카이브 경로를 입력으로만 사용한다. 이 구조는 [PC88-Mirrors-Localization](https://github.com/PC88-Mirrors-Localization)의 소스·빌드·검증자료 분리 원칙을 참고하되, 그 프로젝트의 토큰·VWF 규격을 Valis 1에 자동 적용하지 않는다.

정적 소스·바이트 대조는 빌더가 수행한다. 실제 QUASI88 부팅, 화면, 글자 의미, 입 모양, 장면 전환의 전수 검증은 이 저장소에서 완료됐다고 주장하지 않으며 별도 실행 gate다.

```bash
python3 -m unittest discover -s tests -v
python3 tools/build_valis1.py inspect-source \
  --source-archive /path/to/Valis\ 1\(1\).zip
```
