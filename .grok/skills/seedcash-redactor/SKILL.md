---
name: seedcash-redactor
description: >
  Write one GitHub issue per ready SeedCash finding and publish the
  batch on the SeedCash repo when the operator asks. Use when the user
  says publish the findings, open the issues, redactor, n issues, or
  /seedcash-redactor.
---

# SeedCash redactor

Read `agents/redactor.md` and `brain/issue-policy.md`.

Run `python3 tools/export_findings.py --out findings-out` and then `python3 tools/publish_findings.py --dir findings-out`. Show the operator the count of drafts and the skips.

Pass `--confirm` with `SEEDCASH_AUDITOR_CONFIRM=yes` only after the operator, in this conversation, has asked to publish the batch. Do not add a reproduction section. Do not file a second issue for a check that the tool skipped as already open.
