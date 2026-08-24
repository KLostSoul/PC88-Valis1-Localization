import unittest

from tools.build_valis1 import (
    Operation,
    apply_operations,
    parse_range,
    sub_to_d88,
    token_pair_bytes,
    visualtxt_glyph,
)


class SourceBuildTests(unittest.TestCase):
    def test_token_pairs_are_read_in_order(self):
        self.assertEqual(token_pair_bytes("1011 007F"), bytes.fromhex("1011007F"))

    def test_ranges_are_explicit_hex_ranges(self):
        self.assertEqual(parse_range("0x4B6A~0x59DD"), (0x4B6A, 0x59DD))

    def test_gameover_sub_to_d88_mapping(self):
        raw, encoded = sub_to_d88(0x4400, 0x00)
        self.assertEqual(raw, 0x7E0F)
        self.assertEqual(encoded, 0xC7)

    def test_visualtxt_is_16_by_16_one_bit_per_pixel(self):
        text = "; slot metadata\n" + "\n".join(["■" * 16] * 16)
        self.assertEqual(visualtxt_glyph(text), bytes([0xFF] * 32))

    def test_apply_operations_checks_declared_old_bytes(self):
        data = bytearray([0x10, 0x20])
        report = apply_operations(data, [Operation("test", "fixture", 0, 0x11, 0x10, "")])
        self.assertEqual(data, bytearray([0x11, 0x20]))
        self.assertEqual(report["changed_bytes"], 1)

    def test_apply_operations_rejects_conflicting_sources(self):
        with self.assertRaises(ValueError):
            apply_operations(
                bytearray([0x00]),
                [
                    Operation("test", "first", 0, 0x01, None, ""),
                    Operation("test", "second", 0, 0x02, None, ""),
                ],
            )


if __name__ == "__main__":
    unittest.main()
