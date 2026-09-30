---
name: seedcash-custody
description: >
  Audit SeedCash seed custody: BIP-39 NFKD, xpub checksums, RAM-only
  seed, zeroization, and entropy source. Use when reviewing bip39.py,
  seed.py, passphrases, or /seedcash-custody.
---

# Custody lane

Read `agents/seed-custody.md` and the `custody` headings in `brain/invariants.md`. Follow `brain/disclosure.md`.

`INV-MEMORY-ZEROIZE` is not issue-ready unless the invariant says `file_ready: yes`.
