-- bannuaci_filter.lua
-- 興化平話字過濾器 (Báⁿ-uā-ci̍ Filter)
-- 
-- 功能摘要：
-- 1. 將輸入式平話字轉換為顯示用的真平話字（處理變音符號）。
-- 2. 在組詞過程中，若音節未結束自動補上連字號。
-- 3. 支援 PascalCase (KiTau -> Kî-Táu) 與部分匹配大小寫 (AaS -> Á̤-Suah)。
--
-- [警告] 維護須知：
-- 本腳本邏輯處理了許多邊界情況。
-- 在修改代程式碼前，請務必閱讀相關區塊的註釋，了解「為什麼這麼寫」。
-- 尤其是「貪婪匹配 (Greedy Matching)」與「連字號長度計算」部分，請勿輕易改回簡單的全域判斷。

local M = {}

-- 字串分割輔助函數
local function split(str, sep)
   local t = {}
   for s in string.gmatch(str, "([^"..sep.."]+)") do
      table.insert(t, s)
   end
   return t
end

-- UTF-8 安全的首字母大寫函數
-- 為什麼需要這個？
-- 因為 Lua 標準庫不支援 UTF-8，且平話字包含許多預組合字符 (如 Ê) 和組合變音符號。
-- 簡單的 string.upper() 會破壞這些多字節字符。
local function capitalize_first_letter(text)
    if not text or text == "" then return text end
    
    local precomposed_map = {
        ["â"] = "Â", ["ê"] = "Ê", ["î"] = "Î", ["ô"] = "Ô", ["û"] = "Û",
        ["ā"] = "Ā", ["ē"] = "Ē", ["ī"] = "Ī", ["ō"] = "Ō", ["ū"] = "Ū",
        ["á"] = "Á", ["é"] = "É", ["í"] = "Í", ["ó"] = "Ó", ["ú"] = "Ú",
        ["ṳ"] = "Ṳ",
    }

    local i = 1
    while i <= #text do
        local byte = text:byte(i)
        local char_len = 1
        if byte >= 0xF0 then char_len = 4
        elseif byte >= 0xE0 then char_len = 3
        elseif byte >= 0xC0 then char_len = 2 end

        local char = text:sub(i, i + char_len - 1)
        
        -- 情況 1: ASCII 小寫字母 -> 直接轉大寫
        if char:match("^[a-z]$") then
            return text:sub(1, i - 1) .. char:upper() .. text:sub(i + 1)
        end
        
        -- 情況 2: 預組合字符 (Precomposed) -> 查表替換
        if precomposed_map[char] then
            return text:sub(1, i - 1) .. precomposed_map[char] .. text:sub(i + char_len)
        end
        
        -- 情況 3: 組合變音符號 (Combining Diacritics)
        -- 例如 a + 0xCC 0xA4 (a̤)。我們只大寫基字母，保留後面的變音符號。
        if char:match("^[a-z]$") and i + char_len <= #text then
            local next_byte = text:byte(i + char_len)
            -- 檢查下一個字節是否為組合符號的開頭 (通常落在 0xCC, 0xCD 範圍)
            if next_byte and (next_byte == 0xCC or next_byte == 0xCD) then
                return text:sub(1, i - 1) .. char:upper() .. text:sub(i + 1)
            end
        end
        i = i + char_len
    end
    return text
end

-- 檢查字串是否以大寫字母開頭 (用於判斷使用者意圖)
local function starts_with_upper(text)
    if not text or text == "" then return false end
    local first_char = text:sub(1, 1)
    return first_char:match("^[A-Z]") ~= nil
end

local function filter(input, env)
    local context = env.engine.context
    local input_text = context.input or ""
    local input_len = input_text:len()
    
    -- [關鍵邏輯 1] 計算「當前分詞」的相對位置
    -- 我們不能直接用 input_len，因為在長句輸入時，Rime 會分段處理。
    -- context.composition:back().start 告訴我們當前正在修改的這個詞是從哪裡開始的。
    local current_segment_start = 0
    if context.composition and not context.composition:empty() then
        local seg = context.composition:back()
        if seg then
            current_segment_start = seg.start
        end
    end

    -- 截取當前正在處理的輸入片段 (例如 "KiTau")
    local active_input_segment = input_text:sub(current_segment_start + 1)
    
    -- 建立參考字串：移除數字和符號，只保留字母，用於跟詞典的 Code 進行比對
    -- 這是為了處理像 "Ki'Tau" 這樣帶分隔符的輸入
    local casing_reference = active_input_segment:gsub("[^a-zA-Z]", "")
    
    -- 計算剩餘的有效輸入長度 (用於判斷是否要在詞尾加連字號)
    local active_input_len = input_len - current_segment_start

    for cand in input:iter() do
        local original_text = cand.text
        
        -- 檢查候選詞是否為特定格式：buc@code@hanzi|
        -- 這種格式允許我們同時獲取顯示文字、拼音碼和漢字
        if original_text:find("@") and original_text:find("|") then
            local raw_parts = {}
            local total_code_len = 0
            local hanzi_parts = {}
            
            -- [關鍵邏輯 2] 先收集，後處理 (Fix User Dictionary Bug)
            -- 使用者自造詞 (User Phrase) 在 Rime 中會被存成多個 segment 串接的形式：
            -- "kî@ki5@Hanzi|táu@tau2@Hanzi|"
            -- 如果使用 gmatch 邊讀邊覆蓋變數，會導致前面的音節丟失。
            -- 因此必須先用 table 收集所有 raw_parts。
            for buc_str, code_str, hanzi in original_text:gmatch("([^@]+)@([^@]+)@([^|]+)|") do
                local clean_part_code = code_str:gsub("[%d%s]", "") -- 移除聲調數字和空格
                total_code_len = total_code_len + clean_part_code:len()
                
                table.insert(raw_parts, {
                    buc = buc_str,
                    code = code_str,
                    clean_code = clean_part_code
                })
                table.insert(hanzi_parts, hanzi)
            end

            if #raw_parts > 0 then
                local final_buc_parts = {}
                local input_cursor = 1 -- 指向 casing_reference 的游標
                
                -- [關鍵邏輯 3] 拉鍊式貪婪匹配 (Zipper Greedy Matching)
                -- 這是為了解決混合大小寫 (KiTau) 和部分匹配 (AaS, GiD) 的問題。
                -- 我們不使用全域模式 (Global Case Pattern)，因為它無法處理駝峰式命名。
                -- 我們也不區分「全拼」或「縮寫」，而是使用統一的邏輯：
                -- 逐個字母比對輸入與拼音碼，如果匹配且輸入為大寫，則輸出大寫。
                
                for _, part in ipairs(raw_parts) do
                    local buc_syls = split(part.buc, "-")
                    local code_syls = split(part.code, " ")
                    
                    local part_processed_syls = {}
                    
                    for i = 1, #buc_syls do
                        local b = buc_syls[i]
                        -- 獲取該音節的拼音碼 (移除數字)，例如 "suah"
                        -- fallback: 如果 code 分割後數量不對，使用整個 part 的 clean_code
                        local c = (code_syls[i] or part.clean_code):gsub("[%d]", "")
                        
                        -- A. 檢查首字母匹配
                        local input_char = casing_reference:sub(input_cursor, input_cursor)
                        local code_char = c:sub(1, 1)
                        
                        -- 如果輸入字母存在且與拼音首字母相同 (忽略大小寫)
                        if input_char ~= "" and code_char ~= "" and input_char:lower() == code_char:lower() then
                            
                            -- 大小寫判定：如果使用者輸入大寫，則將該音節首字母大寫
                            if starts_with_upper(input_char) then
                                b = capitalize_first_letter(b)
                            end
                            
                            -- 消耗這個輸入字母
                            input_cursor = input_cursor + 1
                            
                            -- B. 貪婪消耗 (Greedy Consume)
                            -- 繼續檢查該音節剩餘的拼音字母，盡可能消耗輸入串
                            -- 這使得 KiTau (全拼) 能正確消耗完 Ki，將 cursor 移給 Tau
                            -- 也使得 GD (縮寫) 在消耗 G 後，因為 D 不匹配 i 而停止，將 cursor D 留給下一個音節 Doh
                            for j = 2, c:len() do
                                local next_input = casing_reference:sub(input_cursor, input_cursor)
                                local next_code = c:sub(j, j)
                                
                                if next_input ~= "" and next_input:lower() == next_code:lower() then
                                    input_cursor = input_cursor + 1
                                else
                                    -- 一旦不匹配 (例如縮寫情況)，停止消耗此音節
                                    break
                                end
                            end
                        else
                            -- 首字母不匹配 (Fuzzy 或 容錯輸入)，保持原樣不變大寫
                        end
                        
                        table.insert(part_processed_syls, b)
                    end
                    table.insert(final_buc_parts, table.concat(part_processed_syls, "-"))
                end

                local composite_buc = table.concat(final_buc_parts, "-")

                -- [關鍵邏輯 4] 連字號自動補全
                -- 為什麼不用 cand.end? 
                -- 因為在某些 Rime 版本或 Simplifier 之後，cand.end 可能為 nil 或不準確。
                -- 我們比較「詞典拼音總長度」與「當前有效輸入長度」：
                -- 若 Code < Input，代表使用者還輸入了後續的詞，因此當前詞後面應加連字號。
                if total_code_len < active_input_len then
                    composite_buc = composite_buc .. "-"
                end

                local composite_hanzi = "(" .. table.concat(hanzi_parts, " ") .. ")"

                -- 建立 Shadow Candidate 覆蓋原候選詞
                local new_cand = cand:to_shadow_candidate(
                    cand.type,
                    composite_buc,
                    composite_hanzi
                )
                yield(new_cand)
            else
                -- 極少見情況：有特殊符號但解析失敗，原樣輸出避免丟失
                yield(cand)
            end
        else
            -- 普通候選詞，原樣輸出
            yield(cand)
        end
    end
end

return filter