#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate comment_format rules for converting ASCII romanization to Báⁿ-uā-ci̍ display

This script generates YAML comment_format rules that convert romanization like "saa3"
to proper Báⁿ-uā-ci̍ with Unicode combining characters like "sâ̤"
"""

# Tone marks mapping (tone number → combining diacritic)
TONE_MARKS = {
    '2': '\u0301',  # ◌́ COMBINING ACUTE ACCENT
    '3': '\u0302',  # ◌̂ COMBINING CIRCUMFLEX ACCENT
    '4': '\u030D',  # ◌̍ COMBINING VERTICAL LINE ABOVE
    '5': '\u0304',  # ◌̄ COMBINING MACRON
    # Tone 1, 7, 8 are unmarked (just remove the number)
}

def generate_all_rules(output_file=None):
    """Generate all comment_format rules."""
    import sys
    import io

    # Set output to file or stdout with UTF-8 encoding
    if output_file:
        f = open(output_file, 'w', encoding='utf-8')
    else:
        f = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', newline='\n')

    try:
        f.write("# Generated comment_format rules for Báⁿ-uā-ci̍\n")
        f.write("# Copy these rules into the comment_format section of your schema file\n")
        f.write("\n")
        f.write("comment_format:\n")
        f.write("  # Step 1: Add hyphens between syllables for readability\n")
        f.write("  - xform/ /-/g\n")
        f.write("\n")
        f.write("  # Step 2: Convert tone numbers (2-5) to combining diacritics\n")
        f.write("  # Apply to the main vowel in each syllable\n")
        f.write("  # Vowel priority: a > o > e > i > u > y\n")
        f.write("\n")

        # Generate rules for each tone (2, 3, 4, 5)
        for tone_num, tone_mark in TONE_MARKS.items():
            f.write(f"  # Tone {tone_num}\n")

            # Rule 1: Mark 'a' in any context (highest priority)
            # Match: any 'a' followed by optional consonants and the tone number
            # But not 'a' that's part of 'aa' (we'll handle that specially)
            f.write(f"  - xform/([^a])a([^a0-9]*){tone_num}/$1a{tone_mark}$2/\n")
            f.write(f"  - xform/^a([^a0-9]*){tone_num}/a{tone_mark}$1/\n")

            # Rule 2: Mark 'o' if no 'a' is present
            f.write(f"  - xform/([^ao])o([^aoeiu0-9]*){tone_num}/$1o{tone_mark}$2/\n")
            f.write(f"  - xform/^o([^aoeiu0-9]*){tone_num}/o{tone_mark}$1/\n")

            # Rule 3: Mark 'e' if no 'a' or 'o'
            f.write(f"  - xform/([^aoe])e([^aoeiu0-9]*){tone_num}/$1e{tone_mark}$2/\n")
            f.write(f"  - xform/^e([^aoeiu0-9]*){tone_num}/e{tone_mark}$1/\n")

            # Rule 4: Mark 'i' if no a/o/e
            f.write(f"  - xform/([^aoei])i([^aoeiu0-9]*){tone_num}/$1i{tone_mark}$2/\n")
            f.write(f"  - xform/^i([^aoeiu0-9]*){tone_num}/i{tone_mark}$1/\n")

            # Rule 5: Mark 'u' if no a/o/e/i
            f.write(f"  - xform/([^aoeiu])u([^aoeiu0-9]*){tone_num}/$1u{tone_mark}$2/\n")
            f.write(f"  - xform/^u([^aoeiu0-9]*){tone_num}/u{tone_mark}$1/\n")

            # Rule 6: Mark 'y' (ṳ) as last resort
            f.write(f"  - xform/([^aoeiuy])y([^aoeiu0-9]*){tone_num}/$1y{tone_mark}$2/\n")
            f.write(f"  - xform/^y([^aoeiu0-9]*){tone_num}/y{tone_mark}$1/\n")

            f.write("\n")

        f.write("  # Step 3: Convert special romanizations to Unicode combining characters\n")
        f.write("  # Must be done AFTER tone marks are applied\n")
        f.write("\n")

        # Convert aa → a̤ (handle with or without tone marks)
        f.write("  # aa → a̤ (with any tone mark preserved)\n")
        f.write("  - xform/a([́̂̍̄]?)a/a\u0324$1/\n")

        # Convert ee → e̤
        f.write("  # ee → e̤\n")
        f.write("  - xform/e([́̂̍̄]?)e/e\u0324$1/\n")

        # Convert oo → o̤
        f.write("  # oo → o̤\n")
        f.write("  - xform/o([́̂̍̄]?)o/o\u0324$1/\n")

        # Convert y → ṳ
        f.write("  # y → ṳ (standalone or after consonant)\n")
        f.write("  - xform/y([́̂̍̄]?)/\u1E73$1/\n")

        # Convert nn → ⁿ
        f.write("  # nn → ⁿ\n")
        f.write("  - xform/nn/\u207F/\n")

        f.write("\n")
        f.write("  # Step 4: Remove remaining tone numbers (1, 7, 8 are unmarked)\n")
        f.write("  - xform/[1-8]//g\n")

    finally:
        if output_file:
            f.close()

if __name__ == '__main__':
    import sys
    output_file = sys.argv[1] if len(sys.argv) > 1 else None
    generate_all_rules(output_file)
