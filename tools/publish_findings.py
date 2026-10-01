#!/usr/bin/env python3
"""Publish one GitHub issue per finding JSON in a directory.

Dry-run unless both --confirm and SEEDCASH_AUDITOR_CONFIRM=yes are set.
An open issue whose title already contains a dedupe term is skipped.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import file_issue
import gates


def list_titles(repo: str) -> list[dict]:
    result = file_issue.run_gh(
        [
            "gh",
            "issue",
            "list",
            "--repo",
            repo,
            "--state",
            "all",
            "--limit",
            "200",
            "--json",
            "number,title,state",
        ]
    )
    if result.returncode != 0:
        detail = (result.stderr or result.stdout or "gh issue list failed").strip()
        raise RuntimeError(detail)
    data = json.loads(result.stdout or "[]")
    if not isinstance(data, list):
        raise RuntimeError("gh issue list did not return a list")
    return [row for row in data if isinstance(row, dict)]


def matching_open(titles: list[dict], terms: list[str]) -> dict | None:
    for row in titles:
        title = str(row.get("title") or "")
        folded = title.casefold()
        for term in terms:
            if term and term.casefold() in folded:
                return row
    return None


def publish(directory: Path, repo: str, confirm: bool, allow_duplicate: bool) -> dict:
    paths = sorted(directory.glob("*.json"))
    if not paths:
        file_issue.refuse(f"no finding JSON in {directory}")
    if confirm and os.environ.get(file_issue.CONFIRM_ENV) != file_issue.CONFIRM_VALUE:
        file_issue.refuse(
            f"set {file_issue.CONFIRM_ENV}={file_issue.CONFIRM_VALUE} together with --confirm"
        )

    search_error = ""
    titles: list[dict] = []
    try:
        titles = list_titles(repo)
    except (RuntimeError, json.JSONDecodeError, OSError) as exc:
        search_error = str(exc)
        print(f"open-issue list skipped: {search_error}", file=sys.stderr)
    if confirm and search_error:
        file_issue.refuse("open-issue list failed; not filing")

    filed: list[str] = []
    skipped: list[str] = []
    refused: list[str] = []
    for path in paths:
        finding = json.loads(path.read_text(encoding="utf-8"))
        terms = finding.get("dedupe_terms") or [finding.get("invariant_id") or ""]
        if not isinstance(terms, list):
            terms = [str(terms)]
        hit = matching_open(titles, [str(term) for term in terms])
        label = finding.get("invariant_id") or path.name
        if not gates.gates_ok(finding):
            refused.append(f"{label}: gates")
            print(f"refused {label}: eight review gates are incomplete", file=sys.stderr)
            continue
        if hit and not allow_duplicate:
            skipped.append(
                f"{label} already {hit.get('state') or 'open'} as #{hit.get('number')} {hit.get('title')}"
            )
            print(f"skip {label}: #{hit.get('number')} {hit.get('state') or 'open'} {hit.get('title')}")
            continue
        argv = ["--finding", str(path), "--repo", repo]
        if allow_duplicate:
            argv.append("--allow-duplicate")
        if confirm:
            argv.append("--confirm")
        try:
            code = file_issue.main(argv)
        except SystemExit as exc:
            refused.append(f"{label}: {exc.code}")
            print(f"refused {label}: exit {exc.code}", file=sys.stderr)
            continue
        if confirm and code == 0:
            filed.append(label)
            titles.append({"number": "new", "title": file_issue.issue_title(finding)})
        elif code == 0:
            filed.append(label)
    print(
        f"findings={len(paths)} filed={len(filed)} skipped={len(skipped)} refused={len(refused)}"
    )
    if refused:
        return {"filed": filed, "skipped": skipped, "refused": refused, "ok": False}
    return {"filed": filed, "skipped": skipped, "refused": refused, "ok": True}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Publish one issue per finding JSON file.")
    parser.add_argument("--dir", required=True, help="Directory of finding JSON files.")
    parser.add_argument("--repo", help="owner/name. Defaults to issue_repo in brain/pin.md.")
    parser.add_argument(
        "--confirm",
        action="store_true",
        help=f"Create the issues. Also requires {file_issue.CONFIRM_ENV}={file_issue.CONFIRM_VALUE}.",
    )
    parser.add_argument("--allow-duplicate", action="store_true")
    args = parser.parse_args(argv)
    repo = args.repo.strip() if args.repo else file_issue.default_repo()
    directory = Path(args.dir)
    if not directory.is_absolute():
        directory = file_issue.repo_root() / directory
    result = publish(directory, repo, args.confirm, args.allow_duplicate)
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
