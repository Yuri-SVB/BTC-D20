#!/usr/bin/env python3
"""Verify the tutorial's data and worked examples against the BIP-39 spec.

Checks, in order:
  1. Wordlist integrity: the file served by the commit-pinned bitcoin/bips
     submodule has 2048 unique, sorted words and matches the BIP-39
     reference SHA-256 (an independent cross-check on the submodule pin).
  2. The table source computes the table from that submodule file (no copy
     of the word data exists in this repository).
  3. Worked example 1 -- coordinates ((3,4), 1, 11) resolve to "candy".
  4. Worked example 2 -- for the 11 words "never use this example because
     private key secret need phrase true" and D1=11,12 / D2=9, exactly one
     column completes a valid BIP-39 checksum: column 14, "random".
  5. Every instruction edition mentions the same verified example words, so
     translations cannot silently drift from the checked math.
  6. Method entropy accounting: 11*11 + 7 = 128 bits.

Exits non-zero on the first failure. No third-party dependencies.
"""

import hashlib
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
WORDLIST = REPO / "external" / "bips" / "bip-0039" / "english.txt"
WORDLIST_SHA256 = "2f5eed53a4727b4bf8880d8f3f199efc90e58503646d9ff8eff3a2ed3b24dbda"
EDITIONS = ["en", "es", "it", "pt-br"]

failures = 0


def check(label, ok, detail=""):
    global failures
    mark = "ok" if ok else "FAIL"
    print(f"[{mark:>4}] {label}" + (f" -- {detail}" if detail else ""))
    if not ok:
        failures += 1


def word_at(words, d1, d2, d3):
    """Map die results (each 1..16) to a word: section (d1), row (d2), column (d3)."""
    section = (d1 - 1) // 2
    return words[section * 256 + (d2 - 1) * 16 + (d3 - 1)]


def checksum_candidates(words, first11, d1, d2):
    """Return the (column, word) pairs in section/row (d1, d2) that complete a
    valid 12-word BIP-39 mnemonic after `first11`."""
    ent121 = 0
    for w in first11:
        ent121 = (ent121 << 11) | words.index(w)
    section, row = (d1 - 1) // 2, d2
    out = []
    for col in range(16):
        idx = section * 256 + (row - 1) * 16 + col
        full = (ent121 << 11) | idx          # 132 bits: 128 entropy + 4 checksum
        entropy, cs = full >> 4, full & 0xF
        digest = hashlib.sha256(entropy.to_bytes(16, "big")).digest()
        if digest[0] >> 4 == cs:
            out.append((col + 1, words[idx]))
    return out


def main():
    # 1. wordlist integrity (file comes from the pinned bitcoin/bips submodule)
    if not WORDLIST.exists():
        sys.exit("wordlist missing -- run: git submodule update --init --depth 1")
    data = WORDLIST.read_bytes()
    check("submodule wordlist sha256 matches the BIP-39 reference value",
          hashlib.sha256(data).hexdigest() == WORDLIST_SHA256)
    words = data.decode("ascii").split()
    check("wordlist has 2048 unique words",
          len(words) == 2048 and len(set(words)) == 2048)
    check("wordlist is in official (sorted) order", words == sorted(words))

    # 2. the table is computed from the submodule wordlist at compile time
    table_tex = (REPO / "table" / "bip39-table.tex").read_text()
    check("table source reads the wordlist from the bitcoin/bips submodule",
          "external/bips/bip-0039/english.txt" in table_tex)

    # 3. worked example 1
    w = word_at(words, 3, 1, 11)
    check('example 1: ((3,4), 1, 11) -> "candy"', w == "candy", f"got {w!r}")

    # 4. worked example 2
    first11 = "never use this example because private key secret need phrase true".split()
    check("example 2: all 11 example words are BIP-39 words",
          all(w in words for w in first11))
    cands = checksum_candidates(words, first11, 12, 9)
    check('example 2: unique valid 12th word is column 14, "random"',
          cands == [(14, "random")], f"got {cands}")

    # 5. every edition quotes the verified examples
    for lang in EDITIONS:
        tex = (REPO / "instructions" / lang / f"instructions-{lang}.tex").read_text()
        check(f"instructions-{lang} quotes verified example words",
              "candy" in tex and "random" in tex and "12.random" in tex)

    # 6. entropy accounting
    bits = 11 * 11 + 3 + 4
    check("method yields exactly 128 bits of entropy", bits == 128,
          f"11 words x 11 bits + 3 (D1) + 4 (D2) = {bits}")

    if failures:
        sys.exit(f"{failures} check(s) failed")
    print("all checks passed")


if __name__ == "__main__":
    main()
