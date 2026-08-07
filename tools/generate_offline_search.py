#!/usr/bin/env python3

from pathlib import Path
import hashlib
import sys


ROOT = Path(__file__).resolve().parent.parent

WORDLIST = ROOT / "external" / "bips" / "bip-0039" / "english.txt"
TEMPLATE = ROOT / "tools" / "offline-search.template.html"
OUTPUT = ROOT / "dist" / "offline-search.html"

EXPECTED_SHA256 = (
    "2f5eed53a4727b4bf8880d8f3f199efc90e58503646d9ff8eff3a2ed3b24dbda"
)

PLACEHOLDER = "__BIP39_WORDLIST__"


def main():

    if not WORDLIST.exists():
        sys.exit(f"Wordlist not found: {WORDLIST}")

    if not TEMPLATE.exists():
        sys.exit(f"Template not found: {TEMPLATE}")

    # Read the official BIP-39 wordlist.
    # Normalize line endings so the hash is identical on
    # Windows, Linux and macOS.
    words = WORDLIST.read_text(
        encoding="utf-8"
    ).splitlines()

    normalized_wordlist = "\n".join(words) + "\n"

    digest = hashlib.sha256(
        normalized_wordlist.encode("utf-8")
    ).hexdigest()

    if digest != EXPECTED_SHA256:
        sys.exit(
            "BIP-39 wordlist SHA-256 mismatch.\n"
            f"Expected: {EXPECTED_SHA256}\n"
            f"Found:    {digest}"
        )

    if len(words) != 2048:
        sys.exit(
            f"Expected 2048 BIP-39 words, found {len(words)}."
        )

    template = TEMPLATE.read_text(
        encoding="utf-8"
    )

    if PLACEHOLDER not in template:
        sys.exit(
            f"Placeholder {PLACEHOLDER!r} not found in template."
        )

    html = template.replace(
        PLACEHOLDER,
        "\n".join(words)
    )

    OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    OUTPUT.write_text(
        html,
        encoding="utf-8",
        newline="\n"
    )

    print(f"Generated {OUTPUT}")
    print(f"BIP-39 words: {len(words)}")
    print(f"SHA-256: {digest}")


if __name__ == "__main__":
    main()