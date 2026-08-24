# KANJI1 원천

`assignments.csv`는 476개 행의 명시적인 음절/토큰/슬롯/ROM 오프셋 표다.
`../kanji/glyphs/*.txt`는 각 행의 16×16 `■/□` 1bpp 원천이다.

빌더는 Unicode나 토큰에서 슬롯을 계산하지 않는다. 표에 적힌 `slot`과
`rom_offset`의 일치만 검증하고, 표가 가리키는 TXT를 정확히 32바이트로
직렬화한다.
