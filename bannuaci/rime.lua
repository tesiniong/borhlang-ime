-- rime.lua
-- Rime Lua 擴充套件入口檔案

-- 載入並註冊興化平話字過濾器（支援智能句式組合和大小寫處理）
bannuaci_filter = require("bannuaci_filter")

-- 載入並註冊註釋格式化過濾器（用於反查：將輸入式平話字轉換為真實平話字）
comment_formatter = require("comment_formatter")
