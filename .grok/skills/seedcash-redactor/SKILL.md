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

Export candidates with `python3 tools/export_findings.py --out findings-out`. Do not pass `--confirm` on that directory.

File only through `publish-seedcash-issues` with `args.publish` true and `args.target_root` set, after the operator has asked to publish in this conversation. The workflow runs the eight layers on at most four candidates and stops before it writes `cleared/`. Do not add a reproduction section.
