---
name: seedcash-wysiwys
description: >
  Audit SeedCash what-you-sign-is-what-you-see: overview amounts,
  BchAmount rounding, change detection, NFT category walk, locktime
  display, and witness UTXO precedence. Use when reviewing psbt_views.py,
  the amount screen, or /seedcash-wysiwys.
---

# WYSIWYS lane

Read `agents/wysiwys.md` and the `wysiwys` headings in `brain/invariants.md`. Follow `brain/disclosure.md`.

Use impact class `theft` only when a valid signature covers an output the walk did not show.
