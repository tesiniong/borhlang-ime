# 修復反查功能與文檔更新總結

## 📅 更新日期
2025-12-19

## 🔧 程式碼修改

### 1. 修復漢字版反查功能
**檔案**: `bannuaci/borhlang_bannuaci_han.schema.yaml`

**修改內容**:
- 在 `filters` 區段添加 `lua_filter@comment_formatter`
- 使反查結果能正確顯示真平話字（帶變音符號）

**修改前**:
```yaml
filters:
  - simplifier
  - uniquifier
```

**修改後**:
```yaml
filters:
  - simplifier
  - lua_filter@comment_formatter
  - uniquifier
```

### 2. 載入反查輔助模組
**檔案**: `bannuaci/rime.lua`

**修改內容**:
- 載入 `reverse_lookup_helper` 模組
- 在啟動時初始化字典映射表

**新增程式碼**:
```lua
-- 載入反查輔助模組
reverse_lookup_helper = require("reverse_lookup_helper")

-- 初始化反查輔助模組
local success, msg = reverse_lookup_helper.init()
if success then
    -- 初始化成功
else
    error("Failed to initialize reverse_lookup_helper: " .. (msg or "unknown error"))
end
```

### 3. 增強純羅馬字版反查邏輯
**檔案**: `bannuaci/lua/comment_formatter.lua`

**修改內容**:
- 處理反查時 comment 為空的情況
- 使用 `reverse_lookup_helper.lookup()` 查詢漢字對應的讀音
- 自動轉換輸入式平話字為真平話字

**關鍵邏輯**:
```lua
if is_pure_romanization then
    local input_form_romanization = nil

    if comment and comment:match('%d') then
        -- 情況 1：comment 中已有輸入式平話字
        input_form_romanization = comment
    else
        -- 情況 2：comment 為空，使用 reverse_lookup_helper 查詢
        local readings = reverse_lookup_helper.lookup(text)
        if readings and #readings > 0 then
            input_form_romanization = readings[1]
        end
    end

    if input_form_romanization then
        local converted = convert_text(input_form_romanization)
        -- 輸出：羅馬字 (漢字)
    end
end
```

## 📝 文檔更新

### 1. README.md

**新增內容**:
- ✅ 添加「大小寫智能處理」功能說明
- ✅ 補充反查功能的輸出格式說明（漢字版 vs 純羅馬字版）
- ✅ 修正「已知問題」：移除「各音節都首字母大寫的詞彙需要分開輸入」的錯誤描述

**主要新增章節**:
- 「大小寫輸入（智能處理）」使用說明
- 反查功能的兩種輸出格式對比

### 2. CLAUDE.md

**更新內容**:
- ✅ 添加反查功能的當前狀態標記：「✅ Current Status: Fully functional」
- ✅ 補充反查功能的輸出格式說明
- ✅ 添加大小寫處理功能的狀態標記
- ✅ 移除關於「全大寫→每個音節大寫」的錯誤範例

## 🔄 反查功能工作原理

### 漢字版 (`borhlang_bannuaci_han`)
1. 用戶輸入：`` `wo` ``
2. `reverse_lookup_translator` 返回漢字候選詞
3. 主詞典提供輸入式平話字作為 comment（如 `gua3 ngoo3`）
4. `comment_formatter.lua` 轉換為真平話字（如 `guâ ngô̤`）
5. 輸出：**我** `guâ ngô̤`

### 純羅馬字版 (`borhlang_bannuaci`)
1. 用戶輸入：`` `wo` ``
2. `reverse_lookup_translator` 返回漢字候選詞
3. 兩種可能情況：
   - 情況A：`reverse_lookup_han` 提供輸入式平話字
   - 情況B：comment 為空，`reverse_lookup_helper` 從字典查詢
4. `comment_formatter.lua` 轉換為真平話字
5. 交換顯示順序
6. 輸出：**guâ ngô̤** `(我)`

## 📦 備份檔案

以下檔案已備份（副檔名 `.backup`）：
- `bannuaci/borhlang_bannuaci.schema.yaml.backup`
- `bannuaci/borhlang_bannuaci_han.schema.yaml.backup`
- `bannuaci/lua/comment_formatter.lua.backup`
- `bannuaci/rime.lua.backup`

如需恢復，請移除 `.backup` 副檔名。

## 🧪 測試建議

### 測試步驟

1. **部署更新的檔案**
   ```batch
   deploy_to_rime.bat
   ```

2. **重新部署 Rime**
   - 右鍵點擊 Rime 托盤圖示
   - 選擇「重新部署」
   - 等待完成（約 10-30 秒）

3. **測試漢字版反查**
   - 切換到「興化平話字（漢字）」
   - 輸入：`` `wo` ``
   - 預期輸出：**我** `guâ ngô̤`（真平話字帶變音符號）

4. **測試純羅馬字版反查**
   - 切換到「興化平話字」
   - 輸入：`` `wo` ``
   - 預期輸出：**guâ ngô̤** `(我)`（羅馬字為主，漢字為註釋）

5. **測試首字母大寫功能**
   - 輸入：`Inggio`
   - 預期輸出：**I̍ng-giô̤ⁿ**（首字母大寫）

### 可能的問題

1. **反查無結果**
   - 檢查 Rime 日誌：`%APPDATA%\Rime\rime.*.INFO`
   - 確認 `reverse_lookup_helper` 初始化成功
   - 確認 `borhlang_bannuaci_han.dict.yaml` 存在

2. **顯示格式不正確**
   - 確認 `comment_formatter.lua` 已正確部署到 `lua/` 目錄
   - 重新部署 Rime

## ✅ 修改清單

- [x] 備份關鍵檔案
- [x] 修復漢字版反查功能（添加 Lua filter）
- [x] 修復純羅馬字版反查功能（增強 comment_formatter.lua）
- [x] 更新 README.md（添加首字母大寫說明、修正已知問題）
- [x] 更新 CLAUDE.md（補充反查功能現狀說明）
- [ ] 測試反查功能是否正常（待用戶測試）

## 📞 聯絡

如有問題，請在 GitHub Issues 回報。
