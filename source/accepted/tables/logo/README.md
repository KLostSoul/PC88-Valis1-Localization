# 타이틀 로고 원천

`raw-changes.csv`는 완료본 ZIP의 로고 분석/편집 키트가 기록한 명시적
`ram_addr → raw_file_offset` 변경표다. 7,595행 모두 `old_raw`가 사용자
제공 원본 D88과 일치하는 것을 확인했다. `source-map.csv`, 세 call map,
`ram-to-raw-map.csv`는 05CE/061F 디코더와 5C/5D/5E plane의 주소·소비량을
검증하는 분석 자료다.

PNG/PSD/완료 D88 및 생성된 source binary는 빌드 입력에 포함하지 않는다.
직렬화기는 변경표의 raw old/new만 사용하고, sector header와 미선언 payload는
건드리지 않는다.
