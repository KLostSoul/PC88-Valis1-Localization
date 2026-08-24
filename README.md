# PC-88 Valis 1 Localization

PC-8801판 《몽환전사 바리스 1》 한글화의 분석 기록과 재현 가능한 작업 자료를 관리하는 저장소다.

## 현재 저장 범위

현재는 Block 1 자료의 계보·충돌·실패 사유·파일 수준 검증을 정리해 기록한다. Block 1의 513·525·540자 패치는 서로 다른 계보이므로 자동 병합하지 않는다.

- 새 통합 분석: [`docs/valis-block1-repository-analysis.md`](docs/valis-block1-repository-analysis.md)
- Word 분석문서: [`docs/Valis_Block_1_Repository_정리분석.docx`](docs/Valis_Block_1_Repository_정리분석.docx)
- 배포 범위: [`docs/valis-block1-distribution-scope.md`](docs/valis-block1-distribution-scope.md)
- 저작권 보수형 Block 1 분석 압축본: [`evidence/Valis_Block1_정리본_2026-08-24_copyright-safe.zip`](evidence/Valis_Block1_정리본_2026-08-24_copyright-safe.zip)
- 계보 등록부: [`manifests/block1_lineage_register.csv`](manifests/block1_lineage_register.csv)
- 충돌 등록부: [`manifests/block1_conflict_register.csv`](manifests/block1_conflict_register.csv)
- 입력 재배포 범위표: [`manifests/block1_source_inventory.csv`](manifests/block1_source_inventory.csv)
- 압축본 내부 SHA-256 목록: [`manifests/block1_file_manifest.sha256`](manifests/block1_file_manifest.sha256)

## 보관 원칙

- 원본 파일은 바이트를 변경하지 않고 계보별로 분리한다.
- D88·ROM·IPS·manifest·실행 결과는 동일 release unit인지 확인하기 전까지 하나의 최종본으로 부르지 않는다.
- 문서 생성·roundtrip·IPS 파싱과 실제 에뮬레이터 화면 검증을 별도 gate로 관리한다.
- 임시 추출물과 렌더링 결과는 저장소에 넣지 않는다.
- 원본 게임 이미지·ROM·D88·패치 패키지·전체 번역/글리프 데이터는 저장소와 공개 압축본에서 제외한다.

이 저장소의 구조와 문서화 방식은 [PC88-Mirrors-Localization](https://github.com/KLostSoul/PC88-Mirrors-Localization)의 소스/문서/검증자료 분리 원칙을 참고했다. 다만 Mirrors 프로젝트의 VWF·토큰 규격을 Valis 1에 자동 적용하지 않는다.

실수로 원본·파생 게임 데이터를 추가하지 않도록 `.gitignore`에도 D88/ROM/IPS와 원본 패키지 경로를 제외하는 규칙을 둔다.

## 현재 상태

Block 1 자료 정리·분석·manifest 작성은 완료했다. 공개본은 분석문서와 메타데이터만 포함하며, 실제 게임에서 모든 문장·글리프·입 모양·장면 전환이 검증된 단일 배포본은 아직 없다.
