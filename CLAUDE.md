# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Borhlang IME (木蘭輸入法)** is a Rime-based input method editor for the Puxian language (莆仙語/Hinghwa), supporting two romanization systems:

1. **Báⁿ-uā-ci̍ (興化平話字)**: 19th-century missionary romanization
   - Pure romanization mode: Outputs Báⁿ-uā-ci̍ with Hanzi annotations, uses Lua filters
   - Hanzi mode: Outputs Hanzi with Báⁿ-uā-ci̍ annotations

2. **Pouseng Ping'ing (莆仙話拼音)**: Modern Puxian pinyin
   - Outputs Hanzi with pinyin tone numbers

Auto-converts between systems using linguistic rules and Wiktionary data.

## Core Commands

### Build All Dictionaries

```bash
# Windows
build_dicts.bat

# macOS/Linux
python tools/build_all_dicts.py
```

Rebuilds all dictionaries from Wiktionary/Bible/Reference sources. Runs extraction → merge → conversion pipeline.

### Individual Scripts

```bash
# Extract from sources (Input-form for Bible preserves nasal finals nn)
python tools/extract_vocab_from_wikt.py    # → data/vocab_from_wikt.yaml (PSP)
python tools/extract_vocab_from_bible.py   # → data/vocab_from_bible.yaml (Input)

# Convert dictionaries
python tools/convert_dict_v3.py            # PSP → BUC (Hanzi mode)
python tools/generate_pure_bannuaci_dict.py # → BUC (pure romanization)

# Deploy to Rime
deploy_to_rime.bat                         # Windows: auto-copy to %APPDATA%\Rime
./deploy_to_rime.sh                        # Linux/macOS: auto-detect Rime path
```

### Test Conversion

```bash
python data/psp_to_buc.py           # Interactive: type syllables (e.g., "pou2 deng2")
python tools/test_lung.py           # Test specific characters
python tools/test_nao.py            # Test nasal finals
```

調符位置統一記錄在：`data/tone_positions.py`

## Key Data Files

### Source Data

| File | Purpose | Format |
|------|---------|--------|
| `data/cpx-pron-data.lua` | Wiktionary pronunciations | Lua: `["字"] = {"pron1"}` |
| `docs/puxian_phrases_from_wikt.txt` | Wiktionary phrases | TSV: 漢字\tBUC\tPSP |
| `data/bible_data.json` | Hinghwa Bible | JSON with BUC/Hanzi tokens |
| `hinghwa-ime/Pouleng/Pouleng.dict.yaml` | Reference dictionary | PSP, ~24k entries |

### Generated Files

| File | Purpose | Format |
|------|---------|--------|
| `data/vocab_from_wikt.yaml` | Wiktionary vocabulary | PSP |
| `data/vocab_from_bible.yaml` | Bible vocabulary (preserves nasal finals) | **Input-form** |
| `pouseng_pinging/borhlang_pouleng.dict.yaml` | Merged PSP dictionary (auto-generated) | PSP |
| `bannuaci/borhlang_bannuaci_han.dict.yaml` | BUC dictionary (Hanzi mode) | BUC |
| `bannuaci/borhlang_bannuaci.dict.yaml` | BUC dictionary (pure romanization) | Lua format |

### Processing Modules

| File | Purpose |
|------|---------|
| `data/psp_to_buc.py` | Core PSP→BUC conversion with mapping dicts |
| `data/romanization_converter.py` | Three-way converter (PSP↔Input↔BUC) |
| `bannuaci/lua/bannuaci_filter.lua` | Sentence composition + case handling |
| `bannuaci/lua/comment_formatter.lua` | Input-form → BUC for reverse lookup |

**Key converter methods:**
- `RomanizationConverter.buc_to_input()` - BUC → Input (removes diacritics)
- `RomanizationConverter.input_to_psp()` - Input → PSP (**c→z, ch→c**)
- `RomanizationConverter.input_to_buc()` - Input → BUC (adds diacritics)
- `RomanizationConverter.psp_to_input()` - PSP → Input (**z→c, c→ch**)

## Data Flow

```
Wiktionary → extract_vocab_from_wikt.py → vocab_from_wikt.yaml (PSP)
                                              ↓
Bible JSON (BUC) → buc_to_input() → vocab_from_bible.yaml (Input, preserves nn)
                                              ↓
Reference dict (PSP)                          ↓
                     ↘                        ↓
                      build_all_dicts.py (Input→PSP merge)
                                ↓
                    borhlang_pouleng.dict.yaml (PSP, auto-generated)
                                ↓
                        convert_dict_v3.py (PSP→BUC)
                                ↓
                    borhlang_bannuaci_han.dict.yaml (BUC)
                                ↓
                    generate_pure_bannuaci_dict.py
                                ↓
                    borhlang_bannuaci.dict.yaml (Lua format)
```

**Why Bible uses Input-form:**
- Modern Putian dialect lost nasal finals (ⁿ), PSP doesn't record them
- Input retains `nn` → enables nasal reversal logic in convert_dict_v3.py (cases 4-5)
- Input→PSP is many-to-one (simple), PSP→Input loses distinctions

**⚠️  IMPORTANT:** `borhlang_pouleng.dict.yaml` is auto-generated - DO NOT manually edit.

## Three Romanization Systems

| System | Chinese | Purpose | Example | Used In |
|--------|---------|---------|---------|---------|
| **PSP** | 莆仙話拼音 | Modern standard | `zing2 ai4` (情愛) | Dictionary storage |
| **Input** | 輸入式平話字 | Pure ASCII input | `cing2 ai4` | User input, intermediate |
| **BUC** | 興化平話字 | Historical with diacritics | `cíng-a̍i` (情愛) | Display output |

**Critical Initial Differences:**

| Phoneme | PSP | Input | BUC | Example |
|---------|-----|-------|-----|---------|
| [ts] unaspirated | **z** | **c** | **c** | 情: `zing2` / `cing2` / `cíng` |
| [tsʰ] aspirated | **c** | **ch** | **ch** | 清: `cing1` / `ching1` / `ching` |

**⚠️  CRITICAL:** Do NOT confuse Input `cing2` with PSP! Must convert Input→PSP first: `cing2` → `zing2` → `cíng`.

**Conversion chain:**
```
BUC → Input → (vocab_from_bible.yaml) → PSP (merge) → (dictionary) → PSP → BUC (output)
```

Bible data preserves Input-form with nasal finals; conversion to PSP happens during merge.

## Tone Mapping (PSP → BUC)

| Tone | Name | PSP | BUC Mark | Position | Input Key |
|------|------|-----|----------|----------|-----------|
| 1 | 陰平 | 1 | (none) | - | `1` or omit |
| 2 | 陽平 | 2 | ́ (acute) | vowel | `q` |
| 3 | 上聲 | 3 | ̂ (circumflex) | vowel | `v` |
| 4 | 陰去 | 4 | ̍ (vertical) | vowel | `j` |
| 5 | 陽去 | 5 | ̄ (macron) | vowel | `f` |
| 6 | 陰入 | 6 | (none or ̄) | ends h | `6` or omit |
| 7 | 陽入 | 7 | ̍ | ends h | `j` |

**Context-dependent marks:**
- **Vertical line (̍)**: Tone 4 (non-h) or Tone 7 (h-ending)
- **Macron (̄)**: Tone 5 (non-h) or Tone 6 (h-ending)

**Special vowels (combining diacritics):**
- `a̤` (U+0061 U+0324) - PSP `e`
- `e̤` (U+0065 U+0324) - PSP `oe`
- `o̤` (U+006F U+0324) - PSP `or`
- `ṳ` (U+1E73) - PSP `y`
- `ⁿ` (U+207F) - Nasal marker

Input shortcuts: `aa`→`a̤`, `ee`→`e̤`, `oo`→`o̤`, `y`→`ṳ`, `nn`→`ⁿ`

## Conversion Algorithm

### Phase 1: Direct Conversion
Parse PSP syllable (e.g., `pou2`) → initial (p) + final (ou) + tone (2) → map via `psp_to_buc.py` → validate against `cpx-pron-data.lua`.

### Phase 2: Assimilation Reversal (聲母類化反推)

If direct fails, reverse tone assimilation based on previous syllable final:
- **Previous ends -ng**: Current m/n/ng may ← b/p/m, d/t/n/l/z/c/s, g/k/h/ng
- **Previous open syllable**: Current zero-initial may ← b/p, g/k/h
- **Previous ends -h**: No assimilation

Example: 田 `leng2` after open → tries `teng2`, `ting2`... → matches `téng` in Wiktionary.

### Phase 3: Fallback
Use direct result, log warning for manual review.

## Lua Filters (Pure Romanization Mode)

**Dictionary format:** `romanization@input@hanzi|` (pipe delimiter)

**bannuaci_filter.lua:**
- Parses format with regex: `([^@]+)@[^@]+@([^|]+)|`
- Combines syllables: `po-seng-u (鋪 生 有)`
- **Case handling:** Detects input case pattern (lowercase/title), applies to output
- **UTF-8 support:** Handles precomposed + combining diacritics correctly

**comment_formatter.lua:**
- Converts Input-form → BUC for reverse lookup
- Algorithm: parse syllable → separate initial/final → apply replacements (`aa`→`a̤`, `nn`→`ⁿ`) → insert tone mark at correct position → NFC normalize

**reverse_lookup_helper.lua:**
- Loads `borhlang_bannuaci_han.dict.yaml` into memory at startup
- Provides Hanzi → romanization lookup for pure romanization mode

## Important Development Notes

### Unicode Normalization
Always use NFC normalization for output:
```python
from unicodedata import normalize as norm
output = norm('NFC', buc_syllable)
```

### File Encoding
All files must be UTF-8:
```python
open(file, 'r', encoding='utf-8')
```

### Rime Schema Testing
After modifying schemas/dictionaries:
1. Copy files to Rime user directory (`%APPDATA%\Rime` on Windows)
2. For pure romanization mode: ensure Lua files copied to `lua/` subdirectory
3. Trigger Rime deployment (rebuilds dictionaries)

### Conversion Statistics
`DictConverter` tracks: total, success, bracketed, multiple_matches, no_match, from_dict_direct, from_dict_case_123, from_dict_case_45, from_conversion. Review `bannuaci/conversion_log.txt`.

## Language & Communication

**Always use Traditional Chinese (繁體中文) with Taiwan terminology:**
- 儲存 (not 存儲) for "store"
- 演算法 (not 算法) for "algorithm"
- 軟體 (not 软件) for "software"
- 程式 (not 程序) for "program"

## Common Pitfalls

### Dictionary Build
`pouseng_pinging/borhlang_pouleng.dict.yaml` is auto-generated. Check header:
```yaml
# ⚠️  本詞庫為自動生成，請勿手動編輯！
```

### Romanization Confusion
Three distinct systems - do not mix. Bible data preserves Input-form; conversion to PSP happens during merge.

### Missing Finals Error
If `data/bible_conversion_errors.log` shows "未知的輸入式韻母", add missing final to `romanization_converter.py` FINALS_INPUT_TO_PSP dict.

### Unicode on Windows
Console cannot display combining diacritics. Use `repr()` or write to UTF-8 file.
