---
name: seedcash-issue
description: >
  Draft a GitHub issue for one confirmed SeedCash finding, and file it
  only after the operator confirms. Use when the user says open a
  SeedCash issue, file this finding, or /seedcash-issue.
---

# File a SeedCash issue

Read `brain/issue-policy.md` and `agents/issue-clerk.md`.

Run `python3 tools/file_issue.py --finding <path>` and show the operator the printed title and body. That command does not call `gh`.

Call `gh` only when the operator, in this conversation, has approved that exact draft. The command is then `SEEDCASH_AUDITOR_CONFIRM=yes python3 tools/file_issue.py --finding <path> --confirm`.

A batch of ready findings is `agents/redactor.md`.
