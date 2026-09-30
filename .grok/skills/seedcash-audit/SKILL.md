---
name: seedcash-audit
description: >
  Run the SeedCash security audit: pin the tree, dispatch the signer,
  CashToken, QR, custody, WYSIWYS, OS, and SeedSigner-delta lanes, then
  keep only skeptic-confirmed findings. Use when the user says audit
  SeedCash, revisar SeedCash, full security review, or /seedcash-audit.
---

# SeedCash audit

Read `brain/protocol.md`, `brain/scope.md`, and `brain/disclosure.md`. Then run the workflow `audit-seedcash` with `auditor_root` set to this repo and `target_root` set to the SeedCash tree. Pass `os_root` when the OS tree is available. Pass `baseline_root` only for a clean SeedSigner checkout at the tag in `brain/pin.md`.

Do not review the code yourself in place of the workflow. Do not modify the target tree. Do not file issues from this skill; that is `/seedcash-issue`.

If the user only wants the open rows re-checked, run `reverify-corpus` instead.
