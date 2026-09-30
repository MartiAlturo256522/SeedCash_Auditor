---
name: seedcash-signer
description: >
  Audit SeedCash signing: sighash allowlist, BIP-143 preimage, Schnorr
  tag, redeem binding, derivation binding, and signed-PSBT reassembly.
  Use when reviewing psbt_signer.py, FORKID, Schnorr, or /seedcash-signer.
---

# Signer lane

Read `agents/signer.md` and the `signer` headings in `brain/invariants.md`. Follow `brain/disclosure.md`. The target tree is the operator's `target_root`, or the `app_path` in `brain/pin.md` when they did not name one.

Re-read the functions. A row marked `closed` is re-checked, not skipped.
