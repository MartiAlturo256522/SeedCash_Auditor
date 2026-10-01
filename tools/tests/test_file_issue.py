import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

import file_issue
import gates


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
        "title": "Overview headline uses the output sum",
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
    }
    finding.update(stamp())
    finding.update(overrides)
    return finding


class FileIssueTest(unittest.TestCase):
    def setUp(self):
        self.calls = []
        self.original = file_issue.run_gh

        def fake_gh(args):
            self.calls.append(list(args))
            if "list" in args:
                return subprocess.CompletedProcess(args, 0, "[]", "")
            return subprocess.CompletedProcess(args, 0, "https://example.test/1\n", "")

        file_issue.run_gh = fake_gh

    def tearDown(self):
        file_issue.run_gh = self.original
        os.environ.pop(file_issue.CONFIRM_ENV, None)

    def write_finding(self, finding):
        handle = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8")
        json.dump(finding, handle)
        handle.close()
        self.addCleanup(lambda: Path(handle.name).unlink(missing_ok=True))
        return handle.name

    def test_dry_run_does_not_create(self):
        path = self.write_finding(sample())
        code = file_issue.main(["--finding", path])
        self.assertEqual(code, 0)
        self.assertTrue(any(call[1] == "issue" and "list" in call for call in self.calls))
        self.assertFalse(any("create" in call for call in self.calls))

    def test_confirm_without_gates_refuses(self):
        path = self.write_finding(sample(gates={}, gate_evidence={}))
        os.environ[file_issue.CONFIRM_ENV] = "yes"
        with self.assertRaises(SystemExit) as caught:
            file_issue.main(["--finding", path, "--confirm"])
        self.assertEqual(caught.exception.code, 2)
        self.assertFalse(any("create" in call for call in self.calls))

    def test_confirm_without_env_refuses(self):
        path = self.write_finding(sample())
        with self.assertRaises(SystemExit) as caught:
            file_issue.main(["--finding", path, "--confirm"])
        self.assertEqual(caught.exception.code, 2)
        self.assertFalse(any("create" in call for call in self.calls))

    def test_confirm_creates_with_argv_list(self):
        path = self.write_finding(sample())
        os.environ[file_issue.CONFIRM_ENV] = "yes"
        code = file_issue.main(["--finding", path, "--confirm"])
        self.assertEqual(code, 0)
        created = [call for call in self.calls if "create" in call]
        self.assertEqual(len(created), 1)
        self.assertIsInstance(created[0], list)
        self.assertEqual(created[0][0], "gh")
        self.assertIn("--body-file", created[0])

    def test_os_finding_needs_explicit_repo(self):
        path = str(ROOT / "examples" / "version-string.json")
        with self.assertRaises(SystemExit) as caught:
            file_issue.main(["--finding", path])
        self.assertEqual(caught.exception.code, 2)

    def test_forbidden_key_refuses(self):
        path = self.write_finding(sample(payload="nope"))
        with self.assertRaises(SystemExit) as caught:
            file_issue.main(["--finding", path])
        self.assertEqual(caught.exception.code, 2)

    def test_closed_finding_refuses(self):
        path = self.write_finding(sample(status="closed", issue_ready=False))
        with self.assertRaises(SystemExit) as caught:
            file_issue.main(["--finding", path])
        self.assertEqual(caught.exception.code, 2)

    def test_body_has_required_sections(self):
        body = file_issue.render_body(sample())
        for section in ("## Broken check", "## Impact class", "## Where", "## Fix direction", "## Evidence"):
            self.assertIn(section, body)
        self.assertNotIn("reproduc", body.lower())
        self.assertNotIn("payload", body.lower())


if __name__ == "__main__":
    unittest.main()
