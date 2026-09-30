---
name: seedcash-os
description: >
  Audit seedcash-os: kernel CONFIG_NET fragment, image-versus-app commit
  lag, version string, ecdsa pin, and the uid of the signer process.
  Use when reviewing seedcash-os, kernel.config, or /seedcash-os.
---

# OS lane

Read `agents/os-image.md` and the `os` headings in `brain/invariants.md`. Follow `brain/disclosure.md`.

The OS path is `os_path` in `brain/pin.md` unless the operator passed another tree. Do not file OS findings against the app repo from this skill.
