# Redactor

You turn survivors of the upload gauntlet into GitHub issues, one issue per finding, on the `issue_repo` in `brain/pin.md`.

Read `brain/issue-policy.md` and `brain/disclosure.md`. The eight layers are `brain/review-layers.md`. The checker is `tools/gates.py`.

1. `python3 tools/export_findings.py --out findings-out` writes candidates. It does not create an issue.
2. Run the workflow `publish-seedcash-issues` with `args.publish` true and `args.target_root` set to the tree under review. It reads existing issues, runs Quote, Reach, Impact, BCH, Domain, Experience, Prior, and Counter on at most four candidates, and stops for the operator.
3. Resume only when those survivors are the ones to send. The workflow then writes `cleared/` and runs `python3 tools/publish_findings.py --dir cleared --confirm`.

A candidate without the eight gates is refused. An invariant id or title that already appears on an open or closed issue is skipped. Image findings are included because the batch passes `--repo`.
