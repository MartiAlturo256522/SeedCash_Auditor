# Audit protocol

The run is `audit-seedcash`. A cheaper pass over rows already marked `open` is `reverify-corpus`. Filing is `file-seedcash-issue` and stays a draft until the operator confirms.

## Order

1. Read `brain/pin.md`, `brain/scope.md`, `brain/disclosure.md`, and this file.
2. `git rev-parse HEAD` in the tree under review. Record the commit on the report. If it differs from `brain/pin.md`, the pin is stale and the report says so. Do not edit the target to make them match.
3. Each lane reads its files from `brain/lanes.json` and re-checks every invariant with its lane, including rows marked `closed`. A closed row that no longer matches the code is a regression, which is a new open finding.
4. New breaks that have no invariant yet are reported with an empty `invariant_id`. The operator adds an invariant only after the skeptic confirms the finding. The check text is added here, in `brain/invariants.md`, not copied into a skill.
5. A skeptic confirms a finding only after opening the named file. Missing evidence leaves the finding unconfirmed. Unconfirmed findings stay out of the issue queue.
6. The report is assembled from the finding fields. It has no reproduction section.

## Rules that the script enforces

- Specialists and skeptics run read-only.
- A finding without a file and a broken check is dropped.
- The report is rendered by the workflow from those fields, so a specialist cannot append a payload section later.
- OS lanes that were given no `os_root` record a skip. A skip is not a pass.

## What the operator does after

- Read the report.
- For each confirmed finding with `issue_ready` true, run `file-seedcash-issue` and read the draft.
- File only by the rule in `brain/issue-policy.md`.
- Update `status_at_pin` in `brain/invariants.md` when a later commit actually changes the check. Update `brain/pin.md` in the same commit. `tools/lint_brain.py` has to stay green.
