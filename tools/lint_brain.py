#!/usr/bin/env python3
"""Check that each audit fact has one home."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
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
STATUSES = {"open", "closed", "unchecked"}
META_KEYS = ("lane", "impact", "status_at_pin", "file_ready", "where")
INV_SPLIT = re.compile(r"(?=^### INV-[A-Z0-9-]+\s*$)", re.M)
INV_HEAD = re.compile(r"^### (INV-[A-Z0-9-]+)\s*$")
DL_HEAD = re.compile(r"^### (DL-[A-Z0-9-]+)\s*$", re.M)
OPEN_IDS = re.compile(r"let open_ids = \[(.*?)\];", re.S)
QUOTED_INV = re.compile(r'"(INV-[A-Z0-9-]+)"')


def pin_value(text: str, key: str) -> str:
    prefix = f"- {key}:"
    for line in text.splitlines():
        if line.startswith(prefix):
            parts = line.split("`")
            if len(parts) >= 2:
                return parts[1].strip()
            return line[len(prefix) :].strip()
    return ""


def parse_invariants(text: str) -> tuple[str, list[dict]]:
    parts = INV_SPLIT.split(text)
    preamble = parts[0]
    rows = []
    for part in parts[1:]:
        lines = part.splitlines()
        head = INV_HEAD.match(lines[0]) if lines else None
        if not head:
            continue
        row = {"id": head.group(1), "meta": {}, "body": ""}
        index = 1
        while index < len(lines) and lines[index].strip() == "":
            index += 1
        ok = True
        for key in META_KEYS:
            prefix = f"- {key}: "
            if index >= len(lines) or not lines[index].startswith(prefix):
                row["error"] = f"bullet {key} missing"
                ok = False
                break
            row["meta"][key] = lines[index][len(prefix) :].strip()
            index += 1
            while index < len(lines) and lines[index].strip() == "":
                index += 1
        if ok:
            row["body"] = "\n".join(lines[index:]).strip()
        rows.append(row)
    return preamble, rows


def workflow_open_ids(text: str) -> list[str]:
    found = OPEN_IDS.search(text)
    if not found:
        return []
    return QUOTED_INV.findall(found.group(1))


def check() -> list[str]:
    errors: list[str] = []
    pin_path = ROOT / "brain" / "pin.md"
    inv_path = ROOT / "brain" / "invariants.md"
    lanes_path = ROOT / "brain" / "lanes.json"
    delta_path = ROOT / "brain" / "delta-checklist.md"
    audit_path = ROOT / ".grok" / "workflows" / "audit-seedcash.rhai"
    reverify_path = ROOT / ".grok" / "workflows" / "reverify-corpus.rhai"
    file_path = ROOT / ".grok" / "workflows" / "file-seedcash-issue.rhai"
    schema_path = ROOT / "schemas" / "finding.schema.json"

    for path in (pin_path, inv_path, lanes_path, delta_path, audit_path, reverify_path, file_path, schema_path):
        if not path.is_file():
            errors.append(f"missing {path.relative_to(ROOT)}")
    if errors:
        return errors

    pin = pin_path.read_text(encoding="utf-8")
    commit = pin_value(pin, "app_commit")
    issue_repo = pin_value(pin, "issue_repo")
    if not commit:
        errors.append("pin.md has no app_commit")
    if not issue_repo or "/" not in issue_repo:
        errors.append("pin.md has no owner/name issue_repo")

    preamble, rows = parse_invariants(inv_path.read_text(encoding="utf-8"))
    if f"- pin_commit: {commit}" not in preamble:
        errors.append("invariants.md pin_commit does not match pin.md app_commit")

    lanes = json.loads(lanes_path.read_text(encoding="utf-8"))["lanes"]
    lane_ids = [lane["id"] for lane in lanes]
    if len(lane_ids) != len(set(lane_ids)):
        errors.append("duplicate lane id")

    seen: set[str] = set()
    by_lane: dict[str, int] = {lane_id: 0 for lane_id in lane_ids}
    open_ids: list[str] = []
    for row in rows:
        inv_id = row["id"]
        if inv_id in seen:
            errors.append(f"duplicate {inv_id}")
        seen.add(inv_id)
        if row.get("error"):
            errors.append(f"{inv_id}: {row['error']}")
            continue
        meta = row["meta"]
        lane = meta["lane"]
        if lane not in by_lane:
            errors.append(f"{inv_id}: unknown lane {lane}")
        elif lane == "delta":
            errors.append(f"{inv_id}: delta owns the checklist, not invariants")
        else:
            by_lane[lane] += 1
        if meta["impact"] not in IMPACTS:
            errors.append(f"{inv_id}: impact {meta['impact']}")
        if meta["status_at_pin"] not in STATUSES:
            errors.append(f"{inv_id}: status {meta['status_at_pin']}")
        if meta["file_ready"] not in {"yes", "no"}:
            errors.append(f"{inv_id}: file_ready must be yes or no")
        if meta["file_ready"] == "yes" and meta["status_at_pin"] != "open":
            errors.append(f"{inv_id}: file_ready yes requires status open")
        if not meta["where"]:
            errors.append(f"{inv_id}: empty where")
        if not row["body"]:
            errors.append(f"{inv_id}: empty body")
        if meta.get("status_at_pin") == "open":
            open_ids.append(inv_id)

    for lane in lanes:
        lane_id = lane["id"]
        skill = ROOT / ".grok" / "skills" / lane["skill"] / "SKILL.md"
        agent = ROOT / lane["agent"]
        if not skill.is_file():
            errors.append(f"lane {lane_id} missing skill {lane['skill']}")
        else:
            text = skill.read_text(encoding="utf-8")
            if f"name: {lane['skill']}" not in text.split("---", 2)[1]:
                errors.append(f"skill {lane['skill']} frontmatter name mismatch")
        if not agent.is_file():
            errors.append(f"lane {lane_id} missing {lane['agent']}")
        if lane_id != "delta" and by_lane.get(lane_id, 0) < 1:
            errors.append(f"lane {lane_id} owns no invariant")

    delta_ids = DL_HEAD.findall(delta_path.read_text(encoding="utf-8"))
    if len(delta_ids) < 1:
        errors.append("delta checklist has no DL headings")
    if len(delta_ids) != len(set(delta_ids)):
        errors.append("duplicate DL heading")

    listed = workflow_open_ids(reverify_path.read_text(encoding="utf-8"))
    if set(listed) != set(open_ids) or len(listed) != len(open_ids):
        missing = sorted(set(open_ids) - set(listed))
        extra = sorted(set(listed) - set(open_ids))
        errors.append(
            "reverify-corpus open_ids diverges from open invariants"
            + (f" missing={missing}" if missing else "")
            + (f" extra={extra}" if extra else "")
        )

    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    audit_text = audit_path.read_text(encoding="utf-8")
    for field in schema["required"]:
        if field not in audit_text:
            errors.append(f"audit workflow omits finding field {field}")
    for field in ("real", "reason", "evidence"):
        if field not in audit_text:
            errors.append(f"audit workflow omits verdict field {field}")

    for name in ("seedcash-audit", "seedcash-issue"):
        skill = ROOT / ".grok" / "skills" / name / "SKILL.md"
        if not skill.is_file():
            errors.append(f"missing skill {name}")

    disclosure = (ROOT / "brain" / "disclosure.md").read_text(encoding="utf-8")
    for impact in IMPACTS:
        if f"`{impact}`" not in disclosure:
            errors.append(f"disclosure.md does not name {impact}")

    template = (ROOT / "templates" / "github-issue.md").read_text(encoding="utf-8")
    for section in ("Broken check", "Impact class", "Where", "Fix direction", "Evidence"):
        if section not in template:
            errors.append(f"issue template missing {section}")
    return errors


def main() -> int:
    errors = check()
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        print(f"{len(errors)} brain check(s) failed", file=sys.stderr)
        return 1
    print("brain checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
