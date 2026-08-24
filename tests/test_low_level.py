import unittest

from tools.valis_rebuild.codec import decode_block, encode_block


class LowLevelTests(unittest.TestCase):
    def test_explicit_reverse_codec_round_trip(self):
        decoded = bytes((i * 19 + 7) & 0xFF for i in range(0x400))
        raw = encode_block(decoded, 0x3A)
        self.assertEqual(decode_block(raw, 0x3A), decoded)


if __name__ == "__main__":
    unittest.main()

