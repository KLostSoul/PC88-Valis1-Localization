# PC-88 Valis 1 Localization

PC-8801판 《몽환전사 바리스 1》 한글화의 통합 재현 빌드와 분석 기록을 관리하는 저장소다.

## 현재 저장 범위

전체 완료본 ZIP을 분석해 확인한 현행 통합 기준은 사용자가 직접 확보한 원본 Disk A/KANJI1에 1.02 IPS 두 개를 적용하는 방식이다. Block 1의 513·525·540자 중간 계보를 자동 병합하지 않고, 완료본의 통합 delta만 재현 빌드 입력으로 사용한다.

- 재현 빌드 절차: [`docs/integrated-reproduction-build.md`](docs/integrated-reproduction-build.md)
- Python 빌더/검증기: [`tools/reproduce_valis1.py`](tools/reproduce_valis1.py)
- 통합 빌드 manifest: [`manifests/integrated-build.json`](manifests/integrated-build.json)
- 전체 완료본 감사 manifest: [`manifests/full-archive-audit.json`](manifests/full-archive-audit.json)
- 30개 분석문서 내용 대조 manifest: [`manifests/analysis-content-reconciliation.json`](manifests/analysis-content-reconciliation.json)

## 보관 원칙

- 원본 파일은 저장소에 넣지 않고, 바이트를 변경하지 않은 상태로 사용자 로컬 입력으로만 사용한다.
- D88·ROM·IPS·manifest·실행 결과는 동일 release unit인지 확인한 뒤에만 통합 빌드로 부른다.
- 문서 생성·roundtrip·IPS 파싱과 실제 에뮬레이터 화면 검증을 별도 gate로 관리한다.
- 임시 추출물과 렌더링 결과는 저장소에 넣지 않는다.
- 원본 게임 이미지·완성 D88/ROM·전체 패치 번들·전체 번역/글리프 데이터는 저장소에서 제외한다. 배포하는 것은 IPS delta와 재현 코드뿐이다.

이 저장소의 구조와 문서화 방식은 [PC88-Mirrors-Localization](https://github.com/KLostSoul/PC88-Mirrors-Localization)의 소스/문서/검증자료 분리 원칙을 참고했다. 다만 Mirrors 프로젝트의 VWF·토큰 규격을 Valis 1에 자동 적용하지 않는다.

실수로 원본·파생 게임 데이터를 추가하지 않도록 `.gitignore`에도 D88/ROM/IPS와 원본 패키지 경로를 제외하는 규칙을 둔다.

## 빠른 실행

```bash
python3 tools/reproduce_valis1.py inspect-ips disk patches/Valis_Korean_Disk_A_Patch_Ver_1.02.ips
python3 tools/reproduce_valis1.py inspect-ips kanji patches/VALIS_KANJI1_ROM_Patch_Ver_1.02.ips
python3 -m unittest discover -s tests -v
```

실제 빌드는 [`docs/integrated-reproduction-build.md`](docs/integrated-reproduction-build.md)의 원본 입력 해시와 명령을 따른다. 원본 해시가 다르면 도구가 중지하며, 원본을 자동으로 찾거나 다운로드하지 않는다.

현재 상태: 통합 IPS·Python 재현·전체 완료본 파일 감사·30개 분석문서 내용 대조 결과를 저장소에 고정했고, QUASI88의 실제 화면/장면 전환 검증은 사용자의 로컬 실행 gate로 분리했다. 정적 완료본 수치와 런타임 완료를 같은 의미로 취급하지 않는다.
