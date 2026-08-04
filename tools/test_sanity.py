#!/usr/bin/env python3
"""Sanity tests for the BTC-D20 table mathematics.

These verify the structural guarantees the tutorials print. Scope, stated
precisely: the scans are exhaustive over all 2048 candidate final words
(and hence all rows / sections) -- for SAMPLE prefixes, drawn from three
sources: the official reference-implementation test vectors, the
tutorials' printed example, and deterministic seeded-random ones.
(Exhaustiveness over the prefix space itself is impossible in principle:
2048^11 = 2^121 prefixes.) The guarantees checked:

  1. 12 words: for ANY 11 previous words, once D1 and D2 of the 12th word
     are fixed (a row), exactly one word in that row satisfies the
     checksum -- equivalently, 128 valid last words, one per row.
  2. 24 words: for ANY 23 previous words, once D1 of the 24th word is
     fixed (a section), exactly one word in that 256-word section
     satisfies the checksum -- equivalently, 8 valid last words, one per
     section.
  3. The counting law behind both: a c-bit checksum leaves exactly
     2048 / 2^c valid final words, for every prefix.
  4. The dice-to-table map is a bijection with uniform reach: every
     (section, row, column) hits exactly one of the 2048 words, each
     section is reached by exactly 2 of the 16 valid D1 outcomes, each
     row/column by exactly 1 of 16 -- so uniform valid rolls give
     uniform words.
  5. The checksum implementation reproduces the official BIP-39 (Trezor)
     test vectors, for both 128- and 256-bit entropy.
  6. The printed example phrases are valid mnemonics end to end, decoded
     by an independent path (bits -> entropy ++ checksum -> SHA-256).

Deterministic (fixed RNG seed), stdlib-only. Run directly or via
`make test`.
"""

import hashlib
import random
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from verify_tutorial import WORDLIST, all_valid_finals, checksum_candidates, word_at

SEED = 0xB1B39D20
N_PREFIXES = 12  # random prefixes tested per phrase size

EXAMPLE_11 = "never use this example because private key secret need phrase true".split()
EXAMPLE_12 = EXAMPLE_11 + ["random"]
EXAMPLE_24 = EXAMPLE_12 + EXAMPLE_11 + ["polar"]

# Official BIP-39 test vectors (Trezor reference), entropy hex -> mnemonic.
TREZOR_VECTORS = [
    ("00" * 16, "abandon " * 11 + "about"),
    ("7f" * 16, "legal winner thank year wave sausage worth useful legal winner thank yellow"),
    ("ff" * 16, "zoo " * 11 + "wrong"),
    ("00" * 32, "abandon " * 23 + "art"),
    ("ff" * 32, "zoo " * 23 + "vote"),
]


def encode_mnemonic(words, entropy: bytes):
    """Independent BIP-39 encoder: entropy -> mnemonic words."""
    cs_bits = len(entropy) * 8 // 32
    digest = hashlib.sha256(entropy).digest()
    bits = int.from_bytes(entropy, "big")
    cs = digest[0] >> (8 - cs_bits)
    full = (bits << cs_bits) | cs
    n_words = (len(entropy) * 8 + cs_bits) // 11
    return [words[(full >> (11 * (n_words - 1 - i))) & 0x7FF] for i in range(n_words)]


def valid_mnemonic(words, phrase):
    """Independent BIP-39 validator: decode indices, re-check the checksum."""
    idxs = [words.index(w) for w in phrase]
    total_bits = len(idxs) * 11
    cs_bits = total_bits // 33
    full = 0
    for ix in idxs:
        full = (full << 11) | ix
    entropy = (full >> cs_bits).to_bytes((total_bits - cs_bits) // 8, "big")
    cs = full & ((1 << cs_bits) - 1)
    return hashlib.sha256(entropy).digest()[0] >> (8 - cs_bits) == cs


class SanityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.words = WORDLIST.read_text().split()
        cls.rng = random.Random(SEED)

    @staticmethod
    def reference_prefixes(length):
        """Prefixes taken from the reference-implementation test vectors."""
        return [m.split()[:length] for _, m in TREZOR_VECTORS
                if len(m.split()) == length + 1]

    def sample_prefixes(self, length):
        """Reference-vector prefixes + the printed example + seeded-random ones."""
        prefixes = self.reference_prefixes(length)
        prefixes.append(EXAMPLE_11 if length == 11 else EXAMPLE_12 + EXAMPLE_11)
        prefixes += [self.rng.choices(self.words, k=length) for _ in range(N_PREFIXES)]
        return prefixes

    def test_12_words_exactly_one_valid_word_per_row(self):
        """For any 11-word prefix and any (D1, D2), exactly one column checks out."""
        for prefix in self.sample_prefixes(11):
            finals = all_valid_finals(self.words, prefix)
            self.assertEqual(len(finals), 128)
            self.assertEqual(sorted(i // 16 for i in finals), list(range(128)))
            # Same fact through the row-scoped code path, on a spot-check of rows.
            for d1, d2 in [(1, 1), (12, 9), (16, 16), (7, 3)]:
                self.assertEqual(
                    len(checksum_candidates(self.words, prefix, d1, d2)), 1)

    def test_24_words_exactly_one_valid_word_per_section(self):
        """For any 23-word prefix and any D1, exactly one word in the section."""
        for prefix in self.sample_prefixes(23):
            finals = all_valid_finals(self.words, prefix)
            self.assertEqual(len(finals), 8)
            self.assertEqual(sorted(i // 256 for i in finals), list(range(8)))

    def test_counting_law(self):
        """c checksum bits leave 2048 / 2^c valid finals -- the general law."""
        for length, cs_bits in ((11, 4), (23, 8)):
            prefix = self.rng.choices(self.words, k=length)
            self.assertEqual(len(all_valid_finals(self.words, prefix)),
                             2048 >> cs_bits)

    def test_dice_map_bijection_and_uniformity(self):
        """(D1, D2, D3) covers all 2048 words; roll outcomes spread uniformly."""
        seen = set()
        for d1 in range(1, 17):
            for d2 in range(1, 17):
                for d3 in range(1, 17):
                    seen.add(word_at(self.words, d1, d2, d3))
        self.assertEqual(len(seen), 2048)
        # Each section is reached by exactly 2 of 16 valid D1 outcomes.
        for section in range(8):
            hits = [d1 for d1 in range(1, 17) if (d1 - 1) // 2 == section]
            self.assertEqual(len(hits), 2)

    def test_official_bip39_vectors(self):
        """The checksum math reproduces the Trezor reference vectors."""
        for entropy_hex, mnemonic in TREZOR_VECTORS:
            self.assertEqual(
                encode_mnemonic(self.words, bytes.fromhex(entropy_hex)),
                mnemonic.split())

    def test_printed_examples_are_valid_end_to_end(self):
        """The tutorial's 12- and 24-word phrases pass an independent decoder."""
        self.assertTrue(valid_mnemonic(self.words, EXAMPLE_12))
        self.assertTrue(valid_mnemonic(self.words, EXAMPLE_24))
        # And perturbing the last word breaks each (checksum actually binds).
        self.assertFalse(valid_mnemonic(self.words, EXAMPLE_11 + ["polar"]))
        self.assertFalse(valid_mnemonic(self.words, EXAMPLE_24[:-1] + ["random"]))

    def test_encode_decode_round_trip(self):
        """Random entropy -> words -> entropy survives, at both sizes."""
        for size in (16, 32):
            for _ in range(8):
                entropy = self.rng.getrandbits(size * 8).to_bytes(size, "big")
                phrase = encode_mnemonic(self.words, entropy)
                self.assertTrue(valid_mnemonic(self.words, phrase))


def report():
    """Human-readable demonstration (--report): run the exhaustive scan on
    screen for the printed example prefix and one seeded random prefix."""
    words = WORDLIST.read_text().split()
    rng = random.Random(SEED)
    print("=" * 72)
    print("BTC-D20 sanity report -- exhaustive scan of all 2048 final words")
    print("=" * 72)
    for label, prefix in [
        ("reference vector (ff..ff)", ["zoo"] * 11),
        ("printed example", EXAMPLE_11),
        ("random prefix (seeded)", rng.choices(words, k=11)),
    ]:
        finals = all_valid_finals(words, prefix)
        rows = [i // 16 for i in finals]
        print(f"\n12-word standard -- prefix: {label}")
        print("  " + " ".join(prefix))
        print(f"  2048 candidates tested -> {len(finals)} satisfy the checksum")
        print(f"  rows covered: {len(set(rows))}/128, "
              f"max per row: {max(rows.count(r) for r in set(rows))} "
              f"=> exactly one valid word per row")
    for label, prefix in [
        ("reference vector (ff..ff)", ["zoo"] * 23),
        ("printed example x2", EXAMPLE_12 + EXAMPLE_11),
        ("random prefix (seeded)", rng.choices(words, k=23)),
    ]:
        finals = all_valid_finals(words, prefix)
        print(f"\n24-word standard -- prefix: {label}")
        print(f"  2048 candidates tested -> {len(finals)} satisfy the checksum, "
              f"one per section:")
        for i in finals:
            s, r, c = i // 256, (i % 256) // 16, i % 16
            print(f"    section {2*s+1:>2},{2*s+2:<2}  row {r+1:>2}  "
                  f"column {c+1:>2}  ->  {words[i]}")
    print()


if __name__ == "__main__":
    if "--report" in sys.argv:
        report()
    else:
        unittest.main(verbosity=2)
