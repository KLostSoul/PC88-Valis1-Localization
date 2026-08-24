# Layered architecture

## Analysis layer

`analysis/evidence-ledger.json` records what was observed, where it was observed, and who reviewed it. A fact is not buildable merely because a script can parse it.

## Accepted source layer

`source/accepted/` contains literal bytes and maps only after manual review. Every source row must retain provenance to a Project document and an original D88/ROM location. Generated output, guessed mappings, and reference-only data are rejected.

## Serialization layer

The D88 parser understands track pointers, sector headers, payload lengths, and physical file-data offsets. It never rewrites sector headers or gaps. The low-level reverse codec is available for explicitly supplied maps; it does not discover maps.

## Build layer

The CLI calls the source gate before opening a build input. If the ledger,
accepted manifest, or fixed text-source index is invalid, the command stops.
Each accepted component is serialized only from its explicit source table.

The current implementation has deterministic serializers for gameover,
ending, ERROR 07, event blocks 1–6, logo raw tables, hold bytes, and KANJI1.
`text-lint` is called by the build gate so the original/translation source
tables cannot silently disappear from a build revision.

## Verification layer

Verification checks structure, old-value guards, duplicate destinations,
terminators, lengths, round trips, and deterministic hashes. Reference
comparison is a separate read-only operation; `compare --fail-on-diff` is the
exact-release gate and is expected to fail while the documented baseline
conflicts remain.
