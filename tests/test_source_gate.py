from pathlib import Path
import unittest

from tools.valis_rebuild.errors import BuildError
from tools.valis_rebuild.source_gate import lint_all, require_buildable


ROOT = Path(__file__).resolve().parents[1]


class SourceGateTests(unittest.TestCase):
    def test_reviewed_source_tree_is_buildable(self):
        report = lint_all(ROOT)
        self.assertEqual(report["status"], "OK")
        self.assertTrue(report["source_manifest"]["buildable"])

    def test_buildable_gate_returns_manifest(self):
        report = require_buildable(ROOT)
        self.assertEqual(report["status"], "OK")


if __name__ == "__main__":
    unittest.main()
