# Analysis layer — manual evidence only

This directory is the boundary between investigation and build source.

`evidence-ledger.json` is a manually maintained ledger. Every fact that may become build input must identify the project document, section/table/row or binary location, the literal observed bytes, the address layer, and an independent review state.

The accepted source tree contains explicit original-text/Korean-translation
tables transcribed from the completion archive's analysis material. A parser
may help validate a fixed table transcription or inspect a user-supplied
original image, but it may not create an accepted source row, infer a token
mapping, select a correction constant, or promote a completed output into a
build input.

The previous automatic extraction attempt is quarantined under `analysis/quarantine/` and is ignored by Git. It is not part of the new build graph.
