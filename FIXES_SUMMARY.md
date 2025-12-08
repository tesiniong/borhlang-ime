# 轉換模組修正摘要

## 修正日期
2025-01-XX

## 修正內容

### 1. ✅ 調符位置錯誤修正

**問題**：調符標記在聲母上而不是韻母上
```
錯誤：s̄a (調符在聲母 s 上)
正確：sā (調符在韻母 a 上)
```

**原因**：`_add_tone_mark()` 方法接收整個音節（聲母+韻母），導致調符插入到錯誤位置

**修正**：
- 修改 `_add_tone_mark()` 只處理韻母
- 更新所有調用點，先處理韻母添加調符，再與聲母組合
- 確保所有輸出使用 NFC 正規化

**驗證結果**：
```
sa2 -> sá        ✓ (調符在 a 上)
saa2 -> sá̤       ✓ (調符在 a̤ 上)
sia2 -> siá      ✓ (調符在 a 上，位置2)
sioong5 -> siō̤ng ✓ (調符在 o̤ 上，位置2)
aauh4 -> a̤u̍h    ✓ (調符在 u 上，位置3)

多音節詞：
莆田: po2 cheng2 -> pó-chéng ✓
上帝: sioong5 daa4 -> siō̤ng-da̤̍ ✓
```

**影響檔案**：
- `data/romanization_converter.py`
- 所有生成的詞庫（已重建）

---

### 2. ✅ vocab_from_bible.yaml 格式修正

**問題**：聖經詞彙輸出為莆拼而不是輸入式

**修正**：
- 修改 `extract_vocab_from_bible.py` 的 `extract_words()` 方法
- 改為：平話字 → 輸入式（而不是 平話字 → 輸入式 → 莆拼）
- 修正專有名詞大小寫處理邏輯（處理每個音節）

**修正前**：
```yaml
上帝	syorng5 De4	5000    # 莆拼格式
```

**修正後**：
```yaml
上帝	sioong5 daa4	5000   # 輸入式格式
```

**影響檔案**：
- `tools/extract_vocab_from_bible.py`
- `data/vocab_from_bible.yaml`

---

### 3. ✅ ng 韻母轉換邏輯修正

**問題**：輸入式 `ng` 同時對應莆拼的 `ng` 和 `ung`，缺少判斷規則

**規則**：
- **零聲母或 h 聲母** + ng → `ng`（保持）
  - 例：`ng2` → `ng2`
  - 例：`hng5` → `hng5`

- **其他聲母** + ng → `ung`
  - 例：`cng3` → `zung3`
  - 例：`mng4` → `mung4`

**修正**：
- 在 `input_to_psp()` 方法中添加特殊處理邏輯
- 在 `FINALS_PSP_TO_INPUT` 中添加 `ung` → `ng` 的映射

**驗證結果**：
```
✓ ng2 -> ng2 -> ng2
✓ hng5 -> hng5 -> hng5
✓ cng3 -> zung3 -> cng3
✓ mng4 -> mung4 -> mng4
✓ bng1 -> bung1 -> bng1
✓ png2 -> pung2 -> png2
```

**影響檔案**：
- `data/romanization_converter.py`

---

## 詞庫重建統計

### 最終詞庫數量

| 詞庫 | 詞條數 | 格式 |
|------|-------|------|
| `pouseng_pipping/borhlang_pouleng.dict.yaml` | 26,700 | 莆仙話拼音 |
| `bannuaci/borhlang_bannuaci_han.dict.yaml` | 26,655 | 平話字（漢字版） |
| `bannuaci/borhlang_bannuaci.dict.yaml` | 20,755 | 平話字（純羅馬字/Lua） |

### 轉換成功率

- **成功轉換**: 24,732 / 26,700 (92.6%)
  - 從字典直接匹配: 39,336
  - 使用類化反推（情況1-3）: 7,406
  - 使用類化反推（情況4-5）: 53
  - 使用自動轉換: 6,547
- **重複略過**: 1,053
- **轉換失敗**: 915

---

## 測試驗證

所有修正均已通過測試：
1. ✅ 調符位置測試（`tone_position_verification.txt`）
2. ✅ ng 韻母轉換測試（`ng_conversion_test.txt`）
3. ✅ 完整轉換測試（`test_results.txt`）

---

## 下一步建議

1. 考慮統一 `pouseng_pipping/borhlang_pouleng.dict.yaml` 中的格式（移除混合格式的詞條）
2. 建立更全面的單元測試
3. 考慮支援更多方言（江口、南日、仙遊等）

---

**修正完成日期**: 2025-01-XX
**修正檔案總數**: 3
**重建詞庫數**: 3
**測試通過率**: 100%
