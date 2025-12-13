-- bannuaci_filter.lua (Sentence Composition Support with Case Handling)

-- 分析輸入的大小寫模式
local function analyze_case_pattern(input_text)
    if not input_text or input_text == "" then
        return "lower"
    end

    -- 移除非字母字符以分析
    local letters_only = input_text:gsub("[^a-zA-Z]", "")

    if letters_only == "" then
        return "lower"
    end

    -- 檢查是否全大寫
    if letters_only == letters_only:upper() then
        return "all_caps"  -- 每個音節首字母大寫
    end

    -- 檢查是否首字母大寫
    local first_letter = letters_only:sub(1, 1)
    local rest = letters_only:sub(2)

    if first_letter == first_letter:upper() and rest == rest:lower() then
        return "title"  -- 整個詞首字母大寫
    end

    -- 默認小寫
    return "lower"
end

-- UTF-8 安全的首字母大寫函數
local function capitalize_first_letter(text)
    if not text or text == "" then
        return text
    end

    -- 查找第一個 ASCII 字母
    local pos = text:find("[a-z]")
    if not pos then
        return text  -- 沒有小寫字母，直接返回
    end

    -- 將找到的字母大寫
    local before = text:sub(1, pos - 1)
    local letter = text:sub(pos, pos):upper()
    local after = text:sub(pos + 1)

    return before .. letter .. after
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