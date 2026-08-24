# Accepted source boundary

This directory contains only reviewed, literal source data. Text sources keep
the original text and Korean translation in separate fields, alongside the
explicit token/control-byte sequence, address ranges, and D88 raw-byte table.
The event text tables, the Korean verification tables, and the ending 24-row
text table are separate files; no one is regenerated from another.
The builder consumes those tables and never regenerates them from a completed
image.

A source file may be placed here only after:

1. the corresponding original D88/ROM bytes have been inspected;
2. the project document and exact table/row/page location are recorded;
3. token/control boundaries, terminators, lengths, and physical storage are written literally;
4. every component table is updated to the reviewed final release byte value;
5. an independent review marks the manifest component `accepted`.

The builder fails if the manifest is not accepted, an accepted path is
missing, a source row is not guarded by the supplied original byte, a literal
span preimage does not match the preceding component state, or the final hash
does not equal the release baseline. A completed binary, IPS, PNG/BMP/PSD, or
project-source document is never a build input.
