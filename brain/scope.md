# Scope

The auditor reviews the SeedCash application tree and the seedcash-os tree the operator passes in. The defaults are the paths in `brain/pin.md`.

In scope:

- Signing, PSBT parsing, CashTokens, the QR and UR channel, seed derivation, the review screens, and the Buildroot image sources.
- Design choices that make a hostile coordinator, a hostile QR, or a dishonest display able to move funds, hide a field the signature commits to, or break the air gap.
- Regressions of checks that `brain/invariants.md` marks `closed`.

Out of scope:

- Editing the SeedCash or SeedSigner trees. Findings are written here.
- Filing an upstream issue without the confirm step in `brain/issue-policy.md`.
- Triggering transactions, command payloads, and reproduction procedures. The writing rules live in `brain/disclosure.md`.
- Hardware fault injection, decapping, and physical glitching.
- The dirty local SeedSigner checkout at `/Users/martialturorequena/seedsigner-project/seedsigner`. That tree is an older dev branch with local emulator edits. The baseline is the tag in `brain/pin.md`, read from a clean tree.
- Older SeedCash snapshots (`image_2.0.1`, `~/seedcash`, `~/Desktop/emulator/seedcash`) unless the operator passes that path and the report is titled with the commit that was actually read.

OS findings are reported in the audit. They are not filed against `issue_repo` unless the operator names an OS repository.
