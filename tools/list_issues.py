#!/usr/bin/env python3
"""Print issue number, state, and title. This tool never creates an issue."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import file_issue

STATES = {"open", "closed", "all"}


def list_issues(repo: str, state: str, limit: int) -> list[dict]:
    if state not in STATES:
        file_issue.refuse("state must be open, closed, or all")
    if not file_issue.REPO_RE.match(repo):
        file_issue.refuse("repo is not owner/name")
    capped = max(1, min(limit, 200))
    result = file_issue.run_gh(
        [
            "gh",
            "issue",
            "list",
            "--repo",
            repo,
            "--state",
            state,
            "--limit",
            str(capped),
            "--json",
            "number,title,state",
        ]
    )
    if result.returncode != 0:
        detail = (result.stderr or result.stdout or "gh issue list failed").strip()
        print(detail, file=sys.stderr)
        raise SystemExit(3)
    data = json.loads(result.stdout or "[]")
    if not isinstance(data, list):
        file_issue.refuse("issue list was not a list")
    rows = []
    for row in data:
        if not isinstance(row, dict):
            continue
        rows.append(
            {
                "number": row.get("number"),
                "state": row.get("state"),
                "title": row.get("title"),
            }
        )
    return rows


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="List issue titles. Does not create issues.")
    parser.add_argument("--repo", help="owner/name. Defaults to issue_repo in brain/pin.md.")
    parser.add_argument("--state", default="all", choices=sorted(STATES))
    parser.add_argument("--limit", type=int, default=200)
    args = parser.parse_args(argv)
    repo = args.repo.strip() if args.repo else file_issue.default_repo()
    rows = list_issues(repo, args.state, args.limit)
    for row in rows:
        print(f"#{row['number']} {row['state']} {row['title']}")
    print(f"issues={len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
