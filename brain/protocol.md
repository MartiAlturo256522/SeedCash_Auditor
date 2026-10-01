# Audit protocol

The run is `audit-seedcash`. A cheaper pass over rows already marked `open` is `reverify-corpus`. Filing is `publish-seedcash-issues`. A confirmed report is not an issue. The upload path re-reads the finding through all eight layers in `brain/review-layers.md`, then waits for the operator.

## Order

1. Read `brain/pin.md`, `brain/scope.md`, `brain/disclosure.md`, and this file.
2. `git rev-parse HEAD` in the tree under review. Record the commit on the report. If it differs from `brain/pin.md`, the pin is stale and the report says so. Do not edit the target to make them match.
3. Each lane reads its files from `brain/lanes.json` and re-checks every invariant with its lane, including rows marked `closed`. A closed row that no longer matches the code is a regression, which is a new open finding.
4. New breaks that have no invariant yet are reported with an empty `invariant_id`. The operator adds an invariant only after all three review layers confirm the finding. The check text is added in `brain/invariants.md`, not copied into a skill.
5. The audit's review contract is Quote, then Reach, then Impact. The upload contract is all eight layers in `brain/review-layers.md`. A layer that fails or returns no evidence eliminates the finding. Eliminated findings stay out of the issue queue.
6. The report is assembled from the finding fields. It has no reproduction section.

## Rules that the script enforces

- Specialists and the three review layers run read-only.
- A finding without a file and a broken check is dropped.
- A second copy of the same file, function, and invariant is dropped before the review layers.
- A row the specialist marked `closed` is dropped. A regression is reported with status `open`.
- An `os` finding is dropped when no `os_root` was passed.
- The report is rendered by the workflow from those fields, so a specialist cannot append a payload section later.
- OS lanes that were given no `os_root` record a skip. A skip is not a pass.

## What the operator does after

- Read the report.
- A confirmed finding is a lead. Run `publish-seedcash-issues` with `args.publish` true and `args.target_root` set when an issue is actually wanted. That run reads `python3 tools/list_issues.py` and repeats the eight layers on at most four candidates.
- File only by the rule in `brain/issue-policy.md`.
- Update `status_at_pin` in `brain/invariants.md` when a later commit actually changes the check. Update `brain/pin.md` in the same commit. `tools/lint_brain.py` has to stay green.
