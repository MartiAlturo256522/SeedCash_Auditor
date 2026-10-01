# Issue policy

Upstream issues are English, one confirmed finding each, filed against the `issue_repo` in `brain/pin.md`.

The body follows `templates/github-issue.md`. The renderer is `tools/file_issue.py`. A body that grows a reproduction section is a bug in the renderer.

## When an issue may be created

All of the following are required:

1. Quote, Reach, and Impact each kept the finding with evidence, or the operator re-read the lines and set `issue_ready` true on the finding JSON. The layer contract is `brain/review-layers.md`.
2. The finding's `status` is `open` and `issue_ready` is true.
3. The lane is not `os`, unless the operator passed `--repo` for an OS repository.
4. `gh issue list` shows no open issue with the same title, unless the operator passed `--allow-duplicate`.
5. The operator ran the filer with `--confirm` and `SEEDCASH_AUDITOR_CONFIRM=yes`.

`tools/file_issue.py` prints the title and the body and does not call `gh` until step 5. The workflow `file-seedcash-issue` stops for a human confirmation before it can reach step 5.

## Severity

- `critical` — valid signature, funds or tokens can move, review skipped a committed field.
- `high` — the screen can approve bytes the user did not see, or the air gap has a code path.
- `medium` — a binding or parsing check is wrong and the practical result is an invalid signature, a stuck device, or a seed that restores elsewhere.
- `low` — spec deviation that still verifies, a stale version string, a source-only image lead.
- `info` — closed check, kept so a regression has a name.

## What does not get filed

- A row in `brain/invariants.md` with `file_ready: no`.
- A row whose `status_at_pin` is `closed` or `unchecked`.
- A cluster of findings that are one broken check. File the check once.
- Anything the disclosure file forbids.
