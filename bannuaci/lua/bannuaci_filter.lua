-- bannuaci_filter.lua (Sentence Composition Support)
local function filter(input, env)
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
                -- 有特殊符號但解析失敗（防禦性代碼），輸出原形但去掉 |
                yield(cand) 
            end
        else
            -- 完全不匹配格式（例如是用戶詞典裡的舊資料），直接輸出
            yield(cand)
        end
    end
end

return filter