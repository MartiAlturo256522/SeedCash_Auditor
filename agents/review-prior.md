# Prior-issue gate

Read the Prior section of `brain/review-layers.md`.

Run `python3 tools/list_issues.py --state all` in the auditor repo. Compare the invariant id and the title with every open and closed issue.

`keep` is false when the same check already has an issue. `evidence` then includes that issue number, with a `#`.

`keep` is true only when the list was read and `evidence` contains `no matching issue`. A failed list is `keep` false. Do not paste a reproduction from an old issue.
