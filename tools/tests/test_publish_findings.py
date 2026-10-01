import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

import export_findings
import file_issue
import gates
import lint_brain
import list_issues
import publish_findings
import write_cleared

FORBIDDEN = ("steps to reproduce", "proof of concept", "exploit", "payload")


def stamp():
    evidence = {
        "quote": "The quoted lines still show the broken check in the named function.",
        "reach": "The overview caller reaches the signer with this amount on screen.",
        "impact": "The disclosure class wysiwys matches bytes the screen did not show.",
        "bch": "BCH sighash commits to the output amount, so the class stays wysiwys.",
        "domain": "perspective: wysiwys. The overview still feeds the output sum forward.",
        "experience": "SeedSigner shows the input sum on its own line in the overview.",
        "prior_issues": "no matching issue on SeedCashOrg/seedcash for this overview check.",
        "counter": "A refutation that the headline is the documented input sum failed.",
    }
    return {
        "gates": {name: True for name in gates.REQUIRED_GATES},
        "gate_evidence": evidence,
    }


def sample(**overrides):
    finding = {
        "lane": "wysiwys",
        "title": "INV-OVERVIEW-AMOUNT: Overview headline uses the output sum",
        "invariant_id": "INV-OVERVIEW-AMOUNT",
        "status": "open",
        "issue_ready": True,
        "file": "src/seedcash/views/psbt_views.py",
        "function": "BCHPSBTOverviewView.run",
        "broken_check": "The overview is called with inputs_amount set to output_amount.",
        "impact_class": "wysiwys",
        "fix_direction": "Pass the input sum into the headline.",
        "evidence": "inputs_amount=psbt_parser.output_amount",
        "commit": "364cccc",
        "severity": "high",
        "dedupe_terms": ["INV-OVERVIEW-AMOUNT"],
    }
    finding.update(stamp())
    finding.update(overrides)
    return finding


class ExportFindingsTest(unittest.TestCase):
    def test_colon_pass_condition_is_the_fix(self):
        broken, fix = export_findings.split_check(
            "The resolver returns on the first key. The pass condition is: prefer the parent."
        )
        self.assertEqual(broken, "The resolver returns on the first key.")
        self.assertEqual(fix, "prefer the parent")

    def test_exports_only_open_file_ready(self):
        text = (ROOT / "brain" / "invariants.md").read_text(encoding="utf-8")
        _, rows = lint_brain.parse_invariants(text)
        expected = {
            row["id"]
            for row in rows
            if not row.get("error")
            and row["meta"]["status_at_pin"] == "open"
            and row["meta"]["file_ready"] == "yes"
        }
        held_back = {
            row["id"]
            for row in rows
            if row["id"] not in expected
        }
        with tempfile.TemporaryDirectory() as tmp:
            written = export_findings.export(Path(tmp))
            exported = {}
            for path in written:
                exported[path.stem] = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(set(exported), expected)
        self.assertTrue(held_back.isdisjoint(exported))
        self.assertGreaterEqual(len(exported), 1)
        for inv_id, finding in exported.items():
            self.assertEqual(finding["status"], "open")
            self.assertIs(finding["issue_ready"], True)
            self.assertLessEqual(len(finding["title"]), 120)
            self.assertEqual(finding["commit"], "364cccc")
            self.assertIn(inv_id, finding["dedupe_terms"])
            self.assertNotEqual(finding["fix_direction"], "Restore the check named by this invariant.")
            self.assertNotIn("brain/pin.md", finding["fix_direction"])
            blob = json.dumps(finding).lower()
            if inv_id not in export_findings.ALREADY_OPEN:
                for phrase in FORBIDDEN:
                    self.assertNotIn(phrase, blob, inv_id)
        self.assertIn("m/44'/145'/0'", exported["INV-DERIVATION-BINDING"]["fix_direction"])
        self.assertEqual(exported["INV-OS-LAG"]["file"], "seedcash-os")


class PublishFindingsTest(unittest.TestCase):
    def setUp(self):
        self.calls = []
        self.original = file_issue.run_gh
        self.titles = [
            {"number": 81, "title": "SC1-57 SCHNORR USES A DIFFERENT TAG"},
        ]

        def fake_gh(args):
            self.calls.append(list(args))
            if "list" in args:
                return subprocess.CompletedProcess(args, 0, json.dumps(self.titles), "")
            if "create" in args:
                return subprocess.CompletedProcess(args, 0, "https://example.test/new\n", "")
            return subprocess.CompletedProcess(args, 1, "", "unexpected gh")

        file_issue.run_gh = fake_gh

    def tearDown(self):
        file_issue.run_gh = self.original
        os.environ.pop(file_issue.CONFIRM_ENV, None)

    def write_dir(self, findings):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        root = Path(directory.name)
        for finding in findings:
            (root / f"{finding['invariant_id']}.json").write_text(
                json.dumps(finding), encoding="utf-8"
            )
        return root

    def test_dry_run_skips_known_open_title_and_does_not_create(self):
        root = self.write_dir(
            [
                sample(
                    invariant_id="INV-SCHNORR-TAG",
                    title="INV-SCHNORR-TAG: Schnorr tag length differs",
                    lane="signer",
                    impact_class="spec-deviation",
                    severity="low",
                    dedupe_terms=["INV-SCHNORR-TAG", "SCHNORR USES A DIFFERENT TAG"],
                ),
                sample(),
            ]
        )
        code = publish_findings.main(["--dir", str(root), "--repo", "SeedCashOrg/seedcash"])
        self.assertEqual(code, 0)
        self.assertFalse(any("create" in call for call in self.calls))
        created_findings = [
            call for call in self.calls if "create" in call or "--finding" in call
        ]
        self.assertFalse(any("INV-SCHNORR-TAG" in " ".join(call) for call in created_findings))

    def test_ungated_finding_is_refused_without_create(self):
        root = self.write_dir([sample(gates={}, gate_evidence={})])
        code = publish_findings.main(["--dir", str(root), "--repo", "SeedCashOrg/seedcash"])
        self.assertEqual(code, 1)
        self.assertFalse(any("create" in call for call in self.calls))

    def test_confirm_without_env_exits_before_create(self):
        root = self.write_dir([sample()])
        with self.assertRaises(SystemExit) as caught:
            publish_findings.main(
                ["--dir", str(root), "--repo", "SeedCashOrg/seedcash", "--confirm"]
            )
        self.assertEqual(caught.exception.code, 2)
        self.assertFalse(any("create" in call for call in self.calls))


class IssueToolsTest(unittest.TestCase):
    def test_list_issues_never_creates(self):
        calls = []
        original = file_issue.run_gh

        def fake_gh(args):
            calls.append(list(args))
            body = json.dumps([{"number": 81, "title": "schnorr tag", "state": "open"}])
            return subprocess.CompletedProcess(args, 0, body, "")

        file_issue.run_gh = fake_gh
        try:
            code = list_issues.main(["--repo", "SeedCashOrg/seedcash", "--state", "all"])
        finally:
            file_issue.run_gh = original
        self.assertEqual(code, 0)
        self.assertEqual(len(calls), 1)
        self.assertNotIn("create", calls[0])
        self.assertIn("all", calls[0])

    def test_write_cleared_rejects_a_draft_without_gates(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "batch.json"
            source.write_text(json.dumps([sample(gates={}, gate_evidence={})]), encoding="utf-8")
            kept, rejected = write_cleared.write_cleared(source, root / "out")
        self.assertEqual(kept, 0)
        self.assertEqual(rejected, 1)

    def test_write_cleared_keeps_a_stamped_finding(self):
        self.assertTrue(gates.gates_ok(sample()))
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "batch.json"
            source.write_text(json.dumps([sample()]), encoding="utf-8")
            kept, rejected = write_cleared.write_cleared(source, root / "out")
            written = list((root / "out").glob("*.json"))
        self.assertEqual((kept, rejected), (1, 0))
        self.assertEqual(len(written), 1)
