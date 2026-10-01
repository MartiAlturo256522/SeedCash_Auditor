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

`tools/file_issue.py` prints the title and the body and does not call `gh issue create` until step 5. The workflow `file-seedcash-issue` stops for a human confirmation before it can reach step 5.

## Batch

`agents/redactor.md` exports every `file_ready: yes` row. `tools/publish_findings.py` files that directory, one issue per JSON file. The batch passes `--repo` on every call, so an image finding in the directory is filed on that repo. The single-finding tool still requires an explicit `--repo` when the lane is `os`.

Before it renders a finding, the batch skips it when an open issue title already contains the invariant id or another phrase in `dedupe_terms`. Creation still requires step 5. If the open-issue list fails, a confirmed batch stops before any create.

The workflow `publish-seedcash-issues` prints the drafts and stops. It reaches step 5 only when `args.publish` is true and the operator resumes past the confirmation.

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
