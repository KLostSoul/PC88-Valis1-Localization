import tempfile
import unittest
from pathlib import Path

from tools.reproduce_valis1 import apply_ips, inspect_ips, parse_ips


ROOT = Path(__file__).resolve().parents[1]


class IpsTests(unittest.TestCase):
    def test_repository_ips_are_known(self):
        disk = inspect_ips("disk", ROOT / "patches/Valis_Korean_Disk_A_Patch_Ver_1.02.ips", False)
        kanji = inspect_ips("kanji", ROOT / "patches/VALIS_KANJI1_ROM_Patch_Ver_1.02.ips", False)
        self.assertEqual(disk["records"], 1282)
        self.assertEqual(kanji["record_slots_touched"], 476)

    def test_raw_and_rle_records_apply_without_resize(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "fixture.ips"
            path.write_bytes(
                b"PATCH"
                + bytes.fromhex("0000010002AABB")
                + bytes.fromhex("00000400000003CC")
                + b"EOF"
            )
            blob, records = parse_ips(path)
            result = apply_ips(bytes(8), records)
            self.assertEqual(blob[:5], b"PATCH")
            self.assertEqual(result, bytes.fromhex("00AABB00CCCCCC00"))


if __name__ == "__main__":
    unittest.main()
