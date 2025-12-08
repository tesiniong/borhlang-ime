# 莆仙語羅馬字轉換模組規劃

## 問題背景

目前專案中存在三種羅馬字系統，轉換邏輯分散且不完整：

1. **平話字（Báⁿ-uā-ci̍, BUC）** - 19世紀傳教士系統，使用變音符號
2. **輸入式平話字** - 純ASCII，方便輸入
3. **莆仙話拼音（Pouseng Ping'ing, PSP）** - 現代標準拼音

當前問題：
- `psp_to_buc.py` 只處理 PSP → BUC
- `extract_vocab_from_bible.py` 中的 `BucToPspConverter` 轉換不完整
- 缺少 BUC → 輸入式平話字 的標準轉換
- 詞庫來源混雜不同系統，導致錯誤（如 `syong5 Da̤4` 混合數字和變音符號）

## 轉換模組設計目標

### 核心系統：輸入式平話字

**理由**：
1. 純 ASCII 字符，無編碼問題
2. 無複雜的、不規則的符號位置
3. 音系較古老，可兼容其他方言
4. 易於輸入和處理

### 轉換方向

```
         ┌─────────────────────┐
         │   輸入式平話字        │ (Core)
         │   (ASCII only)      │
         └──────┬──────┬───────┘
                │      │
       ┌────────┘      └────────┐
       ▼                         ▼
 ┌──────────┐            ┌─────────────┐
 │ 平話字BUC │            │ 莆仙話拼音PSP │
 │(變音符號)│            │  (莆田方言)   │
 └──────────┘            └─────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │ PSP (江口方言)    │
                    │ PSP (南日方言)    │
                    │ PSP (仙遊方言)... │
                    └──────────────────┘
```

## 已知的轉換規則

### 1. 聲母對照

| 輸入式 | 平話字 | 莆拼PSP | 說明 |
|--------|--------|---------|------|
| b | b | b | |
| p | p | p | |
| m | m | m | |
| d | d | d | |
| t | t | t | |
| n | n | n | |
| l | l | l | |
| g | g | g | |
| k | k | k | |
| h | h | h | |
| ng | ng | ng | |
| c | c | z | 清擦音 |
| ch | ch | c | 清塞擦音 |
| s | s | s | |
| (零) | (零) | (零) | |

### 2. 韻母對照（已知部分）

#### 簡單韻母

| 輸入式 | 平話字 | 莆拼PSP | 說明 |
|--------|--------|---------|------|
| a | a | a | |
| aa | a̤ | e | 下開喉塞元音 |
| ee | e̤ | oe | ? |
| oo | o̤ | or | ? |
| y | ṳ | y | 閉喉元音 |
| i | i | i | |
| u | u | u | |
| e | e | ae | ? |
| o | o | o | |

#### 複韻母（部分已知）

| 輸入式 | 平話字 | 莆拼PSP | 來源 |
|--------|--------|---------|------|
| ai | ai | ai | psp_to_buc.py |
| au | au | ao | psp_to_buc.py |
| ia | ia | ia | psp_to_buc.py |
| iu | iu | iu | psp_to_buc.py |
| aauh | a̤uh | ieoh | psp_to_buc.py |

#### 鼻化韻母

| 輸入式 | 平話字 | 莆拼PSP | 說明 |
|--------|--------|---------|------|
| ann | aⁿ | ? | |
| aann | a̤ⁿ | ? | |
| inn | iⁿ | ? | |

#### 鼻音韻尾

| 輸入式 | 平話字 | 莆拼PSP | 說明 |
|--------|--------|---------|------|
| ang | ang | ang | |
| eng | eng | eng | |
| ing | ing | ing | |
| ong | ong | ong | |
| ng | ng | ng | 單獨韻母 |
| oorng | o̤ng | orng | 需確認 |

#### 入聲韻尾（-h）

| 輸入式 | 平話字 | 莆拼PSP | 說明 |
|--------|--------|---------|------|
| ah | ah | ah | |
| aah | a̤h | eh | |
| ooh | o̤h | orh | |
| ih | ih | ih | |
| eh | eh | aeh | 需確認 |

### 3. 聲調對照

| 調類 | 平話字標記 | 輸入式 | 莆拼PSP | 說明 |
|------|-----------|--------|---------|------|
| 1 陰平 | (無) | 1 | 1 | |
| 2 陽平 | ́ (acute) | 2 | 2 | |
| 3 上聲 | ̂ (circumflex) | 3 | 3 | |
| 4 陰去 | ̍ (vertical)* | 4 | 4 | *非h結尾時 |
| 5 陽去 | ̄ (macron)* | 5 | 5 | *非h結尾時 |
| 6 陰入 | (無 或 ̄)* | 6 | 6 | *h結尾時 |
| 7 陽入 | ̍* | 7 | 7 | *h結尾時 |

**重要規則**：
- vertical line (̍): 非h結尾=tone4，h結尾=tone7
- macron (̄): 非h結尾=tone5，h結尾=tone6

## 需要補充的知識

### 用戶提到的具體案例

**問題案例**：
- 原書平話字：`Siō̤ng-Da̤̍`
- 錯誤輸出：`syong5 Da̤4` （混合格式）
- 正確莆拼：`syorng5 de4`
- 正確輸入式：`sioong5 daa4`

**需要確認**：
1. `io̤ng` 複韻母的處理：
   - 輸入式應該是 `ioong` 還是其他？
   - 莆拼是 `iorng` 還是 `yorng`？

2. 大寫字母規則：
   - `Da̤̍` 中的大寫 D 是什麼意思？
   - 是專有名詞標記嗎？

3. 完整的複韻母列表：
   - 特別是帶 i-, u- 介音的複韻母
   - 例如：ia, iu, ua, ue, io, iong 等

4. 聲母與韻母的搭配限制（如果有）

## 現有代碼資源

### psp_to_buc.py

包含：
- `buc_initials` - 聲母映射字典
- `buc_finals` - 韻母映射字典（PSP→BUC候選列表）
- `buc_tones` - 聲調符號映射

**問題**：
- 只有 PSP → BUC 方向
- 韻母映射可能不完整
- 缺少反向轉換邏輯

### extract_vocab_from_wikt.py

包含 `BucToPspConverter` 類：
- `TONE_MARKS_TO_NUM` - 聲調符號→數字
- `FINAL_MAP` - 韻母反向映射
- `INITIAL_MAP` - 聲母反向映射

**問題**：
- 轉換不完整（產生混合格式）
- 缺少複韻母處理

### convert_dict_v3.py

包含 `BucRomanizer` 類：
- `psp_to_buc_candidates()` - PSP→BUC候選生成
- `buc_to_romanization()` - BUC→輸入式
- `buc_final_to_romanization()` - 特殊字符替換

## 實現計畫

### 階段一：統一轉換模組

創建 `romanization_converter.py`，包含：

```python
class RomanizationConverter:
    """莆仙語羅馬字系統轉換器"""

    # 核心數據結構
    INITIALS = {...}  # 聲母三系統對照
    FINALS = {...}    # 韻母三系統對照
    TONES = {...}     # 聲調三系統對照

    # 主要方法
    @staticmethod
    def input_to_buc(syllable: str) -> str:
        """輸入式 → 平話字"""
        pass

    @staticmethod
    def input_to_psp(syllable: str) -> str:
        """輸入式 → 莆拼"""
        pass

    @staticmethod
    def buc_to_input(syllable: str) -> str:
        """平話字 → 輸入式"""
        pass

    @staticmethod
    def psp_to_input(syllable: str) -> str:
        """莆拼 → 輸入式"""
        pass
```

### 階段二：驗證和測試

1. 創建測試案例（從維基詞典和聖經提取）
2. 驗證所有轉換路徑
3. 修正 `extract_vocab_from_bible.py` 使用新轉換器

### 階段三：重構現有代碼

1. 替換 `psp_to_buc.py`
2. 替換 `convert_dict_v3.py` 中的轉換邏輯
3. 統一所有詞庫格式

## 待辦事項

- [ ] 補充完整的韻母對照表
- [ ] 確認 `io̤ng` 等複韻母的三系統對應
- [ ] 確認大小寫規則
- [ ] 創建 `romanization_converter.py`
- [ ] 編寫單元測試
- [ ] 重構現有代碼
- [ ] 更新文檔

## 相關文件

- `CLAUDE.md` - 專案整體文檔（聲調規則已記錄）
- `data/psp_to_buc.py` - 現有PSP→BUC轉換
- `tools/extract_vocab_from_wikt.py` - BucToPspConverter
- `tools/convert_dict_v3.py` - BucRomanizer

---

**文檔創建日期**：2025-01-XX
**最後更新**：待補充完整韻母表後更新
