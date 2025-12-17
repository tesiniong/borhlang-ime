-- bannuaci_filter.lua (Sentence Composition Support with Case Handling)

-- 不再需要 case_handler - derive 規則保留了 context.input 的原始大小寫

-- 分析輸入的大小寫模式（簡化版本，確保一致性）
local function analyze_case_pattern(input_text)
    if not input_text or input_text == "" then
        return "lower"
    end

    -- 移除非字母字符以分析
    local letters_only = input_text:gsub("[^a-zA-Z]", "")

    if letters_only == "" then
        return "lower"
    end

    -- 檢查是否全大寫（至少2個字母都是大寫）
    if #letters_only >= 2 and letters_only == letters_only:upper() then
        return "all_caps"  -- 每個音節首字母大寫
    end

    -- 檢查首字母是否大寫
    local first_letter = letters_only:sub(1, 1)
    if first_letter == first_letter:upper() then
        return "title"  -- 整個詞首字母大寫
    end

    -- 默認小寫
    return "lower"
end

-- UTF-8 安全的首字母大寫函數
-- 支援預組合字符（如 â, ê）和組合變音符號（如 a̤, e̤）
local function capitalize_first_letter(text)
    if not text or text == "" then
        return text
    end

    -- 預組合拉丁字母的小寫到大寫映射（平話字中實際使用的字符）
    local precomposed_map = {
        -- 帶 circumflex (ˆ) 的字母
        ["â"] = "Â",  -- U+00E2 → U+00C2
        ["ê"] = "Ê",  -- U+00EA → U+00CA
        ["î"] = "Î",  -- U+00EE → U+00CE
        ["ô"] = "Ô",  -- U+00F4 → U+00D4
        ["û"] = "Û",  -- U+00FB → U+00DB

        -- 帶 macron (¯) 的字母
        ["ā"] = "Ā",  -- U+0101 → U+0100
        ["ē"] = "Ē",  -- U+0113 → U+0112
        ["ī"] = "Ī",  -- U+012B → U+012A
        ["ō"] = "Ō",  -- U+014D → U+014C
        ["ū"] = "Ū",  -- U+016B → U+016A

        -- 帶 acute (´) 的字母
        ["á"] = "Á",  -- U+00E1 → U+00C1
        ["é"] = "É",  -- U+00E9 → U+00C9
        ["í"] = "Í",  -- U+00ED → U+00CD
        ["ó"] = "Ó",  -- U+00F3 → U+00D3
        ["ú"] = "Ú",  -- U+00FA → U+00DA

        -- 特殊字符
        ["ṳ"] = "Ṳ",  -- U+1E73 → U+1E72
    }

    -- 方法：逐字節遍歷，識別 UTF-8 字符邊界
    local i = 1
    while i <= #text do
        local byte = text:byte(i)
        local char_len = 1

        -- 判斷 UTF-8 字符長度
        if byte >= 0xF0 then
            char_len = 4
        elseif byte >= 0xE0 then
            char_len = 3
        elseif byte >= 0xC0 then
            char_len = 2
        end

        -- 提取當前字符
        local char = text:sub(i, i + char_len - 1)

        -- 檢查是否為 ASCII 小寫字母
        if char:match("^[a-z]$") then
            local before = text:sub(1, i - 1)
            local upper = char:upper()
            local after = text:sub(i + 1)
            return before .. upper .. after
        end

        -- 檢查是否為預組合小寫字符
        if precomposed_map[char] then
            local before = text:sub(1, i - 1)
            local upper = precomposed_map[char]
            local after = text:sub(i + char_len)
            return before .. upper .. after
        end

        -- 檢查是否為帶組合變音符號的字母（如 a + U+0324 = a̤）
        -- 組合變音符號範圍：U+0300-U+036F (字節序列: 0xCC-0xCD)
        if char:match("^[a-z]$") and i + char_len <= #text then
            local next_byte = text:byte(i + char_len)
            -- 檢查下一個字節是否為組合變音符號的起始字節
            if next_byte and (next_byte == 0xCC or next_byte == 0xCD) then
                -- 只大寫基字母，保留組合變音符號
                local before = text:sub(1, i - 1)
                local upper = char:upper()
                local after = text:sub(i + 1)
                return before .. upper .. after
            end
        end

        i = i + char_len
    end

    -- 沒有找到任何字母，返回原文本
    return text
end

-- 應用大小寫模式到輸出文本
local function apply_case_pattern(text, case_pattern)
    if case_pattern == "lower" or not text or text == "" then
        return text
    end

    if case_pattern == "title" then
        -- 首字母大寫：只將第一個字母大寫
        return capitalize_first_letter(text)
    end

    if case_pattern == "all_caps" then
        -- 每個音節首字母大寫（以連字號分隔）
        local parts = {}
        for part in text:gmatch("[^%-]+") do
            -- 每個音節的首字母大寫
            local capitalized = capitalize_first_letter(part)
            table.insert(parts, capitalized)
        end
        return table.concat(parts, "-")
    end

    return text
end

local function filter(input, env)
    -- 獲取用戶的原始輸入（保留大小寫）
    -- derive 規則保留了 context.input 的原始大小寫
    local context = env.engine.context
    local original_input = context.input or ""

    -- 分析輸入的大小寫模式
    local case_pattern = analyze_case_pattern(original_input)

    for cand in input:iter() do
        local original_text = cand.text

        -- 檢查是否包含我們定義的格式特徵（@ 和 |）
        if original_text:find("@") and original_text:find("|") then
            local buc_parts = {}
            local hanzi_parts = {}
            local is_match = false

            -- 使用 gmatch 循環匹配每一個以 | 結尾的區塊
            -- 模式解析：
            -- ([^@]+)  -> 第一組：平話字 (非 @ 的字元)
            -- @[^@]+@  -> 中間：@輸入碼@ (忽略)
            -- ([^|]+)  -> 第二組：漢字 (非 | 的字元)
            -- |        -> 終止符
            for buc, hanzi in original_text:gmatch("([^@]+)@[^@]+@([^|]+)|") do
                table.insert(buc_parts, buc)
                table.insert(hanzi_parts, hanzi)
                is_match = true
            end

            if is_match then
                -- 組合平話字：用連字號連接，例如 po-seng-u
                local composite_buc = table.concat(buc_parts, "-")

                -- 根據輸入的大小寫模式調整輸出
                composite_buc = apply_case_pattern(composite_buc, case_pattern)

                -- 組合漢字註釋：用空格分隔，例如 (鋪 生 有)
                local composite_hanzi = "(" .. table.concat(hanzi_parts, " ") .. ")"

                -- 建立新的候選詞
                local new_cand = cand:to_shadow_candidate(
                    cand.type,
                    composite_buc,
                    composite_hanzi
                )
                yield(new_cand)
            else
                -- 有特殊符號但解析失敗（防禦性代碼），輸出原形
                yield(cand)
            end
        else
            -- 完全不匹配格式（例如是用戶詞典裡的舊資料），直接輸出
            yield(cand)
        end
    end
end

return filter