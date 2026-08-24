# Reproduction build design v2

The repository is split into three non-overlapping domains.

| Domain | Contents | May feed build? |
|---|---|---:|
| `analysis/` | manually written evidence ledger and review notes | only after acceptance |
| `source/accepted/` | literal, reviewed bytes/tokens/maps with provenance | yes |
| local reference workspace | completed ZIP, completed D88/ROM, IPS, extracted images | no |

## Required flow

```text
original D88/ROM ──read-only inspect──► evidence ledger
project documents ──manual cross-check─► evidence ledger
ledger + original bytes ──independent review──► source/accepted
source/accepted ──strict lint──► literal byte serializer
literal byte serializer ──round-trip verify──► local D88/ROM
local result ──optional comparison──► local reference only
```

The completed archive is an oracle for checking a hypothesis, never a producer of source rows. The builder has no code path that opens a ZIP, IPS, completed image, or reference directory.

## Source row contract

Every accepted literal row must contain:

```json
{
  "id": "ending.seg01.byte000",
  "component": "ending_1_24",
  "runtime_address": "0x4B6A",
  "d88_data_offset": "0x5A25",
  "old_value": "0x00",
  "new_value": "0x00",
  "token": "hangul_base_code",
  "terminator": false,
  "source_documents": ["Valis Project N.docx"],
  "source_location": "table 1, row 42",
  "literal_observation": "document row and original-byte read agree",
  "review": {"status": "confirmed", "reviewer": "", "date": ""}
}
```

The example is a schema illustration, not accepted project data. Missing `old_value`, duplicate offsets, ambiguous maps, unresolved conflicts, and inferred token values are hard errors.

## Stages

- `source-lint`: validate the ledger and accepted-source provenance; never generate rows.
- `export-original`: record read-only D88 sector topology and hashes from a user-supplied original image.
- Debugger listings are observations only; literal old/new byte tables are the only disk write source.
- `build`: require an accepted manifest, then serialize literal source bytes into the original image.
- `verify`: parse the result, check old/new guards, address maps, length/terminator closure, and deterministic hashes.
- `compare`: optional local-only byte comparison with a reference result; its bytes are never imported.
