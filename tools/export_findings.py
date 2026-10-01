#!/usr/bin/env python3
"""Write one finding JSON per open, file-ready invariant.

The check text stays in brain/invariants.md. This only renders it into the
shape tools/file_issue.py already accepts.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import lint_brain

SEVERITY = {
    "theft": "critical",
    "airgap": "high",
    "wysiwys": "high",
    "fail-open": "high",
    "custody": "medium",
    "supply-chain": "medium",
    "invalid-signature": "medium",
    "griefing": "medium",
    "spec-deviation": "low",
    "display": "low",
}
# Open upstream titles that already describe the same check. The publisher
# skips a finding when one of these phrases is already an open issue title.
ALREADY_OPEN = {
    "INV-SCHNORR-TAG": "SCHNORR USES A DIFFERENT TAG",
    "INV-PARSE-FULL-CONSUME": "TRANSACTION PARSER ACCEPTS TRAILING BYTES",
    "INV-QR-SHELL": "SHELL=TRUE IN QR",
    "INV-BYTEWORDS-CRC": "BYTEWORDS WITHOUT CRC",
    "INV-BIP39-NFKD": "BIP39 PASSPHRASE DOES NOT USE NFKD",
    "INV-KERNEL-NET": "KERNEL AND AIR-GAP",
}
WHERE_RE = re.compile(r"`([^`]+)`\s+`([^`]+)`")


def split_check(body: str) -> tuple[str, str]:
    marker = "The pass condition is"
    cut = body.find(marker)
    if cut == -1:
        return body.strip(), "Restore the check named by this invariant."
    broken = body[:cut].strip()
    fix = body[cut + len(marker) :].lstrip(" :").strip()
    for stop in ("The finding has to say", "This row was not finished"):
        if stop in fix:
            fix = fix.split(stop)[0].strip()
    kept = []
    for sentence in re.split(r"(?<=\.)\s+", fix):
        if "the finding" in sentence.lower():
            continue
        kept.append(sentence)
    if kept:
        fix = " ".join(kept).strip()
    return broken, fix.rstrip(".")


def title_for(inv_id: str, broken: str) -> str:
    sentence = broken.split(". ")[0].replace("`", "").strip()
    prefix = f"{inv_id}: "
    room = 120 - len(prefix)
    if len(sentence) > room:
        sentence = sentence[: room - 3].rstrip() + "..."
    title = prefix + sentence
    return title[:120]


def to_finding(row: dict, commit: str, account: str) -> dict:
    meta = row["meta"]
    broken, fix = split_check(row["body"])
    if account and "`brain/pin.md`" in fix:
        fix = fix.replace("`brain/pin.md`", f"`{account}`")
    where = meta["where"]
    found = WHERE_RE.search(where)
    if found:
        path, function = found.group(1), found.group(2)
    else:
        path, function = where, row["id"]
    terms = [row["id"]]
    if row["id"] in ALREADY_OPEN:
        terms.append(ALREADY_OPEN[row["id"]])
    return {
        "lane": meta["lane"],
        "title": title_for(row["id"], broken),
        "invariant_id": row["id"],
        "status": "open",
        "issue_ready": True,
        "file": path,
        "function": function,
        "broken_check": broken,
        "impact_class": meta["impact"],
        "fix_direction": fix,
        "evidence": broken.split(". ")[0].strip(),
        "commit": commit,
        "severity": SEVERITY[meta["impact"]],
        "dedupe_terms": terms,
    }


def ready_rows(text: str) -> list[dict]:
    _, rows = lint_brain.parse_invariants(text)
    ready = []
    for row in rows:
        if row.get("error"):
            continue
        meta = row["meta"]
        if meta["status_at_pin"] == "open" and meta["file_ready"] == "yes":
            ready.append(row)
    return ready


def export(out_dir: Path) -> list[Path]:
    pin = (lint_brain.ROOT / "brain" / "pin.md").read_text(encoding="utf-8")
    commit = lint_brain.pin_value(pin, "app_commit")
    account = lint_brain.pin_value(pin, "account_path")
    text = (lint_brain.ROOT / "brain" / "invariants.md").read_text(encoding="utf-8")
    out_dir.mkdir(parents=True, exist_ok=True)
    written = []
    for row in ready_rows(text):
        finding = to_finding(row, commit, account)
        path = out_dir / f"{row['id']}.json"
        path.write_text(json.dumps(finding, indent=2) + "\n", encoding="utf-8")
        written.append(path)
    return written


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Export file-ready open invariants as finding JSON.")
    parser.add_argument("--out", default="findings-out", help="Directory for the JSON files.")
    args = parser.parse_args(argv)
    out = Path(args.out)
    if not out.is_absolute():
        out = lint_brain.ROOT / out
    written = export(out)
    for path in written:
        print(path.name)
    print(f"{len(written)} findings")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
