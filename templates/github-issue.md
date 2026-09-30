# GitHub issue body

`tools/file_issue.py` is the renderer. This page is the section order it has to keep.

1. One-paragraph summary, which is the finding's broken check.
2. `## Broken check`
3. `## Impact class`
4. `## Where` — file, function, commit.
5. `## Fix direction`
6. `## Evidence` — a short quote of the check.
7. `## What this issue does not include` — one sentence: the issue stops at the broken check, the impact class, and the fix direction.

The title is `[audit] ` plus the finding title. No other section is allowed.
