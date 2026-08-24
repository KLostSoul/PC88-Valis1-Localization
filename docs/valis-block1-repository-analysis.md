# Valis 1 통합 분석·재빌드 정리본

이 문서는 기존 Block 1 계보 기록과 `Valis 1(1).zip` 전체 완료본을 대조해, 실제 통합 빌드에 필요한 기준만 남긴 정리본이다. 문서에 적힌 문자열·토큰·주소를 자동 매핑해 새 결과를 만들지 않는다. 최종 빌드의 권위 있는 입력은 완료본에서 확인한 1.02 IPS 두 개이며, 사용자가 직접 보유한 정확한 원본 D88·KANJI1 ROM에 적용한다. 25개 Project 분석과 추가 5개 MD의 내용 대조 결과는 [`manifests/analysis-content-reconciliation.json`](../manifests/analysis-content-reconciliation.json)에 별도로 고정했으며, 문서상 역사적 주장과 파일 수준 검증을 섞지 않는다.

## 1. 최종 결론

통합 빌드는 다음 두 delta와 두 개의 사용자 로컬 원본으로 고정한다.

| 대상 | 공개 빌드 입력 | 원본 기준 | 재현 결과 기준 |
|---|---|---|---|
| Disk A | `patches/Valis_Korean_Disk_A_Patch_Ver_1.02.ips` | 414,992 bytes, `7404998ee7e94e14d065a11e55bc26f7f8733202eec6774610a20a6d0b5a1fdf` | 414,992 bytes, `18e274dc730902f90e4d3939ad3ac2853c927d19baf896cee88e5b22321427b8` |
| KANJI1 | `patches/VALIS_KANJI1_ROM_Patch_Ver_1.02.ips` | 131,072 bytes, `f6c1c5022fe5935f6dfa3eb919e51441e75191270b639edcb7938b3bce41f6a3` | 131,072 bytes, `3a4ce60dc4a23d7918a8726b99c2192c9420313bab40c50880eea3a387243f45` |

기준 원본의 SHA-256이 다르면 같은 빌드로 취급하지 않는다. 재현기는 원본을 찾거나 다운로드하지 않으며, 원본을 덮어쓰지도 않는다.

## 2. 전체 완료본 감사 결과

완료본 `Valis 1(1).zip`의 SHA-256은 `49f6f6a9c3a7f2e787200d7b9b12ca8de0dd31315ebbb8c81197fadb5dd3ec3d`이다. 감사기는 ZIP의 최상위 파일 65개를 읽어 해시를 기록했고, 내부 분석문서 30개를 다음처럼 확인했다.

| 감사 항목 | 확인값 |
|---|---:|
| Project 분석문서 | 25개 |
| 추가 MD 분석문서 | 5개 |
| 최종 패치 번들 | Block 1~6 + 엔딩 7개 |
| 최상위 통합 IPS | Disk A 1개 + KANJI1 1개 |
| 최상위 IPS와 재현 스킬 내부 자산 | 두 파일 모두 바이트 일치 |

전체 파일별 해시와 문서·번들 수치는 [`manifests/full-archive-audit.json`](../manifests/full-archive-audit.json)에 고정했다. 이 manifest에는 번역 행이나 글리프 데이터를 복사하지 않고, 파일 식별자·크기·해시·검증 수치만 남겼다. 문서의 주장·정정·폐기 항목을 실제 완료본과 대조한 별도 결과는 [`manifests/analysis-content-reconciliation.json`](../manifests/analysis-content-reconciliation.json)에 있다.

## 3. 완료본의 최종 번들 대조

다음 표는 완료본 내부의 각 최종 번들에서 IPS·JSON·CSV·D88을 직접 확인한 결과다. `IPS bytes`는 해당 번들의 delta 기록 바이트이며, 통합 IPS의 전체 변경 바이트와 단순 합산하지 않는다. 각 번들은 서로 다른 payload 영역과 시점의 산출물이므로 중간 번들을 이어 붙여 최종 이미지를 만들지 않는다.

| 범위 | 문서 행 | 문자/제어 | 실행 범위·종료 | IPS records / bytes | 보고서 검증 |
|---|---:|---:|---|---:|---|
| Block 1 | 678 | 540 / 138 | `0x9680~0x9C99` | 61 / 1,449 | mismatch 0, 선언 영역 밖 0 |
| Block 2 | 1,653 | 1,471 / 182 | `0x9680~0xA4F4`, `0xA4F5=0F` | 132 / 3,536 | mismatch 0, 파일 크기 불변 |
| Block 3 | 984 | 886 / 98 | `0x9680~0x9E6F`, `0x9E70=0F` | 62 / 1,934 | mismatch 0, 파일 크기 불변 |
| Block 4 | 811 | 684 / 127 | `0x9680~0x9D93`, `0x9D94=0F` | 84 / 1,701 | mismatch 0, 파일 크기 불변 |
| Block 5 | 1,381 | 1,162 / 219 | `0x9680~0xA24D`, `0xA24E=0F` | 131 / 2,848 | mismatch 0, 파일 크기 불변 |
| Block 6 | 411 | 351 / 60 | `0x9680~0x99E9`, `0x99EA=0F` | 31 / 817 | mismatch 0, 파일 크기 불변 |
| 엔딩 24세그먼트 | 24 | 540 base-code / 해당 없음 | SUB `0x4B6A~0x59DD`, MAIN `0x0C6A~0x1ADD` | 199 / 2,398 | 0F 24개, tail 불변, quote 검사 OK |

본문 6개 블록의 문서 행은 합계 5,918개이며, 각 보고서의 `decoded_after_matches_*`·`mismatch_count`·`file_size_unchanged`·payload 범위 검증을 확인했다. 엔딩은 본문 블록과 다른 SUB/MAIN 구조이므로 별도 행으로 유지한다.

## 4. 기존 Block 1 계보와 완료본의 관계

기존 Block 1 자료의 513자, 525자, 540자 결과는 서로 다른 시점의 스트림·공백·종료 위치를 가진다. 이들은 분석용 historical lineage로 남기되 통합 빌드 입력으로 승격하지 않는다.

| 과거 계보 | 확인된 차이 | 통합 빌드에서의 처리 |
|---|---|---|
| 2026-05-20 초기 513 | `E8 0B`, `0x9C63=0F`, 129 controls | 실험 계보로만 보존 |
| 2026-05-22 completed/typofix | 513 chars, 138 controls, typofix·glyph 분기 | 최종 IPS와 자동 병합 금지 |
| 2026-05-23 direct157 | 입 모양 157 applied / 49 deferred | 부분 실험으로만 기록 |
| 2026-05-24 525 | 두 블록 재배치, `0x9C7B=0F` | 별도 재배치 계보로만 기록 |
| 2026-05-28 orange | 540 chars, 138 controls, `18 12`, `0x9C99=0F` | Block 1 최종 번들 검증자료로 대조 |
| 완료본 1.02 | Disk A·KANJI1 통합 IPS pair | 재현 빌드의 유일한 공개 delta 기준 |

따라서 `18 12`를 초기 `E8 0B`와 합치거나, 513/525/540 행을 자동으로 재번호화하거나, 과거 ROM의 글리프 슬롯을 1.02 ROM에 자동 이식하지 않는다.

## 4.1 문서 내용 대조 결과

원문 30개는 순서를 고정해 EOF까지 확인했다. Project 문서는 문단과 표를 원래 순서로 추출해 검토했고, MD 원문은 현재 파일의 논리 행 수·SHA-256·끝부분을 확인한 뒤 각 문서의 결론, 정정, 폐기 이력을 완료본 수치와 대조했다. 이 결과는 다음처럼 분리한다.

- 최종 완료본과 직접 맞는 것은 7개 번들의 실행 범위·종료 바이트·행/문자/제어 수·mismatch 및 파일 크기 검증, 통합 Disk IPS의 23,330 변경 바이트, 로고 범위와 겹치는 7,521바이트, KANJI1의 476 슬롯이다.
- Project 1~18의 “한글 출력/패치 미완료”는 각 문서 EOF 시점의 역사적 상태다. 이후 통합 완료본의 상태를 부정하거나 대체하는 최신 판정으로 읽지 않는다.
- Project 19의 3문자 표시, Project 22의 `manual_v2`, Project 23의 525자 재패치, MD의 471→476 글리프 계보는 부분 성공 또는 산출물 계보다. 전체 화면·전체 의미·전체 실행 성공의 증명으로 확장하지 않는다.
- Project 20~21의 자동 토큰 재배치, 513/525/540 계보 자동 병합, MD에 남은 자동 JIS/Unicode 매핑 및 “100%” 문구는 최종 입력으로 승격하지 않는다.
- 실행 화면, 번역 문장 의미, 모든 글리프의 문맥별 표시, 원본 이미지의 배포 권리는 저장소의 정적 파일만으로 확정하지 않는다.

이 절의 판단은 요약을 위한 자동 매핑이 아니라 각 문서에 남은 성공·실패·정정의 위치를 최종 파일 수준 결과와 분리한 것이다.

## 5. 통합 IPS의 독립 검산

| IPS | SHA-256 | records | 기록 바이트 | 범위 |
|---|---|---:|---:|---|
| Disk A 1.02 | `7f14c7b5d6961e234f702aa3e6007944ad3ec8231af225f6296ef3491e1eff53` | 1,282 | 23,330 | `0x316B~0x1DB54` |
| KANJI1 1.02 | `1cb66ed56faf20a29cf0ee860805a14fc7d9132f825c22fa846c3bb81a70bc7c` | 2,026 | 12,621 | `0x2F41~0x1FFFF` |

KANJI1은 32-byte glyph 단위이며 최종 IPS가 건드리는 슬롯은 476개다. IPS 오프셋만으로 한글 음절 이름을 다시 만들지 않는다. Disk A는 D88 컨테이너 크기와 혼합 섹터 구조를 결과에서 다시 파싱한다.

## 6. 통합 빌드에 남긴 파일

| 경로 | 역할 |
|---|---|
| `tools/reproduce_valis1.py` | IPS 파서·적용기, D88 구조 검사, 입력/결과 해시 검사, 전체 완료본 감사 |
| `patches/*.ips` | 완료본에서 확인한 1.02 delta 2개 |
| `manifests/integrated-build.json` | 입력·패치·결과 기준 해시와 배포 제한 |
| `manifests/full-archive-audit.json` | 전체 완료본 파일·문서·최종 번들 감사 결과 |
| `docs/integrated-reproduction-build.md` | 재현 명령과 중지 조건 |
| `tests/test_reproduce_valis1.py` | IPS raw/RLE 적용과 저장소 IPS 통계 테스트 |

Block 1의 계보·충돌 설명은 이 문서에 필요한 비교만 남겼다. 별도 CSV와 분석 압축본은 빌드에 사용되지 않으므로 저장소에서 제거했다.

## 7. 삭제한 불필요 자료

다음 자료는 통합 빌드의 입력도 아니고 현재 manifest의 기준도 아니므로 삭제했다.

- 이전 Block 1 분석만 담은 `evidence/Valis_Block1_정리본_2026-08-24_copyright-safe.zip`
- 위 압축본 전용 `block1_file_manifest.sha256`
- 이전 계보 전용 `block1_lineage_register.csv`
- 이전 충돌 전용 `block1_conflict_register.csv`
- 이전 입력 목록 전용 `block1_source_inventory.csv`

전체 완료본 자체는 저장소에 복사하지 않는다. 원본 D88·ROM·완성 D88/ROM·중첩 번들·전체 번역표·글리프 원천도 공개하지 않는다.

## 8. 최종 검증 경계

저장소에서 자동으로 판정하는 것은 파일 수준 재현이다.

1. 정확한 원본 SHA-256 확인.
2. IPS header/EOF/record/range 확인.
3. 고정 크기 적용 확인.
4. Disk A D88 header·80 tracks·혼합 sector·payload 구조 확인.
5. 결과 SHA-256과 변경 바이트/슬롯 수 확인.

QUASI88 부팅, 화면 글리프, 발화 입 모양, 장면 전환, 엔딩·게임오버·스태프롤 실제 화면은 이 저장소가 자동으로 확정하지 않는다. 해당 실행 gate를 통과하지 않은 결과를 문서의 수치만으로 기능 완료라고 부르지 않는다.

## 9. 최종 상태

파일 수준에서는 통합 완료본의 1.02 IPS·해시·번들 수치를 재검산했고, 내용 수준에서는 30개 분석문서의 역사적 주장·부분 성공·폐기 항목을 별도 manifest로 분리했다. 따라서 저장소는 재빌드에 필요한 공개 파일만 제공하며, “문서 수치가 맞다”는 것과 “에뮬레이터 화면까지 검증됐다”는 것을 같은 완료 상태로 부르지 않는다. 최종 재현 절차는 `docs/integrated-reproduction-build.md`, 기계 검산 결과는 `manifests/full-archive-audit.json`, 내용 대조 결과는 `manifests/analysis-content-reconciliation.json`, 실행 코드는 `tools/reproduce_valis1.py`를 기준으로 한다.
