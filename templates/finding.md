# Finding JSON

One finding is one object matching `schemas/finding.schema.json`. Write it to a file and pass that path to `tools/file_issue.py`.

`invariant_id` is empty when the break has no row yet. After a skeptic confirms it, add the row to `brain/invariants.md` and re-run `tools/lint_brain.py`.

`issue_ready` is true only when the invariant's `file_ready` is `yes` and a human has read the evidence. OS findings stay false until an OS repository is named.
