#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate comment_format rules for converting ASCII romanization to Báⁿ-uā-ci̍ display

This script generates YAML comment_format rules that convert romanization like "saa3"
to proper Báⁿ-uā-ci̍ with Unicode combining characters like "sâ̤"

Usage:
    python generate_comment_format.py > comment_format_rules.yaml
"""

# Tone marks mapping (tone number → combining diacritic)
TONE_MARKS = {
    '2': '\u0301',  # ◌́ COMBINING ACUTE ACCENT
    '3': '\u0302',  # ◌̂ COMBINING CIRCUMFLEX ACCENT
    '4': '\u030D',  # ◌̍ COMBINING VERTICAL LINE ABOVE
    '5': '\u0304',  # ◌̄ COMBINING MACRON
    # Tone 1 is unmarked
    # Tones 7, 8 are entering tones (usually unmarked or with -h)
}

# Special vowel romanizations that need Unicode combining diacritics
SPECIAL_VOWELS = {
    'aa': 'a\u0324',  # a̤ (a + COMBINING DIAERESIS BELOW)
    'ee': 'e\u0324',  # e̤
    'oo': 'o\u0324',  # o̤
    'y': '\u1E73',    # ṳ (LATIN SMALL LETTER U WITH DIAERESIS BELOW)
}

# Nasal marker
NASAL_MARKER = {
    'nn': '\u207F',   # ⁿ (SUPERSCRIPT LATIN SMALL LETTER N)
}

def generate_tone_rules():
    """
    Generate rules to convert tone numbers to combining diacritics.

    The main vowel in each syllable needs the tone mark.
    Priority: a > o > e > i > u > y

    We need to handle patterns like:
    - ka2 → ká
    - saa3 → sâ̤ (but we do this in two steps: saa3 → sâa3, then âa → â̤)
    - guann2 → guáⁿ
    """
    rules = []

    # For each tone (2-5), we need to mark the main vowel
    # We'll process from back to front to find the tone number first

    for tone_num, tone_mark in TONE_MARKS.items():
        # Single vowel patterns (simplest case)
        # Pattern: consonants + single vowel + optional consonants + tone
        # Examples: ka2 → ká, si3 → sî
        for vowel in ['a', 'o', 'e', 'i', 'u', 'y']:
            # Match: any non-digit characters, then the vowel, then optional consonants, then the tone
            # We need to be careful with romanizations like "aa", "ee" etc.
            # So we match single vowels that are NOT preceded by the same vowel
            rules.append(f"    - xform/([^{vowel}aoeiu])({vowel})([^aoeiu0-9]*){tone_num}/$1$2{tone_mark}$3/")

        # Double vowel patterns (diphthongs and special romanizations)
        # For diphthongs, mark the first/main vowel according to priority
        # ai, au, ao, ei, eu, ia, io, iu, oa, oe, oi, ua, ue, ui, uo
        diphthong_patterns = [
            ('au', 'a'),  # áu
            ('ao', 'a'),  # áo
            ('ai', 'a'),  # ái
            ('ia', 'a'),  # iá
            ('ua', 'a'),  # uá
            ('oa', 'a'),  # oá
            ('oi', 'o'),  # ói
            ('ou', 'o'),  # óu
            ('oe', 'o'),  # óe
            ('io', 'o'),  # ió
            ('uo', 'o'),  # uó
            ('ei', 'e'),  # éi
            ('eu', 'e'),  # éu
            ('ue', 'e'),  # ué
            ('iu', 'u'),  # iú
            ('ui', 'u'),  # uí
            # Special romanizations (will be converted to Unicode later)
            ('aa', 'a'),  # â̤ (mark the 'a')
            ('ee', 'e'),  # ê̤
            ('oo', 'o'),  # ô̤
        ]

        for diphthong, main_vowel in diphthong_patterns:
            # Find the position of main vowel in diphthong
            pos = diphthong.index(main_vowel)
            if pos == 0:
                # Mark first vowel: xform/ia2/íaá/ → ia with tone on i
                before = ''
                after = diphthong[1:]
                rules.append(f"    - xform/([^aoeiu])({diphthong})([^aoeiu0-9]*){tone_num}/$1{main_vowel}{tone_mark}{after}$3/")
            else:
                # Mark second vowel: xform/ai2/aí/
                before = diphthong[:pos]
                after = diphthong[pos+1:]
                rules.append(f"    - xform/([^aoeiu])({diphthong})([^aoeiu0-9]*){tone_num}/$1{before}{main_vowel}{tone_mark}{after}$3/")

    return rules

def generate_special_char_rules():
    """
    Generate rules to convert ASCII romanizations to Unicode combining characters.
    These should be applied AFTER tone marks are added.
    """
    rules = []

    # Convert special vowels
    # aa → a̤ (but preserve any tone marks already added)
    # Pattern: we need to handle both "aa" and "áa", "âa" etc.

    # For aa → a̤, we need to handle: a, á, â, a̍, ā followed by 'a'
    for special, unicode_char in SPECIAL_VOWELS.items():
        if special in ['aa', 'ee', 'oo']:
            base_vowel = special[0]
            # Match base vowel (possibly with tone mark) + second vowel
            # Use ́̂̍̄ to match any tone mark
            rules.append(f"    - xform/{base_vowel}([́̂̍̄]?){base_vowel}/{unicode_char}$1/")
        elif special == 'y':
            # Convert standalone 'y' to ṳ (but not 'ny' etc in middle of word)
            # Match word boundary or after consonant
            rules.append(f"    - xform/([^aoeiu]|^)y([́̂̍̄]?)([^aoeiu]|$)/$1{unicode_char}$2$3/")

    # Convert nasal marker: nn → ⁿ
    rules.append(f"    - xform/nn/{NASAL_MARKER['nn']}/")

    # Remove remaining tone numbers (tone 1, 7, 8 which are unmarked)
    rules.append(f"    - xform/[1-8]//")

    return rules

def generate_all_rules(output_file=None):
    """Generate all comment_format rules."""
    import sys

    # Set output to file or stdout with UTF-8 encoding
    if output_file:
        f = open(output_file, 'w', encoding='utf-8')
    else:
        import io
        f = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', newline='\n')

    try:
        f.write("# Generated comment_format rules for Báⁿ-uā-ci̍\n")
        f.write("# Copy these rules into the comment_format section of your schema file\n")
        f.write("\n")
        f.write("comment_format:\n")
        f.write("  # Step 1: Add hyphens between syllables for readability\n")
        f.write("  - xform/ /-/g\n")
        f.write("\n")
        f.write("  # Step 2: Convert tone numbers to combining diacritics\n")

        tone_rules = generate_tone_rules()
        for rule in tone_rules:
            f.write(rule + "\n")

        f.write("\n")
        f.write("  # Step 3: Convert special romanizations to Unicode combining characters\n")

        special_rules = generate_special_char_rules()
        for rule in special_rules:
            f.write(rule + "\n")
    finally:
        if output_file:
            f.close()

if __name__ == '__main__':
    import sys
    output_file = sys.argv[1] if len(sys.argv) > 1 else None
    generate_all_rules(output_file)
