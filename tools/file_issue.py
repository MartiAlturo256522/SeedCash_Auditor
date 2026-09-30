#!/usr/bin/env python3
"""Draft or file one SeedCash audit issue.

Dry-run unless both --confirm and SEEDCASH_AUDITOR_CONFIRM=yes are set.
The body is the section order in templates/github-issue.md.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

CONFIRM_ENV = "SEEDCASH_AUDITOR_CONFIRM"
CONFIRM_VALUE = "yes"
FORBIDDEN_KEYS = {"reproduction", "repro", "poc", "payload", "exploit", "steps"}
FORBIDDEN_TEXT = ("steps to reproduce", "proof of concept", "exploit", "payload")
REPO_RE = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
IMPACTS = {
    "theft",
    "wysiwys",
    "invalid-signature",
    "griefing",
    "fail-open",
    "custody",
    "airgap",
    "supply-chain",
    "spec-deviation",
    "display",
}
REQUIRED_STRINGS = (
    "title",
    "file",
    "function",
    "broken_check",
    "fix_direction",
    "evidence",
    "commit",
    "lane",
    "impact_class",
    "status",
)


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def run_gh(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(list(args), check=False, capture_output=True, text=True)


def default_repo() -> str:
    pin = repo_root() / "brain" / "pin.md"
    for line in pin.read_text(encoding="utf-8").splitlines():
        if line.startswith("- issue_repo:"):
            parts = line.split("`")
            if len(parts) >= 2 and parts[1].strip():
                return parts[1].strip()
    raise SystemExit("refused: brain/pin.md has no issue_repo")


def refuse(message: str) -> None:
    print(f"refused: {message}", file=sys.stderr)
    raise SystemExit(2)


def load_finding(path: str) -> dict:
    raw = Path(path).read_text(encoding="utf-8")
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        refuse(f"finding is not JSON: {exc}")
    if not isinstance(data, dict):
        refuse("finding must be a JSON object")
    return data


def check_policy(finding: dict, repo: str, repo_was_explicit: bool) -> None:
    bad = {key.lower() for key in finding} & FORBIDDEN_KEYS
    if bad:
        refuse("forbidden keys: " + ", ".join(sorted(bad)))
    if finding.get("status") != "open":
        refuse("status is not open")
    if finding.get("issue_ready") is not True:
        refuse("issue_ready is not true")
    if finding.get("impact_class") not in IMPACTS:
        refuse("impact_class is outside the disclosure enum")
    for field in REQUIRED_STRINGS:
        value = finding.get(field)
        if not isinstance(value, str) or not value.strip():
            refuse(f"missing {field}")
    if finding["lane"] == "os" and not repo_was_explicit:
        refuse("os findings are not filed against the app repo; pass --repo")
    if not REPO_RE.match(repo):
        refuse("repo is not owner/name")
    if len(finding["title"].strip()) > 120:
        refuse("title longer than 120 characters")
    blob = json.dumps(finding).lower()
    for phrase in FORBIDDEN_TEXT:
        if phrase in blob:
            refuse(f"finding text contains {phrase}")


def render_body(finding: dict) -> str:
    severity = finding.get("severity")
    severity_line = ""
    if isinstance(severity, str) and severity.strip():
        severity_line = f"\nSeverity: {severity.strip()}\n"
    invariant = finding.get("invariant_id") or ""
    invariant_line = f"\nInvariant: {invariant}\n" if invariant else ""
    body = (
        f"{finding['broken_check'].strip()}\n"
        f"{severity_line}"
        f"\n## Broken check\n\n"
        f"{finding['broken_check'].strip()}\n"
        f"\n## Impact class\n\n"
        f"{finding['impact_class'].strip()}\n"
        f"\n## Where\n\n"
        f"File: `{finding['file'].strip()}`\n\n"
        f"Function: `{finding['function'].strip()}`\n\n"
        f"Commit: `{finding['commit'].strip()}`\n"
        f"{invariant_line}"
        f"\n## Fix direction\n\n"
        f"{finding['fix_direction'].strip()}\n"
        f"\n## Evidence\n\n"
        f"{finding['evidence'].strip()}\n"
        f"\n## What this issue does not include\n\n"
        f"This issue stops at the broken check, the impact class, and the fix direction.\n"
    )
    lowered = body.lower()
    for phrase in FORBIDDEN_TEXT:
        if phrase in lowered:
            refuse(f"rendered body contains {phrase}")
    return body


def issue_title(finding: dict) -> str:
    title = finding["title"].strip()
    if title.startswith("[audit] "):
        return title
    return "[audit] " + title


def search_duplicates(repo: str, title: str) -> list[dict]:
    probe = title[len("[audit] ") :] if title.startswith("[audit] ") else title
    words = probe.split()[:6]
    query = "in:title " + " ".join(words)
    result = run_gh(
        [
            "gh",
            "issue",
            "list",
            "--repo",
            repo,
            "--state",
            "open",
            "--search",
            query,
            "--limit",
            "10",
            "--json",
            "number,title",
        ]
    )
    if result.returncode != 0:
        detail = (result.stderr or result.stdout or "gh issue list failed").strip()
        raise RuntimeError(detail)
    data = json.loads(result.stdout or "[]")
    if not isinstance(data, list):
        raise RuntimeError("gh issue list did not return a list")
    return [row for row in data if isinstance(row, dict)]


def create_issue(repo: str, title: str, body: str) -> str:
    handle = tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8")
    try:
        handle.write(body)
        handle.close()
        result = run_gh(
            [
                "gh",
                "issue",
                "create",
                "--repo",
                repo,
                "--title",
                title,
                "--body-file",
                handle.name,
            ]
        )
    finally:
        Path(handle.name).unlink(missing_ok=True)
    if result.returncode != 0:
        detail = (result.stderr or result.stdout or "gh issue create failed").strip()
        print(detail, file=sys.stderr)
        raise SystemExit(3)
    return (result.stdout or "").strip()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Draft or file one SeedCash audit issue.")
    parser.add_argument("--finding", required=True, help="Path to a finding JSON object.")
    parser.add_argument("--repo", help="owner/name. Defaults to issue_repo in brain/pin.md.")
    parser.add_argument(
        "--confirm",
        action="store_true",
        help=f"File the issue. Also requires {CONFIRM_ENV}={CONFIRM_VALUE}.",
    )
    parser.add_argument(
        "--allow-duplicate",
        action="store_true",
        help="File even when an open issue has a similar title.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    repo_was_explicit = args.repo is not None
    repo = args.repo.strip() if args.repo else default_repo()
    finding = load_finding(args.finding)
    check_policy(finding, repo, repo_was_explicit)
    title = issue_title(finding)
    body = render_body(finding)

    print(f"repo: {repo}")
    print(f"title: {title}")
    print("---")
    print(body, end="" if body.endswith("\n") else "\n")

    search_error = ""
    duplicates: list[dict] = []
    try:
        duplicates = search_duplicates(repo, title)
    except (RuntimeError, json.JSONDecodeError, OSError) as exc:
        search_error = str(exc)
        print(f"duplicate search skipped: {search_error}", file=sys.stderr)

    if duplicates:
        print("open issues with a similar title:")
        for row in duplicates:
            print(f"  #{row.get('number')} {row.get('title')}")

    if not args.confirm:
        print("dry-run: gh issue create was not called")
        return 0

    if os.environ.get(CONFIRM_ENV) != CONFIRM_VALUE:
        refuse(f"set {CONFIRM_ENV}={CONFIRM_VALUE} together with --confirm")
    if search_error:
        refuse("duplicate search failed; not filing")
    if duplicates and not args.allow_duplicate:
        refuse("a similar open issue exists; pass --allow-duplicate to file anyway")

    url = create_issue(repo, title, body)
    print(url)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
