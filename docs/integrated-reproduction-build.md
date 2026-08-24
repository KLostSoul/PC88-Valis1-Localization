# 통합 재현 빌드

이 저장소의 통합 빌드는 제공된 전체 완료본에서 확인한 1.02 IPS 두 개를 기준으로 한다.
원본 게임 이미지와 KANJI1 ROM은 공개하지 않는다. 사용자가 합법적으로 보유한 원본을 직접 경로로 넣으면 Python 도구가 입력 해시, IPS 구조, 결과 해시, D88 혼합 섹터 구조를 모두 검사한다.

## 빌드 입력

| 입력 | 저장소 파일 | 기준 |
|---|---|---|
| Disk A 원본 | 사용자가 직접 준비 | 414,992 bytes, SHA-256 `7404998ee7e94e14d065a11e55bc26f7f8733202eec6774610a20a6d0b5a1fdf` |
| KANJI1 원본 | 사용자가 직접 준비 | 131,072 bytes, SHA-256 `f6c1c5022fe5935f6dfa3eb919e51441e75191270b639edcb7938b3bce41f6a3` |
| Disk A delta | `patches/Valis_Korean_Disk_A_Patch_Ver_1.02.ips` | SHA-256 `7f14c7b5d6961e234f702aa3e6007944ad3ec8231af225f6296ef3491e1eff53` |
| KANJI1 delta | `patches/VALIS_KANJI1_ROM_Patch_Ver_1.02.ips` | SHA-256 `1cb66ed56faf20a29cf0ee860805a14fc7d9132f825c22fa846c3bb81a70bc7c` |

최종 결과 기준은 Disk A `18e274dc730902f90e4d3939ad3ac2853c927d19baf896cee88e5b22321427b8`, KANJI1 `3a4ce60dc4a23d7918a8726b99c2192c9420313bab40c50880eea3a387243f45`이다. 원본 해시가 다르면 도구는 기본적으로 중지한다.

## 실행

저장소 루트에서 실행한다. 원본은 별도 위치에 두며 `build/`에 복사하지 않아도 된다.

```bash
python3 tools/reproduce_valis1.py inspect-ips disk patches/Valis_Korean_Disk_A_Patch_Ver_1.02.ips
python3 tools/reproduce_valis1.py inspect-ips kanji patches/VALIS_KANJI1_ROM_Patch_Ver_1.02.ips

python3 tools/reproduce_valis1.py build \
  --disk-base /path/to/legally-obtained/Valis_Disk_A_original.d88 \
  --kanji-base /path/to/legally-obtained/KANJI1_original.ROM \
  --output-dir build/valis1-1.02
```

성공하면 `build/valis1-1.02/`에 다음 세 파일이 생긴다.

```text
Valis_Disk_A_reproduced.d88
KANJI1_Valis_reproduced.ROM
build-report.json
```

도구는 D88 파일을 삽입·삭제하거나 원본을 덮어쓰지 않는다. Disk A는 헤더 0x2B0, 80개 트랙, 트랙 0~1의 256-byte×16-sector와 트랙 2~79의 1024-byte×5-sector 혼합 구조, 407,552-byte payload를 유지해야 한다. KANJI1은 32-byte 단위의 16×16 1bpp glyph ROM이며 결과는 476개 슬롯, 12,621개 변경 바이트 기준을 검사한다.

## 전체 완료본과의 관계

`Valis 1(1).zip`은 Block 1~6, 엔딩, 로고, Gameover, KANJIROM 자료와 분석 산출물을 포함한 작업 아카이브다. 내부의 블록별 `FINAL` 표기는 각 시점의 번들 이름이지, 서로 다른 중간 D88을 다시 이어 붙이라는 지시가 아니다. 통합 빌드는 아카이브 최상위에 포함된 1.02 IPS 두 개를 사용한다.

`tools/reproduce_valis1.py audit-source`는 이 ZIP의 최상위 파일 65개를 읽어 해시를 기록하고, 25개 Project DOCX와 5개 MD 분석 DOCX를 모두 확인하며, Block 1~6 및 엔딩의 최종 패치 번들 7개에서 IPS/JSON/CSV/D88 구성과 보고서의 수치 검증 필드를 대조한다. 감사 결과는 [`manifests/full-archive-audit.json`](../manifests/full-archive-audit.json)에 저장한다. 이 감사는 번역 문장이나 글리프를 자동 매핑하지 않는다. 30개 분석문서의 역사적 주장·부분 성공·폐기 항목을 완료본과 내용 수준에서 분리한 결과는 [`manifests/analysis-content-reconciliation.json`](../manifests/analysis-content-reconciliation.json)에 저장한다.

내용 대조 manifest는 문서의 모든 수치를 새 번역 데이터로 재생성했다는 뜻이 아니다. 완료본에서 독립적으로 확인되는 파일 수준 사실과, 각 문서 EOF 시점의 탐색·실패·부분 성공 기록을 분리해 재빌드 입력으로 승격할 항목만 고정한다.

```bash
python3 tools/reproduce_valis1.py audit-source \
  --source-zip /path/to/Valis\ 1\(1\).zip \
  --output manifests/full-archive-audit.json
```

확인한 소스 아카이브 SHA-256:

```text
49f6f6a9c3a7f2e787200d7b9b12ca8de0dd31315ebbb8c81197fadb5dd3ec3d  Valis 1(1).zip
```

블록별 원본·완성 D88/ROM·전체 번역표·글리프 원천·PNG·DOCX는 재현 도구의 공개 입력으로 복제하지 않는다. 공개 저장소는 IPS delta, 직접 작성한 Python 검증기, 해시/범위 manifest와 분석 원칙만 제공한다. 실제 부팅·화면·장면 전환 검증은 IPS 적용 후 사용자의 QUASI88 환경에서 별도 gate로 수행한다.

## 검증 실패를 숨기지 않는 규칙

- 원본 SHA-256 불일치: 빌드 중지.
- IPS의 헤더·EOF·레코드·범위 불일치: 빌드 중지.
- D88 구조나 파일 크기 변화: 빌드 중지.
- 결과 해시 불일치: 성공으로 기록하지 않음.
- `--allow-unknown`은 탐색용 검사만 허용하며 release pass로 간주하지 않음.

이 절차는 서로 다른 513/525/540자 Block 1 계보를 자동 병합하지 않는다. 통합 빌드는 완료본에서 확정된 1.02 배포 delta를 하나의 재현 가능한 입력 세트로 고정하는 작업이다.
