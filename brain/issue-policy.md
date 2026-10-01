# Issue policy

Upstream issues are English, one confirmed finding each, filed against the `issue_repo` in `brain/pin.md`.

The body follows `templates/github-issue.md`. The renderer is `tools/file_issue.py`. A body that grows a reproduction section is a bug in the renderer.

## When an issue may be created

All of the following are required:

1. All eight layers in `brain/review-layers.md` kept the finding. The finding JSON carries `gates` and `gate_evidence` for `quote`, `reach`, `impact`, `bch`, `domain`, `experience`, `prior_issues`, and `counter`. `tools/gates.py` is the check. A draft with `issue_ready` true and no gates is not ready.
2. The finding's `status` is `open` and `issue_ready` is true.
3. The lane is not `os`, unless the operator passed `--repo` for an OS repository.
4. `python3 tools/list_issues.py --state all` shows no open or closed issue with the same title, unless the operator passed `--allow-duplicate`. The Prior layer already did this comparison. The filer does it again.
5. The operator ran the filer with `--confirm` and `SEEDCASH_AUDITOR_CONFIRM=yes`.

`tools/file_issue.py` prints the title and the body and does not call `gh issue create` until step 5. The workflow `file-seedcash-issue` stops for a human confirmation before it can reach step 5.

## Batch

`agents/redactor.md` exports every `file_ready: yes` row as a candidate. Candidates are not issues. `tools/publish_findings.py` files a directory only when each JSON passes `tools/gates.py`, then skips a title that already appears on an open or closed issue. The batch passes `--repo` on every call, so an image finding in the directory is filed on that repo. The single-finding tool still requires an explicit `--repo` when the lane is `os`, and it still requires the eight gates.

Creation still requires step 5. If the issue list fails, a confirmed batch stops before any create.

The workflow `publish-seedcash-issues` prints the candidate count and stops. With `args.publish` true it runs the eight layers on at most four candidates, stops for the operator, writes `cleared/` only for survivors, and only then calls the filer. A missing `target_root` stops that path.

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
