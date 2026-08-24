# PC-88 바리스 1 Block 1 저장소용 통합 분석

## 1. 문서 목적과 분석 범위

이 문서는 다음 세 자료를 서로 대체하지 않고 대조해 Block 1을 저장소에 보관하기 위한 기준으로 다시 정리한 것이다.

1. `Valis_Block_1_상세통합분석.docx`: Block 1.zip 내부 원본·중첩 ZIP·CSV·JSON·MD·DOCX·ROM·D88·IPS·PNG를 처음부터 EOF까지 읽은 상세 분석.
2. `Valis_30개_통합_분석문서.docx`: 기존 프로젝트 분석문서 25개와 추가 MD 분석문서 5개를 재독해해 중복·충돌·폐기·미완료를 정리한 상위 감사.
3. `KLostSoul/PC88-Mirrors-Localization`: PC-88 한글화 저장소의 문서·소스·임시 산출물·원본 이미지 분리 정책과 재현 중심의 기록 방식을 참고한 기준.

이 문서는 Block 1의 바이트와 계보를 새로 자동 매핑하거나 숫자를 하나로 맞추는 문서가 아니다. 기존 두 분석문서에서 반복된 내용은 한 번만 남기고, 서로 다른 버전·주소·토큰·검증 범위는 충돌 등록부로 분리한다.

배포 범위는 저작권을 고려해 별도로 제한한다. 분석에 사용한 원본 게임 이미지, ROM, D88, 중첩 패치 패키지, 전체 번역표와 글리프 데이터는 저장소와 공개 압축본에 포함하지 않는다. 저장소에는 직접 작성한 분석·메타데이터·검증 지침만 둔다.

## 2. 참고 저장소에서 가져온 원칙과 적용 범위

참고한 문서:

- [PC88-Mirrors-Localization README](https://github.com/KLostSoul/PC88-Mirrors-Localization/blob/main/README.md)
- [한글화 설계 및 작업 기록](https://github.com/KLostSoul/PC88-Mirrors-Localization/blob/main/docs/korean-localization-design.md)
- [원본 CD 이미지 분석](https://github.com/KLostSoul/PC88-Mirrors-Localization/blob/main/docs/original-cd-image-analysis.md)
- [참고 저장소의 .gitignore](https://github.com/KLostSoul/PC88-Mirrors-Localization/blob/main/.gitignore)

참고 저장소에서 적용할 수 있는 공통 원칙은 다음과 같다.

- 분석 기준·소스·재현 스크립트·manifest는 문서와 함께 Git에 기록한다.
- 원본 게임 이미지, 추출된 대형 이미지, 에뮬레이터 번들, 임시 생성물은 일반 소스와 분리한다.
- 파일 생성 성공과 실제 에뮬레이터 실행 성공을 별도 검증 단계로 둔다.
- 원본과 결과물의 hash, 입력·출력 경로, 도구 버전을 고정한다.
- 시험 규격과 생산판 규격을 혼동하지 않는다.

다만 참고 저장소는 `Mirrors` 프로젝트를 대상으로 한 문서다. 그 저장소의 8×16 글리프, 500자 시험 토큰, VWF 구조를 Block 1의 Valis 런타임에 자동 적용하지 않는다. Block 1의 실제 ROM·D88·runtime stream·제어 토큰이 우선이다.

## 3. 두 기존 분석문서의 역할을 합친 결과

### 3.1 Block 1 상세 분석문서가 제공하는 것

Block 1 상세 분석문서는 실제 Block 1.zip의 산출물 계보를 파일 수준에서 고정한다.

- 초기 2026-05-20 계보: 513 text, 129 controls, `E8 0B` 공백, `0x9C63=0F`.
- 2026-05-22 completed·typofix·uniform glyph 계보: 513 text와 138 controls를 가진 별도 패치 결과들.
- 2026-05-23 direct157 계보: 입 모양 직접 변경 157개, 보류 49개.
- 2026-05-24 525 계보: 525 text, 138 controls, `0x9C7B=0F`.
- 2026-05-28 orange speech-only 계보: 540 text, 138 controls, orange speech 213, generalized 124, 공백 `18 12`, `0x9C99=0F`.

또한 IPS record·변경 바이트·D88 payload 범위·ROM/D88 크기와 해시를 독립 검산하고, 최신 계보의 파일 수준 일관성과 실제 게임 화면 검증의 부재를 구분한다.

### 3.2 30개 통합 분석문서가 제공하는 것

30개 통합 분석문서는 Block 1만이 아니라 전체 프로젝트의 상위 기술 모델을 제공한다.

- D88 container, flat payload, runtime RAM, ROM glyph, token, VRAM/display를 서로 다른 계층으로 분리한다.
- 파일 offset을 runtime RAM 주소로 산술 변환한 초기 오류를 폐기한다.
- 첫 이벤트 `0x9680–0x9C63`, `0F`, manual_v2 최소 변경 경로를 강한 부분 성공으로 남긴다.
- 두 번째 이후 이벤트, 엔딩, 로고, 글리프는 각자 다른 manifest와 검증 수준을 요구한다고 정리한다.
- `18 12` 공백과 `10 11` wait를 섞지 않으며, 일반 문자·발화 조건·별도 입 제어를 분리한다.
- D88·KANJI1 ROM·IPS·manifest·hash pair가 하나의 release unit이어야 한다고 규정한다.

### 3.3 새 저장소용 결론

두 문서를 함께 사용하면 Block 1은 “최종 패치 파일 하나”가 아니라 다음 네 층으로 보관해야 한다.

1. 원본 및 당시 생성된 패키지: 내용 변경 없이 보존.
2. 계보별 독립 분석: 513·525·540 등 서로 다른 결과를 합치지 않음.
3. 통합 기술 모델: 주소 계층·token family·검증 gate를 설명.
4. 저장소 manifest: 각 파일의 역할·hash·검증 수준·재현 상태를 기록.

## 4. Block 1 canonical 계보표

| 계보 | 실제 자료 | 핵심 값 | 저장소 판정 |
|---|---|---|---|
| 2026-05-20 초기 | ROM·D88·manifest·slot CSV·disk changes CSV | 513 text, 129 controls, `E8 0B`, `0x9C63=0F` | 초기 실험 계보. 최신 결과와 결합 금지 |
| 2026-05-22 completed | D88·ROM·IPS·runtime bin·summary·report | 513 chars, 138 controls, `0x9C63=0F` | 파일 수준 결과. 최신 정답으로 승격하지 않음 |
| 2026-05-22 typofix | `빨`·`리`·`바/랄게` 보정 ROM/D88 | completed와 후반 행·토큰 불일치 | 독립 계보. 충돌 행을 보존 |
| 2026-05-22 uniform glyph | 148 unique Hangul, 664 IPS records | 2,930 changed bytes | ROM glyph 계보. 문자열 성공과 분리 |
| 2026-05-23 direct157 | mouth direct patch CSV·JSON·script | 157 applied, 49 deferred | 부분 적용. 완료로 표시하지 않음 |
| 2026-05-24 525 | two-block repatch D88·report·summary | 525 chars, 138 controls, `0x9C7B=0F` | 확장 계보. 513과 별도 보관 |
| 2026-05-28 orange | latest JSON·CSV·IPS·D88 | 540 chars, 138 controls, 213 orange, `0x9C99=0F` | 최신 파일 계보. 실행·화면은 미검증 |

가장 최신 날짜가 가장 정확한 기능 결과라는 뜻은 아니다. 날짜는 계보 순서를 정하는 데 사용하고, 기능 판정은 해당 파일의 독립 검산과 실행 gate로 별도 결정한다.

## 5. Block 1에서 확정·부분확정·폐기할 내용

### 5.1 확정 또는 강한 파일 수준 확정

- Block 1.zip에는 실제 패치 산출물과 중간 검증자료가 들어 있다.
- 각 텍스트·CSV·JSON·MD·DOCX는 파일 끝까지 읽었고, 최신 orange CSV는 1,450행 전체를 확인했다.
- KANJI ROM은 131,072 bytes, D88은 414,992 bytes 계열이다.
- IPS record 수와 변경 바이트 범위는 산출물에서 독립적으로 파싱할 수 있다.
- 2026-05-24 525 계보와 2026-05-28 540 계보는 종료 주소와 스트림 길이가 달라 서로 다른 결과다.
- `18 12`는 후속 token layout·orange 계보의 공백이고 `10 11`은 wait 후보다. 초기 `E8 0B` 계보와 혼합하지 않는다.
- 최신 orange 계보는 구조상 540 chars, 138 controls, `0x9C99=0F`, 1,449 changed records를 함께 주장한다.

### 5.2 부분확정 또는 독립검산 필요

- token layout 표의 일부 행은 바이트를 할당하면서도 실제 한글 바이트 확인 필요라고 남아 있다.
- translation workbook은 모든 행을 확정으로 표시하지만 주소가 겹치는 구간이 있어 문서 표기만으로 확정할 수 없다.
- `빨`, `빌`, `바`, `랄게`의 글리프와 token은 계보별 주소·ROM이 다르다.
- orange 213 speech 적용과 124 generalized 예외가 실제 발화 문맥에 맞는지 확인되지 않았다.
- latest D88와 대응 KANJI ROM·glyph source가 하나의 실행 가능한 release pair인지 archive만으로 닫히지 않는다.
- IPS와 roundtrip 성공은 파일 수준 결과이며, 게임 부팅·화면 글리프·입 움직임·장면 전환 성공을 대신하지 않는다.

### 5.3 폐기 또는 재사용 금지

- 초기 513·525·540 결과를 같은 슬롯표로 자동 병합하는 것.
- 초기 `E8 0B` 공백을 후속 `18 12` 공백과 섞는 것.
- 서로 다른 base ROM에 IPS를 적용해 하나의 최종 ROM으로 부르는 것.
- 번역 문장 분할이 어색한 `…バ→…바`, 다음 `カみたい…→보 같이…`를 의미적으로 확정하는 것.
- bundle 이름의 completed/final 표기를 전체 기능 완료로 사용하는 것.

## 6. 참고 저장소 방식으로 재구성한 저장소 구조

저장소의 루트는 분석·문서·증거 패키지를 구분한다.

```text
PC88-Valis1-Localization/
├─ README.md
├─ docs/
│  ├─ valis-block1-repository-analysis.md
│  └─ valis-block1-distribution-scope.md
├─ evidence/
│  └─ Valis_Block1_정리본_2026-08-24_copyright-safe.zip
└─ manifests/
   ├─ block1_file_manifest.sha256
   ├─ block1_lineage_register.csv
   ├─ block1_conflict_register.csv
   └─ block1_source_inventory.csv
```

원본 D88·ROM과 패치 패키지는 저장소나 공개 압축본에 재배포하지 않는다. 대신 계보명·수량·종료 주소·검증 범위·충돌만 기록하고, 원본이 필요하면 사용자가 합법적으로 보유한 로컬 자료를 별도 입력으로 사용하도록 한다. 이는 참고 저장소의 소스/문서/임시 산출물 분리 원칙을 저작권 보수적으로 적용한 것이다.

## 7. 저작권 보수형 Block 1 압축본의 내부 구조

공개 압축본은 원본 바이트를 재배포하지 않고, 다음의 분석·메타데이터만 담는다.

```text
Valis_Block1_정리본_2026-08-24/
├─ README.md
├─ 00_analysis/
│  └─ valis-block1-repository-analysis.md
├─ source_inventory.csv
└─ 99_audit/
   ├─ block1_file_manifest.sha256
   ├─ block1_lineage_register.csv
   └─ block1_conflict_register.csv
```

`source_inventory.csv`는 분석에 사용한 로컬 입력의 종류와 재배포 여부만 기록한다. `block1_file_manifest.sha256`는 공개 압축본 내부 파일의 해시만 포함하며, 제외된 원본의 바이트를 복원하거나 대체하지 않는다.

## 8. 저장소에 포함할 것과 제외할 것

### 공개 저장소와 압축본에 포함

- 새로 작성한 MD 분석문서.
- 계보표·충돌표·공개 압축본의 SHA-256 manifest.
- 원본 입력의 종류·날짜·검증 역할·재배포 상태를 적은 inventory.
- 원본을 다시 배포하지 않고도 후속 검증을 설계할 수 있는 지침.

### 로컬 분석 입력으로만 사용

- D88·ROM·IPS·중첩 ZIP·원본 게임 이미지.
- 전체 번역표·글리프 시트·원문 대사와 이를 재현하는 대형 CSV/JSON.
- 사용자가 제공한 원본 DOCX와 token layout/workbook.

### 저장소와 공개 압축본에서 제외

- 추출된 D88·ROM을 여러 경로에 복제한 파일.
- 패치 적용 후의 게임 이미지와 배포용 ROM/D88.
- 렌더링 PNG/PDF, 임시 추출 텍스트, 로컬 작업 로그.
- 서로 다른 계보를 하나로 재생성한 “최종” ROM/D88.

이 구분은 특정 관할의 저작권 판단을 대신하는 법률 자문이 아니다. 권리 확인 없이 원본·파생 게임 데이터를 공개 저장소로 옮기지 않기 위한 보수적 배포 기준이다.

## 9. 필수 manifest와 release unit

Block 1 결과를 나중에 실제 패치에 사용하려면 다음 세트를 하나의 release unit으로 기록해야 한다.

| 필드 | 내용 |
|---|---|
| source identity | 원본 D88 SHA-256, KANJI1 base ROM SHA-256 |
| lineage | 2026-05-20 / 05-22 / 05-23 / 05-24 / 05-28 중 하나 |
| runtime range | 시작 주소, 종료 주소, `0F`, 스트림 길이 |
| token policy | 문자·공백·wait·mouth·eye·CG·clear를 별도 family로 기록 |
| patch evidence | old/new byte, D88 offset, IPS record, 변경 이유 |
| glyph evidence | 문자, token, slot, ROM offset, 32B hash, 확정 수준 |
| execution gate | 파일 roundtrip, 에뮬레이터 부팅, 화면 캡처, 사용자 재현 여부 |

현재 Block 1은 lineage와 파일 수준 evidence는 여러 개 존재하지만, 모든 필드가 하나의 최신 release unit으로 묶여 있지 않다. 따라서 이번 저장소 push는 “검증 완료 패치 배포”가 아니라 “정리된 증거·분석 저장”으로 표시한다.

## 10. 다음 검증 순서

1. 새 저장소의 manifest에서 각 파일의 SHA-256과 원본 압축본 내부 경로를 고정한다.
2. 513·525·540 계보를 각각 독립적으로 복호해 runtime HL 진행과 종료 `0F`를 재확인한다.
3. token layout의 “실제 바이트 확인 필요” 행과 workbook 중첩 행을 우선 재덤프한다.
4. 최신 orange D88·대응 KANJI ROM·glyph source를 같은 실행 세트로 묶는다.
5. 각 한글 token을 glyph slot·32-byte ROM data·화면 글리프로 연결해 수동 검증한다.
6. 에뮬레이터에서 이벤트 시작·대화 중간·`0x9C99=0F` 직전·장면 전환을 캡처한다.
7. direct157의 157 적용·49 보류와 orange의 213 speech 적용을 동일 실행본에서 비교한다.
8. 검증되지 않은 계보는 폐기하지 않고 historical lineage로 남기며, production release와 분리한다.

## 11. 최종 판정

Block 1의 두 기존 분석문서와 30개 통합문서를 대조한 결과, Block 1에는 실제 패치·글리프·토큰·입 모양 작업의 여러 재현 가능한 파일 계보가 있다. 그러나 513·525·540자 계보를 하나의 최종본으로 통합할 수 없고, 최신 540자 계보도 파일 수준 일관성과 실제 게임 기능 성공을 동일시할 수 없다.

참고 저장소의 구조를 적용해 새 저장소에는 분석문서·manifest·저작권 보수형 압축본을 구분해 기록한다. 이번 push의 의미는 Block 1 분석 결과와 계보를 잃지 않도록 정리하고 후속 검증이 가능한 상태로 고정하는 것이며, 원본 게임 데이터나 전체 게임 한글화가 공개·완료됐다고 선언하는 것이 아니다.

최종 상태(당시 Block 1 계보 감사): **513·525·540 중간 계보를 자동 병합하지 않으며, 각각은 historical lineage로 보존한다.**

## 12. 전체 완료본 대조 후의 통합 재현 기준

이후 제공된 `Valis 1(1).zip`은 Block 1~6·엔딩·로고·Gameover·KANJIROM 자료와 25개 Project 분석문서 및 5개 MD 분석문서를 함께 담은 전체 완료본이다. 이 아카이브를 다시 파일 단위로 확인한 결과는 다음과 같다.

- 전체 아카이브 SHA-256: `49f6f6a9c3a7f2e787200d7b9b12ca8de0dd31315ebbb8c81197fadb5dd3ec3d`.
- 최상위 파일 65개를 해시로 고정하고, 분석 DOCX 30개(Projects 25개 + MD 분석 5개)를 전부 읽어 문서 XML 통계를 기록했다.
- Block 1~6 및 엔딩의 최종 패치 번들 7개는 각각 IPS·D88·JSON·CSV 구성을 확인했다. 각 번들의 보고서에서 문서 스트림 불일치 0, 선언 영역 밖 변경 0, 파일 크기 변경 없음이 확인되는 경우를 수치로 기록했다.
- 최상위 `Valis_Korean_Disk_A_Patch_Ver_1.02.ips`와 `VALIS_KANJI1_ROM_Patch_Ver_1.02.ips`는 내부 `Valis1_PC88_Localization_Skills_IPS_Only_2026-08-09.zip`의 재현 자산과 바이트 단위로 동일하다.

따라서 재빌드는 중간 Block 1 스트림을 문서에서 자동으로 다시 만들거나 513·525·540 계보를 합치는 방식이 아니다. 완료본에서 확인된 통합 IPS 두 개를 정확히 고정하고, 사용자가 직접 보유한 일치 원본 D88·KANJI1 ROM에 적용한 뒤 입력 해시·IPS 레코드·D88 구조·결과 해시를 검사한다. 이 절차는 `tools/reproduce_valis1.py`와 `docs/integrated-reproduction-build.md`에 구현되어 있으며, 전체 완료본 감사 결과는 `manifests/full-archive-audit.json`에 남긴다.

이 재현 판정은 파일 수준이다. QUASI88에서의 부팅, 화면 글리프, 발화 입 모양, 장면 전환, 엔딩·게임오버·스태프롤은 통합 빌드 후 별도 실행 gate로 남긴다. 원본·완성 D88/ROM과 전체 번역/글리프 데이터는 공개하지 않는다.
