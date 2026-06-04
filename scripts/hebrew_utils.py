#!/usr/bin/env python3
"""
Hebrew text normalization utilities for Torah Knowledge Graph.

Removes cantillation marks (ta'amim), nikud (vowels), normalizes maqaf,
collapses extra whitespace, preserves final letters.

Usage:
    from hebrew_utils import normalize_hebrew
    clean = normalize_hebrew("בְּרֵאשִׁ֖ית בָּרָ֣א אֱלֹהִ֑ים...")
    # => "בראשית ברא אלהים את השמים ואת הארץ"
"""

import re
import unicodedata


# Hebrew cantillation marks (Ta'amei HaMikra) — U+0591 through U+05AF
HEBREW_CANTILLATION_RANGE = range(0x0591, 0x05AF + 1)

# Hebrew vowels / points (Niqqud) — U+05B0 through U+05BD, U+05BF, U+05C1, U+05C2, U+05C4, U+05C5, U+05C7
HEBREW_POINTS = set([
    0x05B0, 0x05B1, 0x05B2, 0x05B3, 0x05B4, 0x05B5, 0x05B6, 0x05B7,
    0x05B8, 0x05B9, 0x05BA, 0x05BB, 0x05BC, 0x05BD, 0x05BF,
    0x05C1, 0x05C2, 0x05C4, 0x05C5, 0x05C7,
])

# Dagesh / shin/sin dots are U+05BC (dagesh), U+05C1 (shin dot), U+05C2 (sin dot)
# We keep dagesh as it affects pronunciation but remove shin/sin dots
HEBREW_REMOVE = set(HEBREW_CANTILLATION_RANGE) | HEBREW_POINTS


def normalize_hebrew(raw: str) -> str:
    """
    Normalize Hebrew text by removing cantillation marks and vowel points,
    normalizing maqaf to regular hyphen, collapsing whitespace.

    Preserves:
        - Hebrew letters (including final forms)
        - Spaces
        - Regular punctuation
    """
    if not raw:
        return ""

    # Step 1: Remove cantillation marks and nikud
    cleaned = "".join(
        ch for ch in raw
        if ord(ch) not in HEBREW_REMOVE
    )

    # Step 2: Normalize maqaf (U+05BE) to regular hyphen
    cleaned = cleaned.replace("־", "-")

    # Step 3: Normalize punctuation: remove sof pasuq / paseq
    cleaned = cleaned.replace("׃", "")  # Sof pasuq
    cleaned = cleaned.replace("׀", "")  # Paseq (vertical bar)

    # Step 4: Collapse multiple spaces and strip
    cleaned = re.sub(r"\s+", " ", cleaned).strip()

    return cleaned


def strip_cantillation_only(raw: str) -> str:
    """
    Remove only cantillation marks, preserving nikud.
    Useful when you want vowels but not musical signs.
    """
    if not raw:
        return ""
    return "".join(
        ch for ch in raw
        if ord(ch) not in set(HEBREW_CANTILLATION_RANGE)
    )


if __name__ == "__main__":
    # Self-test
    samples = [
        ("בְּרֵאשִׁ֖ית בָּרָ֣א אֱלֹהִ֑ים אֵ֥ת הַשָּׁמַ֖יִם וְאֵ֥ת הָאָֽרֶץ׃", "בראשית ברא אלהים את השמים ואת הארץ"),
        ("וַיֹּאמֶר֩ אֱלֹהִ֗ים", "ויאמר אלהים"),
        ("שְׁמַ֖ע יִשְׂרָאֵ֑ל", "שמע ישראל"),
    ]

    print("=== Hebrew Normalization Tests ===\n")
    for raw, expected in samples:
        result = normalize_hebrew(raw)
        status = "✅" if result == expected else "❌"
        print(f"{status} Input:    {raw}")
        print(f"   Expected: {expected}")
        print(f"   Got:      {result}")
        print()
