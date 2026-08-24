# 무겐전사 바리스 1 — 미러형 재현 빌드 사양

이 한글패치 저장소의 기본 사양은 한국어로 해석합니다. 원본 D88/ROM 검증, 분석 근거와 확정 소스의 분리, 이벤트 1~6·게임오버·엔딩·로고·ERROR 07·KANJI1의 직접 바이너리 기록, 재파싱·해시·10개 통합 테스트가 필수입니다. 완료본은 로컬 비교 전용이고 어셈블러·IPS·자동 매핑은 빌드 경로에 없습니다.

상세 한국어 기준은 [직접 바이너리 재현 빌드](ko/direct-binary-build.md), [근거·소스 대응표](ko/evidence-and-source-map.md), [검증 절차](ko/reproducibility.md)입니다. 아래 영문 사양은 부가 참고본입니다.

---

## 1. 목적과 경계

이 저장소의 목적은 완료본을 복사하는 것이 아니라, 사용자가 제공한 원본 D88/ROM을 입력으로 받아 문서와 바이너리 분석에서 확정한 소스 데이터를 다시 조립하여 동일한 구조의 결과물을 만드는 것이다.

완료본 ZIP은 다음 용도로만 사용한다.

- 분석자가 문서의 주장과 결과 바이트를 대조하는 비교 오라클
- 주소·길이·종결자·sector 범위의 독립 검증 대상
- 재빌드 후 차이 보고의 비교 대상

완료본 ZIP, 완료 D88/ROM, IPS, 완료본에서 추출한 BMP/PNG, 완료본의 payload를 빌드 입력으로 사용하지 않는다. `build` 명령에는 reference 경로를 전달할 수 없고, `compare` 명령만 별도 reference 경로를 허용한다.

자동 문서 추출, 자동 토큰 매핑, 자동 주소 추정, 완료본 바이트의 소스 승격, correction 값의 자동 선택은 금지한다. 스크립트는 사람이 확정한 리터럴 행을 검증하고 직렬화할 뿐이다.

## 2. 저장소 구조

```text
valis-reproduction-build/
├── analysis/
│   ├── project-documents/           # 문서별 수동 분석 노트와 인용 위치
│   ├── evidence/                    # 바이트 단위 관찰·계산·대조 기록
│   ├── decisions/                   # 충돌 해결 또는 빌드 차단 결정
│   ├── document-index.json          # 파일명/해시/범위 목록, source 행 생성 금지
│   └── reference-policy.md          # 완료본 격리 규칙
├── source/
│   ├── media/
│   │   ├── d88-layout.json          # 원본 D88 track/sector 구조의 명시적 표
│   │   └── rom-layout.json          # 원본 KANJI1 geometry/hash/slot 규칙
│   ├── tokens/
│   │   ├── control-token-registry.json
│   │   └── character-token-registry.csv
│   ├── events/
│   │   ├── block-1/records.jsonl
│   │   ├── block-2/records.jsonl
│   │   ├── block-3/records.jsonl
│   │   ├── block-4/records.jsonl
│   │   ├── block-5/records.jsonl
│   │   └── block-6/records.jsonl
│   ├── gameover/
│   │   ├── fixed-01-15/records.jsonl
│   │   └── scroll-01-35/records.jsonl
│   ├── ending/
│   │   └── segments-01-24/records.jsonl
│   ├── kanji/
│   │   ├── assignments.csv
│   │   └── glyph-sources.manifest.json
│   ├── logo/
│   │   ├── source-map.json
│   │   └── relocation-map.json
│   ├── asm/                         # 디버거 관찰 기록; 빌드 입력 아님
│   │   ├── source/*.asm             # 역어셈블 listing
│   │   └── symbols.json
│   └── source-manifest.json         # 모든 행의 승인/차단 상태
├── tools/
│   ├── valis_rebuild/
│   │   ├── d88.py                   # D88 구조 파서/sector-safe writer
│   │   ├── codec.py                 # 명시된 reverse stream codec
│   │   ├── source.py                # literal source validator
│   │   ├── serializer.py            # accepted source → D88/ROM
│   │   ├── verifier.py              # old/new/round-trip/hash 검증
│   │   └── cli.py
│   └── commands/                    # 단계별 얇은 진입점
├── tests/
│   ├── unit/
│   ├── component/
│   └── integration/
├── logs/                            # 로컬 생성, 커밋 금지
└── build/                           # 로컬 생성 D88/ROM, 커밋 금지
```

`analysis/quarantine/auto_extract_*/`는 이전 잘못된 자동 추출 산출물의 격리 보관소일 뿐이며, 위 source graph와 import 경로에 포함하지 않는다.

## 3. 수동 분석에서 빌드 소스로 넘어가는 계약

각 리터럴 source 행은 다음 필드를 모두 가진다.

```json
{
  "id": "event-01.row-0009",
  "component": "event_block_1",
  "ordinal": 9,
  "kind": "character",
  "text": "비",
  "token_bytes": "30 3C",
  "old_bytes": "30 3C",
  "runtime": {
    "space": "main",
    "address_start": "0x969F",
    "address_end": "0x96A0"
  },
  "storage": {
    "kind": "d88_file_data",
    "offset_start": "0x1A2A0",
    "offset_end": "0x1A2A1"
  },
  "source": {
    "documents": ["Valis Project N.docx"],
    "location": "table 1 / row 9",
    "observation": "document bytes and original D88 read agree"
  },
  "review": {
    "status": "confirmed",
    "reviewer": "",
    "date": ""
  }
}
```

위 예시는 필드 계약만 보여주는 예시이며 실제 accepted source가 아니다. `old_bytes`가 없거나, 주소 계층이 섞였거나, 문서 위치가 없거나, review가 confirmed가 아니면 serializer가 거부한다.

## 4. 주소와 저장 계층

주소를 하나의 숫자로 취급하지 않는다. 모든 행은 다음 중 하나 이상의 계층을 명시한다.

| 계층 | 의미 | 검증 방법 |
|---|---|---|
| `runtime_main` | MAIN CPU의 실행/스트림 주소 | 문서의 실행 위치와 원본 메모리 관찰 |
| `runtime_sub` | SUB CPU의 스트림 주소 | SUB 주소 범위와 세그먼트 경계 대조 |
| `d88_file_header` | D88 sector 16바이트 헤더 | track pointer와 CHRN으로 확인 |
| `d88_file_data` | sector payload의 절대 파일 오프셋 | 헤더 뒤 payload 범위로 확인 |
| `flat_payload` | 헤더를 제거한 연속 payload 좌표 | 읽기 전용 분석용, 쓰기 주소로 직접 사용 금지 |
| `rom_offset` | KANJI1 실제 ROM 위치 | slot×0x20 및 원본 ROM read로 확인 |

runtime 주소에서 D88 offset으로 이동하는 식은 전역 추정식이 아니라 component별 명시적 map으로 기록한다. 한 component 안에서도 0x400 block별 base, reverse 순서, correction, sector 분할을 각각 적는다.

## 5. 컴포넌트별 설계

### 5.1 원본 D88/ROM

`export-original`은 원본 D88의 header, track pointer, CHRN, sector length, data offset, payload hash만 읽어 JSON으로 기록한다. 이 명령은 번역 행이나 매핑 행을 만들지 않는다.

ROM은 크기, SHA-256, glyph slot 크기, 원본 slot bytes를 기록한다. 원본 ROM은 커밋하지 않고, 사용자가 명령행으로 제공한다.

### 5.2 본편 블록 1~6

각 block은 다음을 별도 기록한다.

- 문서의 작업순번
- 문자/제어/종결자의 종류
- 원문·번역문과 literal token bytes
- 각 행 전후 runtime 주소
- 각 행의 원본 D88 data offset과 old bytes
- 0x400 단위 reverse 저장 block 및 correction
- 빈 공간·padding·다음 stream 경계

행 길이가 바뀌면 이후 행 주소, stream 길이, physical write 범위, 여유 공간을 다시 계산한다. 계산 결과가 문서 또는 원본 read와 닫히지 않으면 block 전체를 `blocked`로 둔다.

### 5.3 게임오버 고정 1~15 / 스크롤 1~35

고정 세그먼트와 스크롤 블록은 서로 다른 source schema를 사용한다. 고정 세그먼트는 본문과 원본 `0F` 종결자를 분리하고, 스크롤은 각 block의 20 token-pair body와 marker를 별도로 기록한다.

marker를 body에 자동 포함하거나 제외하지 않는다. 문서의 marker 위치와 원본 byte read가 모두 일치해야 accepted 상태가 된다.

### 5.4 엔딩 1~24

24개 세그먼트 각각에 대해 segment 번호, 본문 bytes, `0F`, runtime 범위, sector data 범위, correction 구간, allocation tail 정책을 기록한다. 엔딩 전체를 하나의 완성 binary로 저장하지 않는다.

길이 변경은 다음 값을 함께 재계산한다.

- segment 이후 runtime address
- 다음 segment 경계
- reverse raw position
- sector 경계 및 변경 범위
- 남은 공간
- 종료 후 실행 흐름/branch target

단 하나라도 불일치하면 엔딩 serializer는 중지한다.

### 5.5 문자·번역·제어 토큰

문자표와 제어표를 분리한다. 문자 토큰처럼 보인다는 이유로 제어 토큰을 문자로 변환하지 않는다. 의미가 확정되지 않은 토큰은 `unknown`으로 남기고 build source에 넣지 않는다.

### 5.6 KANJI1

문자 assignment에는 Unicode, token pair, KANJI slot, ROM offset, old glyph bytes, new glyph bytes, glyph source provenance를 모두 적는다. Unicode 순서나 token 값으로 slot을 자동 계산하지 않는다.

glyph source는 사용자가 별도로 제공한 local source만 허용한다. 완료본에서 추출한 BMP/PNG를 빌드 입력으로 사용하지 않는다.

### 5.7 로고와 ASM

로고는 RAM range, encoder entry, source bitmap, RAM→D88 reverse map, 주소 보정 결과가 모두 닫혀야 빌드 가능하다. 하나라도 없으면 원본 보존으로 처리한다.

디버거 관찰은 실제로 확인된 entrypoint, branch target, 사용 가능한 free space, 실행 전후 bytes를 기록한다. 관찰 listing은 조립하지 않으며 추측성 stub이나 자동 hook은 실제 게임 이미지에 적용하지 않는다.

## 6. serializer 규칙

1. 사용자가 제공한 원본 D88/ROM을 메모리로 읽는다.
2. `source-manifest.json`이 모든 required component를 `confirmed`로 표시하는지 확인한다.
3. source 행을 ordinal/address 순서로 읽되, 정렬·추정·중복 제거를 하지 않는다.
4. 각 행의 `old_bytes`가 원본 입력과 같은지 확인한다.
5. 명시된 physical offset에만 쓴다. sector header/gap/미선언 영역에는 쓸 수 없다.
6. duplicate offset, overlap, length overflow, branch overflow, correction coverage 누락은 즉시 실패한다.
7. component별 재디코드 결과가 literal source와 일치하는지 확인한다.
8. D88/ROM output과 로그를 local build 디렉터리에 생성한다.

IPS를 생성하거나 적용하는 단계는 없다. IPS는 비교 자료일 뿐 재현 빌드 산출물이 아니다.

## 7. 단계별 명령

```sh
# 0. 수동 근거/accepted source만 검사 — 행을 만들지 않음
python -m tools.valis_rebuild source-lint

# 0a. 원문/번역/검증표 JSONL의 고정 행 수와 provenance 검사
python -m tools.valis_rebuild text-lint

# 1. 원본 D88 구조만 export — 번역/매핑 생성 없음
python -m tools.valis_rebuild export-original \
  --d88 /path/to/original.d88 --out build/export-original

# 2. 원본 D88 기반 바이트 재직렬화
python -m tools.valis_rebuild build-d88 \
  --d88 /path/to/original.d88 --out build/disk

# 3. 원본 KANJI1 기반 글리프 재직렬화
python -m tools.valis_rebuild build-rom \
  --rom /path/to/original/KANJI1.ROM --out build/rom

# 4. 구조·old/new·재디코드·hash 검증
python -m tools.valis_rebuild verify \
  --d88 build/disk/valis.d88 --rom build/rom/KANJI1.ROM

# 5. 완료본과 로컬 비교 — build 입력으로 역류하지 않음
python -m tools.valis_rebuild compare \
  --built build/disk/valis.d88 --reference /local/reference/result.d88
```

실제 CLI는 `source-lint`, `text-lint`, `export-original`, `build-d88`, `build-rom`, `build`, `verify`, `compare`를 별도 command로 노출한다. `build-d88`와 `build-rom`은 source acceptance가 닫히면 실행되고, 그 전에는 실패해야 한다. `compare --fail-on-diff`는 exact-release 확인용이다.

## 8. 검증 로그

각 build는 `repro-log.json`을 생성한다.

```json
{
  "schema": "valis-reproduction-log/v1",
  "command_line": "...",
  "input_hashes": {"original_d88": "...", "original_kanji1": "..."},
  "source_tree_hash": "...",
  "accepted_fact_ids": ["..."],
  "component_reports": [
    {"component": "event_block_1", "writes": 0, "roundtrip": "OK"}
  ],
  "output_hashes": {"d88": "...", "rom": "..."},
  "reference_comparison": null,
  "status": "OK"
}
```

reference comparison 결과는 이 로그에 선택적으로 기록할 수 있지만, reference bytes나 reference-derived source를 기록하지 않는다.

## 9. GitHub 반영 기준

허용:

- Python 소스와 디버거 관찰 listing
- 사람이 작성한 JSON/JSONL/CSV/YAML 원천표
- 문서·테스트·검증 로그 형식
- 원본 hash와 구조 메타데이터

금지:

- D88/ROM/IPS/ZIP
- 완료본 payload
- 완료본에서 추출한 BMP/PNG/TXT binary dump
- `build/`, `logs/`, local glyph directory
- 자동 추출·자동 매핑 산출물

GitHub에 push하기 전 `release-check`가 금지 확장자, reference 경로, generated marker, unaccepted source를 검사한다. 하나라도 발견되면 push하지 않는다.
