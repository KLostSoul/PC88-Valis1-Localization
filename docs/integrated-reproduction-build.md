# 통합 소스 재현 빌드

이 문서는 완료 아카이브에서 확인한 소스를 Python으로 다시 읽어 Disk A D88과 KANJI1 ROM을 생성하는 절차를 고정한다. IPS를 읽거나 적용하지 않으며, IPS 파일은 빌드 입력·검증 근거·배포 결과가 아니다.

## 입력

| 입력 | 준비 방법 | 검사 |
|---|---|---|
| 원본 Disk A | 사용자가 합법적으로 보유한 원본의 경로를 직접 지정 | D88 414,992바이트, 혼합 섹터 구조 |
| 원본 KANJI1 ROM | 사용자가 합법적으로 보유한 원본의 경로를 직접 지정 | 131,072바이트 |
| 완료 소스 아카이브 | 사용자 로컬의 `Valis 1(1).zip` | SHA-256 `49f6f6a9c3a7f2e787200d7b9b12ca8de0dd31315ebbb8c81197fadb5dd3ec3d` |

원본 D88과 ROM은 저장소에 넣지 않는다. 빌더는 원본을 덮어쓰지 않고 새 출력 파일을 만든다.

## 소스 단계

빌더는 아카이브를 다음 순서의 명시적 단계로 읽는다.

1. `events`: Block 1~6의 최종 `*_changes_*.csv`를 읽는다. 각 CSV의 `disk_offset`, `raw_old`, `raw_new`를 그대로 사용한다.
2. `ending`: 엔딩 최종 `*_changes.csv`를 읽는다.
3. `logo`: 로고 편집 키트의 세 개 원천 스트림과 `ram_to_raw_reverse_map_2800_6159_verified.csv`를 읽고, 각 RAM 바이트를 D88 raw 바이트로 역변환한다. 역변환식은 `DE = 0x400 - raw_index`, `correction = 0x40 - d88_c`, `new_raw = (desired + hi(DE) + lo(DE) - correction) & 0xFF`다.
4. `gameover`: 고정 15세그먼트와 스크롤 35블록의 DOCX 토큰표를 읽는다. SUB→D88 네 그룹과 `0x3A` 보정식을 사용하며, 0F 종료 토큰도 표의 범위에 따라 명시적으로 기록한다.
5. `error`: Error 메시지 DOCX의 D88 열과 D88 저장값 열을 읽는다. 문서 표의 실행 주소를 D88 오프셋으로 대체하지 않는다. 50번 미사용 행은 범위 표기와 11바이트 값 수가 불일치하므로 경고를 build report에 남긴다.
6. `kanji`: KANJI 편집 키트의 476개 VISUALTXT를 읽는다. 각 파일의 16개 16픽셀 행을 32바이트로 변환해 파일명에 명시된 `off` 위치에 쓴다. 일본어 슬롯을 자동 매핑하거나 글리프 이름을 추정하지 않는다.

## 실행

```bash
python3 tools/build_valis1.py build \
  --original-disk /path/to/Valis_Disk_A_original.d88 \
  --original-kanji /path/to/KANJI1_original.ROM \
  --source-archive /path/to/Valis\ 1\(1\).zip \
  --output-dir build/valis1-source
```

단계 선택 예:

```bash
python3 tools/build_valis1.py build \
  --original-disk /path/to/Valis_Disk_A_original.d88 \
  --original-kanji /path/to/KANJI1_original.ROM \
  --source-archive /path/to/Valis\ 1\(1\).zip \
  --output-dir build/events-ending \
  --stages events,ending
```

출력 디렉터리에는 다음이 생긴다.

```text
Valis_Disk_A_reproduced_from_sources.d88
KANJI1_reproduced_from_visualtxt.ROM
build-report.json
```

`build-report.json`에는 입력 해시, 소스 아카이브 해시, 단계별 작업 수·변경 바이트·D88 구조, Error 표 경고, 출력 해시가 기록된다.

## 완료본 대조 방법

Block 1~6과 엔딩의 최종 D88은 서로 다른 독립 결과다. `events,ending`을 한 번에 선택하면 각 CSV를 순서대로 원본에 적용한 합성 D88이 생성되지만, 그 합성 D88을 아카이브의 어느 한 번들 최종 D88이라고 부르지 않는다.

기준 원본 해시가 완료 아카이브의 canonical baseline과 같으면 빌더는 다음을 추가로 수행한다.

- Block 1 CSV만 기준 원본에 적용 → Block 1 번들 내부 D88과 비교
- Block 2 CSV만 기준 원본에 적용 → Block 2 번들 내부 D88과 비교
- 같은 방식으로 Block 3~6과 엔딩까지 비교

현재 7개 비교는 모두 일치한다. 로고 단독 단계도 키트의 기준 결과 해시와 일치한다. Gameover·Error는 완료 아카이브에 같은 형식의 독립 최종 D88 기준이 없으므로, 토큰표 파싱·주소 변환·충돌·변경 바이트 수를 정적 gate로 기록하고 화면 검증을 완료로 가장하지 않는다.

## 재현성·저작권 경계

- 저장소에는 원본 D88/ROM, 완료 D88/ROM, 원본 번역표, 글리프 소스, 패치 번들을 넣지 않는다.
- 완료 아카이브는 로컬 경로 입력이며 자동 다운로드하지 않는다.
- IPS를 사용해 결과를 만드는 경로는 없다. 소스가 부족하면 빌드가 성공한 것처럼 보정하지 않고 오류 또는 경고를 보고한다.
- 513·525·540 슬롯의 Block 1 중간 계보, 추정 제어 토큰, 자동 JIS/Unicode 글리프 매핑은 빌드 입력으로 승격하지 않는다.
- 실제 QUASI88 부팅·화면·문장 의미·입 모양·장면 전환 전수 검증은 별도 실행 gate다.

구조와 검증자료를 분리하는 방식은 [PC88-Mirrors-Localization](https://github.com/PC88-Mirrors-Localization)을 참고했다. 다만 이 저장소의 source stream·D88 변환식·글리프 슬롯 규칙은 Valis 1 자료에서 직접 확인한 값이다.
