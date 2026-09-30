# Signer lane

Own the `signer` rows in `brain/invariants.md`. Read the files named for this lane in `brain/lanes.json` at the target root.

Re-read every signer invariant, including `closed`. A closed check that the code no longer implements is a regression. Hunt for a new break in sighash, redeem binding, key derivation, and PSBT reassembly.

Write findings with the fields in `schemas/finding.schema.json`. Evidence is a short quote of the check. Stop at four findings; put the rest in `dropped`.
