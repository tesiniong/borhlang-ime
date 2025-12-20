-- comment_formatter.lua
-- 將反查結果的註釋從輸入式平話字轉換為真平話字

-- 聲母列表（用於分離聲母和韻母）
local INITIALS = {'ch', 'ng', 'b', 'p', 'm', 'd', 't', 'n', 'l', 'g', 'k', 'h', 'c', 's', ''}

-- 聲調符號位置表（來自 generate_pure_bannuaci_dict.py）
-- 位置從 1 開始計數（Lua 風格），指的是在「已轉換的韻母」中的位置
local TONE_POSITIONS = {
    -- 單字母
    a = 1, aa = 1, e = 1, ee = 1, oo = 1,
    i = 1, o = 1, u = 1, y = 1,

    -- 多字母
    ai = 1, au = 1, aau = 2, eo = 2,
    ia = 2, ioo = 2, iu = 2, oi = 1,
    ua = 2, uai = 2, ui = 1, io = 2,

    -- 鼻音韻
    ng = 1, ang = 1, eng = 1, ing = 1, eong = 2,
    eeng = 1, oong = 1, iang = 2, uang = 2, yng = 1,
    ioong = 2,

    -- 鼻化韻
    ann = 1, aann = 1, eenn = 1, oonn = 1,
    iann = 2, oinn = 1, uann = 2, aaann = 2,
    ioonn = 2,

    -- 入聲韻
    ah = 1, aih = 1, aah = 1, aauh = 3,
    eh = 1, eeh = 1, eoh = 2, iah = 2,
    ih = 1, iooh = 2, oih = 1, ooh = 1,
    uah = 2, uh = 1, yh = 1,
}

-- 特殊字符替換（aa→a̤, ee→e̤, oo→o̤, y→ṳ, nn→ⁿ）
local function apply_replacements(text)
    -- 使用 UTF-8 組合字符
    text = text:gsub('aa', 'a\u{0324}')  -- a + combining diaeresis below
    text = text:gsub('ee', 'e\u{0324}')  -- e + combining diaeresis below
    text = text:gsub('oo', 'o\u{0324}')  -- o + combining diaeresis below
    text = text:gsub('y', '\u{1E73}')    -- ṳ (Latin small letter u with diaeresis below)
    text = text:gsub('nn', '\u{207F}')   -- ⁿ (superscript n)
    return text
end

-- UTF-8 字符串長度（計算字符數而非字節數）
local function utf8_len(s)
    local _, count = s:gsub('[^\128-\193]', '')
    return count
end

-- UTF-8 字符串插入（在指定位置插入字符）
local function utf8_insert(str, pos, insert_str)
    if pos > utf8_len(str) then
        pos = utf8_len(str)
    end

    local byte_pos = 0
    local char_count = 0

    for p, c in utf8.codes(str) do
        if char_count >= pos then
            byte_pos = p
            break
        end
        char_count = char_count + 1
    end

    if byte_pos == 0 then
        return str .. insert_str
    else
        return str:sub(1, byte_pos - 1) .. insert_str .. str:sub(byte_pos)
    end
end

-- 將單個音節從輸入式轉換為平話字
local function convert_syllable(input_syl)
    -- 檢查是否包含聲調數字
    local tone = input_syl:match('(%d)$')
    if not tone then
        -- 沒有聲調數字，直接替換特殊字符
        return apply_replacements(input_syl)
    end

    local base = input_syl:sub(1, -2)  -- 移除最後的數字

    -- 分離聲母和韻母
    local initial = ''
    local final = base

    -- 按長度排序，優先匹配長聲母（如 ch, ng）
    for _, init in ipairs(INITIALS) do
        if init ~= '' and base:sub(1, #init) == init then
            local remainder = base:sub(#init + 1)

            -- 特殊處理：韻化輔音（m, ng）
            if remainder == '' and (init == 'm' or init == 'ng') then
                initial = ''
                final = base
            else
                initial = init
                final = remainder
            end
            break
        end
    end

    -- 處理韻母替換（aa→a̤ 等）
    local processed_final = apply_replacements(final)

    -- 決定聲調符號
    local ends_with_h = final:sub(-1) == 'h'
    local tone_marks = {
        ['1'] = '',
        ['2'] = '\u{0301}',  -- ́ acute accent
        ['3'] = '\u{0302}',  -- ̂ circumflex
        ['4'] = '\u{030D}',  -- ̍ vertical line above
        ['5'] = '\u{0304}',  -- ̄ macron
        ['6'] = (not ends_with_h) and '\u{0304}' or '',  -- tone 6
        ['7'] = '\u{030D}',  -- ̍ vertical line above (same as tone 4)
        ['8'] = '',
    }

    local tone_mark = tone_marks[tone] or ''

    if tone_mark == '' then
        -- 無聲調符號，直接返回
        return initial .. processed_final
    end

    -- 查找聲調位置（使用原始韻母查表）
    local position = TONE_POSITIONS[final] or 1

    -- 插入聲調符號到已處理的韻母中
    local final_with_tone = utf8_insert(processed_final, position, tone_mark)

    return initial .. final_with_tone
end

-- 轉換整個文本（多個音節用空格分隔）
local function convert_text(input_text)
    if not input_text or input_text == '' then
        return input_text
    end

    local syllables = {}
    for syl in input_text:gmatch('%S+') do
        table.insert(syllables, convert_syllable(syl))
    end

    return table.concat(syllables, ' ')
end

-- 解析特殊格式的候選文本（用於純羅馬字版）
-- 格式：guâ@gua3@我| 或 guâ@gua3@我|/ngô̤@ngoo3@我|
local function parse_special_format(text)
    local buc_parts = {}
    local hanzi_parts = {}
    local code_parts = {}
    local is_match = false

    -- 匹配模式：romanization@code@hanzi|
    for buc, code, hanzi in text:gmatch("([^@]+)@([^@]+)@([^|]+)|") do
        table.insert(buc_parts, buc)
        table.insert(code_parts, code)
        table.insert(hanzi_parts, hanzi)
        is_match = true
    end

    if is_match then
        return {
            romanization = table.concat(buc_parts, " "),  -- 用空格分隔不同讀音
            code = table.concat(code_parts, " "),
            hanzi = table.concat(hanzi_parts, " ")
        }
    end

    return nil
end

-- 檢測當前 schema
local function get_current_schema(env)
    local schema_id = env.engine.schema.schema_id or ""
    return schema_id
end

-- 主過濾器函數
local function filter(input, env)
    -- 檢查是否為反查模式（輸入以 ` 開頭）
    local context = env.engine.context
    local user_input = context.input or ""
    local is_reverse_lookup = user_input:sub(1, 1) == "`"

    -- 檢查當前 schema
    local schema_id = get_current_schema(env)
    local is_pure_romanization = (schema_id == "borhlang_bannuaci")

    for cand in input:iter() do
        local comment = cand.comment
        local text = cand.text

        -- 反查模式
        if is_reverse_lookup then
            -- 純羅馬字版的反查
            if is_pure_romanization then
                -- 反查時可能有兩種情況：
                -- 1. comment 有內容（來自 reverse_lookup_han）：輸入式平話字
                -- 2. comment 為空（來自 luna_pinyin）：需要從 reverse_lookup_helper 查詢

                local input_form_romanization = nil

                if comment and comment:match('%d') then
                    -- 情況 1：comment 中已有輸入式平話字
                    input_form_romanization = comment
                else
                    -- 情況 2：comment 為空，使用 reverse_lookup_helper 查詢
                    local readings = reverse_lookup_helper.lookup(text)
                    if readings and #readings > 0 then
                        -- 使用第一個讀音（可以考慮顯示所有讀音）
                        input_form_romanization = readings[1]
                    end
                end

                if input_form_romanization then
                    -- 轉換輸入式平話字為真平話字
                    local converted = convert_text(input_form_romanization)

                    -- 創建新的候選詞：羅馬字作為主顯示，漢字作為註釋
                    local new_cand = cand:to_shadow_candidate(
                        cand.type,
                        converted,  -- 羅馬字作為主顯示
                        "(" .. text .. ")"  -- 漢字作為註釋
                    )
                    yield(new_cand)
                else
                    -- 無法找到讀音，直接輸出原候選詞
                    yield(cand)
                end

            -- 漢字版的反查
            elseif not is_pure_romanization and comment and comment:match('%d') then
                -- text: 漢字
                -- comment: 輸入式平話字

                -- 轉換 comment 為真平話字
                local converted = convert_text(comment)

                local new_cand = cand:to_shadow_candidate(
                    cand.type,
                    cand.text,  -- 漢字
                    converted   -- 真平話字
                )
                yield(new_cand)
            else
                -- 其他反查結果，直接輸出
                yield(cand)
            end
        else
            -- 非反查模式
            -- 只處理 comment 中的輸入式平話字（主要用於漢字版）
            if comment and comment:match('%d') then
                local converted = convert_text(comment)

                local new_cand = cand:to_shadow_candidate(
                    cand.type,
                    cand.text,
                    converted
                )
                yield(new_cand)
            else
                -- 不需要轉換，直接輸出（包括純羅馬字版的正常輸入）
                yield(cand)
            end
        end
    end
end

return filter
