-- rime.lua
-- Rime Lua 擴充套件入口檔案

-- 載入並註冊興化平話字過濾器（支援智能句式組合和大小寫處理）
bannuaci_filter = require("bannuaci_filter")

-- 載入並註冊註釋格式化過濾器（用於反查：將輸入式平話字轉換為真實平話字）
comment_formatter = require("comment_formatter")

-- 載入反查輔助模組（用於純羅馬字版反查：建立漢字到平話字的映射表）
reverse_lookup_helper = require("reverse_lookup_helper")

-- 初始化反查輔助模組
local success, msg = reverse_lookup_helper.init()
if success then
    -- 初始化成功，詞典已載入
else
    -- 初始化失敗，記錄錯誤（Rime 會在日誌中顯示）
    error("Failed to initialize reverse_lookup_helper: " .. (msg or "unknown error"))
end
