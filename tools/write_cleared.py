#!/usr/bin/env python3
"""Write cleared findings only when every upload gate already passed.

The workflow decides the gates. This tool rejects a file that does not
carry all eight, with the evidence phrases the layers have to produce.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import file_issue
import gates

INV_RE = re.compile(r"^[A-Z][A-Z0-9-]{0,40}$")


def write_cleared(source: Path, dest: Path) -> tuple[int, int]:
    raw = json.loads(source.read_text(encoding="utf-8"))
    if not isinstance(raw, list):
        file_issue.refuse("cleared input must be a JSON list")
    dest.mkdir(parents=True, exist_ok=True)
    kept = 0
    rejected = 0
    for index, item in enumerate(raw):
        label = item.get("invariant_id") if isinstance(item, dict) else "?"
        if not isinstance(item, dict) or not gates.gates_ok(item):
            rejected += 1
            print(f"reject {label}")
            continue
        name = str(item.get("invariant_id") or "")
        if not INV_RE.match(name):
            name = f"FINDING-{index}"
        (dest / f"{name}.json").write_text(json.dumps(item, indent=2) + "\n", encoding="utf-8")
        kept += 1
        print(f"cleared {name}")
    print(f"cleared={kept} rejected={rejected}")
    return kept, rejected


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Write findings that passed every upload gate.")
    parser.add_argument("--src", required=True, help="JSON list of gated findings.")
    parser.add_argument("--out", default="cleared", help="Directory to write.")
    args = parser.parse_args(argv)
    root = file_issue.repo_root()
    source = Path(args.src)
    dest = Path(args.out)
    if not source.is_absolute():
        source = root / source
    if not dest.is_absolute():
        dest = root / dest
    kept, rejected = write_cleared(source, dest)
    if kept == 0:
        return 2
    if rejected:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
