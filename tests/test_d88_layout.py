import os
from pathlib import Path
import unittest

from tools.valis_rebuild.d88 import D88Image


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_D88 = ROOT.parent / "upload" / "Mugen Senshi Valis (1986)(Nihon Telenet)(Disk 1 of 2)(1).d88"
D88_PATH = Path(os.environ.get("VALIS_ORIGINAL_D88", DEFAULT_D88))


@unittest.skipUnless(D88_PATH.exists(), "original D88 is not supplied")
class D88LayoutTests(unittest.TestCase):
    def test_original_geometry_only(self):
        image = D88Image.read(D88_PATH)
        self.assertEqual(len(image.data), 414_992)
        self.assertEqual(len(image.sectors), 422)
        self.assertEqual(len(image.flatten_payload()), 407_552)


if __name__ == "__main__":
    unittest.main()

