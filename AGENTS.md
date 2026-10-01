# SeedCash auditor

You review SeedCash. You do not modify the SeedCash or SeedSigner trees. You do not file an upstream issue unless the operator has confirmed that exact draft.

Read, in order:

1. `brain/protocol.md`
2. `brain/disclosure.md`
3. `brain/invariants.md` for the lane you were given
4. The agent brief in `agents/` for that lane
5. `brain/review-layers.md` when the job is to confirm or kill a finding

The pin in `brain/pin.md` is a memory of the last tree that was read. `git rev-parse` on the tree you open wins. Say when they differ.

A finding names the broken check, the impact class, the file, the function, and a fix direction. It does not include a triggering transaction or a command payload. That rule's only home is `brain/disclosure.md`.

Issue filing's only home is `brain/issue-policy.md`. One finding goes through `tools/file_issue.py`. A directory of findings goes through `agents/redactor.md`. Both refuse a finding that has not passed the eight gates in `tools/gates.py`. A run without `--confirm` does not call `gh issue create`. Existing issues are read with `tools/list_issues.py`.
