import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

import lint_brain


class LintBrainTest(unittest.TestCase):
    def test_brain_is_consistent(self):
        self.assertEqual(lint_brain.check(), [])

    def test_bad_bullet_is_reported(self):
        text = "### INV-EXAMPLE\n- lane: signer\n- wrong: x\n"
        _, rows = lint_brain.parse_invariants(text)
        self.assertEqual(rows[0]["error"], "bullet impact missing")


if __name__ == "__main__":
    unittest.main()
