# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Borhlang IME (木蘭輸入法)** is a Rime-based input method editor for the Puxian language (莆仙語/Hinghwa), supporting two romanization systems:

1. **Báⁿ-uā-ci̍ (興化平話字)**: 19th-century missionary romanization system
   - **Pure romanization mode** (`borhlang_bannuaci.schema.yaml`): Outputs Báⁿ-uā-ci̍ text with Hanzi annotations, uses **Lua filters** for intelligent sentence composition
   - **Hanzi mode** (`borhlang_bannuaci_han.schema.yaml`): Outputs Hanzi with Báⁿ-uā-ci̍ annotations

2. **Pouseng Ping'ing (莆仙話拼音)**: Modern Puxian pinyin system
   - Outputs Hanzi with pinyin tone numbers

The project auto-converts between these systems using linguistic rules and Wiktionary data.

## Core Commands

### One-Click Dictionary Update (推薦使用)

**Complete workflow - rebuild all dictionaries from all sources:**

**Windows:**
```bash
build_dicts.bat
```

**macOS/Linux:**
```bash
python tools/build_all_dicts.py
```

This master script orchestrates the entire dictionary building pipeline:
1. Extracts vocabulary from Wiktionary data (`docs/puxian_phrases_from_wikt.txt`)
2. Extracts vocabulary from Hinghwa Bible (`docs/hinghua_bible.txt`)
3. Merges all sources into `pouseng_pinging/borhlang_pouleng.dict.yaml`
4. Converts to Báⁿ-uā-ci̍ dictionary (Hanzi version)
5. Generates pure Báⁿ-uā-ci̍ dictionary (Lua format)

**Use this script whenever you update any source data files.**

### Individual Processing Scripts

**Extract vocabulary from Wiktionary:**
```bash
python tools/extract_vocab_from_wikt.py
```
- Reads: `docs/puxian_phrases_from_wikt.txt` (4 TSV columns: 漢字, Báⁿ-uā-ci̍, PSP original, PSP actual)
- Outputs: `data/vocab_from_wikt.yaml` (~4000 entries)
- Handles duplicates, converts Báⁿ-uā-ci̍ to PSP if needed

**Extract vocabulary from Bible:**
```bash
python tools/extract_vocab_from_bible.py
```
- Reads: `docs/hinghua_bible.txt` (aligned Báⁿ-uā-ci̍ and Hanzi lines)
- Outputs: `data/vocab_from_bible.yaml` (extracted n-grams and words)
- Handles 合音字 (e.g., 「家己」→ ga̍i), proper nouns → lowercase
- Extracts 2-4 character phrases with frequency weighting

**Manual conversion** (莆仙話拼音 → 興化平話字):
```bash
python tools/convert_dict_v3.py
```

This converts Pouseng Ping'ing to Báⁿ-uā-ci̍ (Hanzi version):
- Reads `pouseng_pinging/borhlang_pouleng.dict.yaml`
- Reads `data/cpx-pron-data.lua` (Wiktionary character pronunciation data)
- Outputs to `bannuaci/borhlang_bannuaci_han.dict.yaml`
- Generates `bannuaci/conversion_log.txt` (warnings and conversion notes)

**Generate pure Báⁿ-uā-ci̍ dictionary:**
```bash
python tools/generate_pure_bannuaci_dict.py
```

Converts Hanzi version to Lua-compatible format:
- Reads `bannuaci/borhlang_bannuaci_han.dict.yaml`
- Outputs `bannuaci/borhlang_bannuaci.dict.yaml` (format: `romanization@input@hanzi|`)
- Merges homophones with `/` separator

**Note**: Use `build_all_dicts.py` instead of running these individually.

### Windows Quick Deployment

**Automated deployment to Rime** (Windows only):
```bash
deploy_to_rime.bat
```

This batch script automatically:
- Copies all Báⁿ-uā-ci̍ schema files (`.schema.yaml`) to `%APPDATA%\Rime`
- Copies all dictionary files (`.dict.yaml`) to `%APPDATA%\Rime`
- Copies Lua filter scripts to `%APPDATA%\Rime\lua\`
- Copies `rime.lua` entry file to `%APPDATA%\Rime`
- Provides step-by-step instructions for Rime redeployment

### Testing Individual Conversions

Test the phonetic conversion algorithm directly:
```bash
python data/psp_to_buc.py
# Interactive mode - type syllables with tones (e.g., "pou2 leng2")
```

**Additional test scripts** (in `tools/` directory):
```bash
python tools/test_lung.py        # Test specific character conversions
python tools/test_nao.py         # Test nasal final conversions
python tools/test_final_type.py  # Test final type classification
```

These are debugging tools for developers working on the conversion algorithm.

### Format Generation Scripts

Generate display format transformation rules:
```bash
python tools/generate_comment_format.py      # For Báⁿ-uā-ci̍ display
python tools/generate_comment_format_v2.py   # Alternative version
```

These generate the `comment_format` rules used in Rime schema files to transform ASCII romanization into proper tone marks.

## Architecture & Data Flow

### Complete Data Flow

```
SOURCE DATA                          PROCESSING                       OUTPUT
═══════════════════════════════════════════════════════════════════════════════

1. Wiktionary Phrases                extract_vocab_from_wikt.py      vocab_from_wikt.yaml
   (docs/puxian_phrases_from_wikt.txt)  ──────────────────────>        (~4000 entries)
   - 漢字\tBUC\tPSP_orig\tPSP_actual                                             │
                                                                                 │
2. Hinghwa Bible                     extract_vocab_from_bible.py     vocab_from_bible.yaml  │
   (docs/hinghua_bible.txt)             ──────────────────────>        (n-grams, freq-based) │
   - Aligned BUC/Hanzi                                                           │
   - 合音字 handling                                                              │
                                                                                 │
3. Base Dictionary                                                               │
   (pouseng_pinging/                                                             │
    borhlang_pouleng.dict.yaml)                                                  │
   - Manually curated                                                            │
                                                     ┌───────────────────────────┘
                                                     │
                                                     ▼
                                            MERGED DICTIONARY
                                    pouseng_pinging/borhlang_pouleng.dict.yaml
                                             (莆仙話拼音)
                                                     │
                                                     │ convert_dict_v3.py
                                                     │ (Uses: psp_to_buc.py
                                                     │        cpx-pron-data.lua)
                                                     ▼
                                    bannuaci/borhlang_bannuaci_han.dict.yaml
                                          (興化平話字 - 漢字版)
                                                     │
                                                     │ generate_pure_bannuaci_dict.py
                                                     ▼
                                    bannuaci/borhlang_bannuaci.dict.yaml
                                       (興化平話字 - Lua格式)
                                    format: romanization@input@hanzi|
```

**Why merge multiple sources?**
- **Base dictionary**: Manually curated, highest quality
- **Wiktionary phrases**: Comprehensive multi-character words
- **Bible text**: Natural language patterns, idiomatic expressions
- **Conversion validation**: All entries validated against `cpx-pron-data.lua`

**Why Pouseng Ping'ing → Báⁿ-uā-ci̍ direction?**
- Pouseng Ping'ing is the modern standard with complete vocabulary
- Báⁿ-uā-ci̍ is historically accurate but lacks comprehensive modern lexicon
- Easier to validate PSP→BUC than BUC→PSP

### Key Data Files

**Source Data:**
| File | Purpose | Format |
|------|---------|--------|
| `data/cpx-pron-data.lua` | Wiktionary pronunciation data | Lua table: `["字"] = {"pron1", "pron2"}` |
| `docs/puxian_phrases_from_wikt.txt` | Wiktionary phrases | TSV: 漢字\tBUC\tPSP_orig\tPSP_actual |
| `docs/hinghua_bible.txt` | Hinghwa Bible text | Aligned BUC/Hanzi lines, 合音字 in 「」 |
| `hinghwa-ime/Pouleng/Pouleng.dict.yaml` | Reference dictionary | Rime dict format (~24k entries) |

**Processing Modules:**
| File | Purpose | Format |
|------|---------|--------|
| `data/psp_to_buc.py` | Core conversion algorithm | Python module with mapping dicts |
| `data/puxian_initials.json` | Initial consonants by dialect | JSON phoneme inventory |
| `data/puxian_rhymes.json` | Rhyme patterns by dialect | JSON phoneme inventory |

**Generated Intermediate Files:**
| File | Purpose | Generated By |
|------|---------|--------------|
| `data/vocab_from_wikt.yaml` | Extracted Wiktionary vocabulary | `extract_vocab_from_wikt.py` |
| `data/vocab_from_bible.yaml` | Extracted Bible vocabulary | `extract_vocab_from_bible.py` |

### Dictionary Format

All Rime dictionaries follow this format:
```yaml
---
name: dictionary_name
version: "0.1.0"
...

漢字<TAB>romanization<TAB>weight
莆田	pou2 leng2	500
食飯	sia2 mue5
```

**Important**:
- Use TAB characters (not spaces) between columns
- Romanization syllables are space-separated
- Weight (frequency) is optional
- Header ends with `...` followed by blank line

### Schema Configuration

Two directories contain complete Rime schemes:

**bannuaci/** (興化平話字):
- `borhlang_bannuaci.schema.yaml` - Pure romanization output (uses Lua filter)
- `borhlang_bannuaci_han.schema.yaml` - Hanzi with romanization annotations (no Lua filter)
- `borhlang_bannuaci.dict.yaml` - Dictionary (auto-generated with special format)
- `lua/bannuaci_filter.lua` - Lua filter for intelligent sentence composition
- `rime.lua` - Lua entry file that registers the filter

**pouseng_pinging/** (莆仙話拼音):
- `borhlang_pouleng.schema.yaml` - Schema configuration
- `borhlang_pouleng.dict.yaml` - Dictionary (manually maintained)

### Lua Intelligent Features (Pure Romanization Mode Only)

The **pure romanization mode** (`borhlang_bannuaci.schema.yaml`) uses a Lua filter to enable intelligent sentence composition:

**Dictionary Entry Format:**
```yaml
# Special format: romanization@input_code@hanzi|
# Note the pipe "|" at the end of each syllable
po@po1@鋪|seng@seng1@生|u@u2@有|
```

**Lua Filter Processing (`lua/bannuaci_filter.lua`):**
1. Parses the special format using regex pattern: `([^@]+)@[^@]+@([^|]+)|`
   - First group: romanization (e.g., `po`)
   - Second group: hanzi (e.g., `鋪`)
   - The `|` pipe character serves as the delimiter
2. Extracts romanization and Hanzi parts for each syllable
3. Combines multiple syllables with hyphens: `po-seng-u`
4. Groups Hanzi as annotations in parentheses: `(鋪 生 有)`
5. Final output: `po-seng-u (鋪 生 有)`

**Key Features:**
- **Automatic hyphenation**: Multi-syllable words are connected with `-` (hyphen)
- **Hanzi annotations**: Original characters shown in parentheses for reference
- **Sentence composition**: Enables natural romanization text output while preserving character information

**File Structure:**
- `bannuaci/rime.lua` - Entry point that loads the filter
- `bannuaci/lua/bannuaci_filter.lua` - Main filter implementation
- Both files must be deployed to Rime user directory for the filter to work

**Note**: The Hanzi output mode (`borhlang_bannuaci_han.schema.yaml`) does NOT use this Lua filter.

## Conversion Algorithm Details

### Phase 1: Direct Conversion

For each Pouseng Ping'ing syllable (e.g., `pou2`):
1. Parse into: initial (p) + final (ou) + tone (2)
2. Map using `psp_to_buc.py`:
   - Initial: `p` → `p`
   - Final: `ou` → `o` (one of several candidates)
   - Tone: `2` → `́` (acute accent)
3. Combine: `pó`
4. Validate against Wiktionary data in `cpx-pron-data.lua`

### Phase 2: Assimilation Reversal (聲母類化反推)

If direct conversion fails, reverse tone assimilation patterns:

**Rules by previous syllable final**:
- **Previous ends in -ng**: Current m/n/ng may come from b/p/m, d/t/n/l/z/c/s, g/k/h/ng respectively
- **Previous is open syllable**: Current zero-initial may come from b/p, g/k/h
- **Previous ends in -h**: No assimilation

Example:
```
Input: "田" with PSP "leng2" after open syllable
→ Direct: léng (not in Wiktionary for 田)
→ Reverse: Try teng2, ting2, deng2...
→ Match: téng (found in Wiktionary)
→ Output: téng
```

### Phase 3: Fallback

If both phases fail, use direct conversion result and log as warning for manual review.

## Working with Dictionaries

### Recommended Workflow (推薦工作流程)

**When you update any source data:**

1. **Update source files:**
   - Add/edit entries in `pouseng_pipping/borhlang_pouleng.dict.yaml` (manual curation)
   - OR update `docs/puxian_phrases_from_wikt.txt` (Wiktionary data)
   - OR update `docs/hinghua_bible.txt` (Bible text)

2. **Run the master build script:**
   ```bash
   python tools/build_all_dicts.py
   ```

3. **Review outputs:**
   - Check `bannuaci/conversion_log.txt` for warnings
   - Verify generated dictionaries in `bannuaci/` and `pouseng_pinging/`

4. **Deploy to Rime:**
   - Windows: Run `deploy_to_rime.bat`
   - macOS/Linux: Manually copy files to Rime user directory

### Adding Individual Entries (Manual Method)

**For manual dictionary updates without rebuilding from all sources:**

1. Edit `pouseng_pinging/borhlang_pouleng.dict.yaml`
2. Add entries in format: `漢字<TAB>拼音<TAB>權重`
3. Run individual conversion scripts:
   ```bash
   python tools/convert_dict_v3.py
   python tools/generate_pure_bannuaci_dict.py
   ```
4. Review `bannuaci/conversion_log.txt` for warnings

### Updating Source Data Files

**Wiktionary character pronunciations:**
1. Edit `data/cpx-pron-data.lua`
2. Add/modify entries in format: `["字"] = {"pron1", "pron2"},`
3. Run `python tools/build_all_dicts.py`

**Wiktionary phrases:**
1. Edit `docs/puxian_phrases_from_wikt.txt`
2. Format: `漢字<TAB>Báⁿ-uā-ci̍<TAB>PSP_original<TAB>PSP_actual`
3. Run `python tools/build_all_dicts.py`

**Bible text:**
1. Edit `docs/hinghua_bible.txt`
2. Maintain format: BUC line, Hanzi line, blank line
3. Mark 合音字 with 「」: e.g., 「家己」for ga̍i
4. Run `python tools/build_all_dicts.py`

### Merging New Vocabulary

When you have new words (possibly with duplicates):

**Option A - Simple append**:
```bash
# Appends all entries, Rime handles duplicates by weight
cat new_words.txt >> pouseng_pinging/borhlang_pouleng.dict.yaml
python tools/convert_dict_v3.py
```

**Option B - Smart merge** (requires custom script):
- Parse both dictionaries
- Deduplicate by hanzi+pinyin
- Keep highest weight when duplicate
- Sort by weight
- Regenerate YAML

## Phonetic System References

### Tone Mapping (PSP → Báⁿ-uā-ci̍)

| Tone | Name | PSP | Báⁿ Mark | Position | Input Key |
|------|------|-----|----------|----------|-----------|
| 1 | 陰平 | 1 | (none) | - | `1` or omit |
| 2 | 陽平 | 2 | ́ (acute) | On vowel | `q` |
| 3 | 上聲 | 3 | ̂ (circumflex) | On vowel | `v` |
| 4 | 陰去 | 4 | ̍ (vertical line) | On vowel | `j` |
| 5 | 陽去 | 5 | ̄ (macron) | On vowel | `f` |
| 6 | 陰入 | 6 | (none or ̄) | Ends in h | `6` or omit |
| 7 | 陽入 | 7 | ̍ | Ends in h | `j` |

**CRITICAL: Tone Mark Context Dependency**

The same diacritic mark has different meanings depending on the syllable ending:

- **Vertical line above (̍ U+030D)**:
  - On non-h-ending syllable → Tone 4 (陰去) e.g., `sê̍ng` = `seng4`
  - On h-ending syllable → Tone 7 (陽入) e.g., `do̤̍h` = `dooh7`, `le̍h` = `leh7`

- **Macron (̄ U+0304)**:
  - On non-h-ending syllable → Tone 5 (陽去) e.g., `kā` = `ka5`
  - On h-ending syllable → Tone 6 (陰入) e.g., `sāh` = `sah6`

This rule is implemented in `convert_dict_v3.py` (lines 210-218) and must be preserved when processing Báⁿ-uā-ci̍ text.

**Tone Input Keys** (since number keys are used for candidate selection):
- `q` = Tone 2 (陽平 ´)
- `v` = Tone 3 (上聲 ˆ)
- `j` = Tone 4/7 (陰去/陽入 ̍)
- `f` = Tone 5 (陽去 ¯)

**Examples**:
- Input `baq` → Shows only tone 2 candidates: `bá` (爸)
- Input `bav` → Shows only tone 3 candidates: `bâ` (罷)
- Input `ba` → Shows all tones: `ba`, `bá`, `bâ`, `ba̍`, `bā`, etc.

This is implemented in the schema's `speller/algebra` section using `derive` rules.

### Initial Consonant Mapping

```python
# From psp_to_buc.py
buc_initials = {
    "b": "b",    "p": "p",    "m": "m",
    "d": "d",    "t": "t",    "n": "n",    "l": "l",
    "g": "g",    "k": "k",    "ng": "ng",  "h": "h",
    "z": "c",    "c": "ch",   "s": "s",
    "": ""  # zero initial
}
```

**Key difference**: PSP uses `z/c`, Báⁿ uses `c/ch`

### Special Vowels in Báⁿ-uā-ci̍

These require combining diacritics:
- `a̤` (U+0061 U+0324) - PSP `e`
- `e̤` (U+0065 U+0324) - PSP `oe`
- `o̤` (U+006F U+0324) - PSP `or`
- `ṳ` (U+1E73) - PSP `y`
- `ⁿ` (U+207F) - Nasalization marker

Input shortcuts in schema: `aa`/`ar`→`a̤`, `ee`/`er`→`e̤`, `uu`/`ur`/`y`→`ṳ`, `nn`→`ⁿ`

## Important Development Notes

### Unicode Normalization

Always use NFC normalization for output:
```python
from unicodedata import normalize as norm
output = norm('NFC', buc_syllable)
```

This ensures combining diacritics are properly composed.

### Conversion Statistics

The `DictConverter` class tracks:
- `total`: Total entries processed
- `success`: Successfully converted entries
- `bracketed`: Compound characters in [brackets]
- `multiple_matches`: Multiple valid pronunciations found
- `no_match`: Required Wiktionary lookup
- `from_dict_direct`: Matched directly
- `from_dict_case_123`: Matched via assimilation reversal (cases 1-3)
- `from_dict_case_45`: Matched via assimilation reversal (cases 4-5)
- `from_conversion`: Used automatic conversion fallback

Review `bannuaci/conversion_log.txt` for detailed conversion notes.

### File Encoding

All files must be UTF-8:
- Python files: `# -*- coding: utf-8 -*-`
- YAML files: `# encoding: utf-8`
- Lua files: UTF-8 encoding required for proper Unicode handling
- Always specify encoding when opening: `open(file, 'r', encoding='utf-8')`

### Rime Schema Testing

After modifying schemas or dictionaries:

1. Copy files to Rime user directory:
   - Windows: `%APPDATA%\Rime` (or use `deploy_to_rime.bat`)
   - macOS: `~/Library/Rime`
   - Linux: `~/.config/ibus/rime` or `~/.config/fcitx/rime`

2. **For pure romanization mode**: Ensure Lua files are copied:
   - Copy `bannuaci/rime.lua` to Rime user directory
   - Copy `bannuaci/lua/bannuaci_filter.lua` to `[Rime user directory]/lua/`
   - Without these files, the Lua filter will fail and pure romanization mode won't work correctly

3. Trigger Rime deployment (rebuilds dictionaries)

4. Test input scenarios:
   - Tone-less input (most common)
   - Abbreviations (first letters)
   - Fuzzy sounds
   - Reverse lookup (backtick prefix)
   - **Pure romanization mode**: Multi-syllable words should display with hyphens and Hanzi annotations

## Project Structure Rationale

### Input Method System Architecture

The project provides **three distinct input methods**:

1. **Pure Báⁿ-uā-ci̍ Romanization** (`borhlang_bannuaci.schema.yaml`)
   - Outputs: Romanization text with Hanzi annotations
   - Example: `po-seng-u (鋪 生 有)`
   - Uses Lua filter for intelligent sentence composition
   - Target users: Those writing in romanization

2. **Hanzi with Báⁿ-uā-ci̍ Annotations** (`borhlang_bannuaci_han.schema.yaml`)
   - Outputs: Hanzi with romanization as reference
   - Example: `鋪生有 pó-seng-ú`
   - No Lua filter needed
   - Target users: Those writing in Hanzi who want romanization reference

3. **Pouseng Ping'ing (Modern Pinyin)** (`borhlang_pouleng.schema.yaml`)
   - Outputs: Hanzi with pinyin tone numbers
   - Example: `鋪生有 pou²seng¹u²`
   - Target users: Modern Puxian language learners and speakers

### Why Two Separate Dictionaries?

**Pouseng Ping'ing** (`pouseng_pinging/`):
- Manually curated modern lexicon
- Community-maintained
- Source of truth for contemporary usage
- Includes modern terms, place names, etc.

**Báⁿ-uā-ci̍** (`bannuaci/`):
- Auto-generated from Pouseng Ping'ing
- Historically authentic romanization
- Validated against 19th-century texts via Wiktionary
- Preserves missionary romanization conventions
- Special format to support Lua filter processing

### Why Keep hinghwa-ime/?

Reference submodule from original project:
- Source of Pouleng.dict.yaml (24,000+ entries)
- Historical development context
- Community contribution guidelines
- Original schema configurations

**Do not modify** - copy entries to `pouseng_pinging/` instead.

## Language & Communication

**Always use Traditional Chinese (繁體中文) with Taiwan terminology**:
- 儲存 (not 存儲) for "store"
- 演算法 (not 算法) for "algorithm"
- 軟體 (not 软件) for "software"
- 程式 (not 程序) for "program"

This matches the project's target audience and linguistic heritage.

## Future Extensions

Current status: Only **Pouleng (莆田)** dialect is complete.

Planned dialect points (require new schema files):
- Gangngao (江口)
- Nangnih (南日)
- Dangngai (東海)
- Sengniu (仙遊)
- Iuyang (游洋)
- Horngneng (楓亭)

Each requires:
1. Dictionary with dialect-specific pronunciations
2. Schema file with dialect name
3. Phoneme inventory updates in `data/puxian_rhymes.json`
4. Possibly dialect-specific conversion rules

The conversion pipeline (`convert_dict_v3.py`) is designed to support multiple dialects via parameter passing.
