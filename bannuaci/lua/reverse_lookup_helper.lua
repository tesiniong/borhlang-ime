-- reverse_lookup_helper.lua
-- 反查輔助模組：建立漢字到平話字的映射表

local M = {}

-- 漢字到平話字讀音的映射表
M.hanzi_to_readings = {}

-- 讀取詞典文件並建立映射表
function M.load_dictionary(dict_path)
    local file = io.open(dict_path, "r")
    if not file then
        return false, "Cannot open dictionary file: " .. dict_path
    end

    local in_data_section = false
    local line_count = 0

    for line in file:lines() do
        line_count = line_count + 1

        -- 跳過註釋和空行
        if line:match("^%s*#") or line:match("^%s*$") then
            goto continue
        end

        -- 檢查是否到達數據區
        if line:match("^%.%.%.$") then
            in_data_section = true
            goto continue
        end

        -- 只處理數據區的內容
        if in_data_section then
            -- 解析格式：漢字\t拼音\t權重
            -- 使用 tab 分隔
            local hanzi, reading = line:match("^([^\t]+)\t([^\t]+)")

            if hanzi and reading then
                -- 移除讀音中的空格和數字，只保留基本形式
                -- 但我們需要保留完整的讀音（帶數字）
                if not M.hanzi_to_readings[hanzi] then
                    M.hanzi_to_readings[hanzi] = {}
                end

                -- 避免重複
                local already_exists = false
                for _, r in ipairs(M.hanzi_to_readings[hanzi]) do
                    if r == reading then
                        already_exists = true
                        break
                    end
                end

                if not already_exists then
                    table.insert(M.hanzi_to_readings[hanzi], reading)
                end
            end
        end

        ::continue::
    end

    file:close()
    return true, "Loaded " .. line_count .. " lines"
end

-- 查詢漢字的平話字讀音
function M.lookup(hanzi)
    return M.hanzi_to_readings[hanzi]
end

-- 初始化
function M.init()
    -- 嘗試多個可能的路徑
    local possible_paths = {
        "C:/Users/Siniong/AppData/Roaming/Rime/borhlang_bannuaci_han.dict.yaml",
        os.getenv("APPDATA") .. "/Rime/borhlang_bannuaci_han.dict.yaml",
    }

    for _, path in ipairs(possible_paths) do
        local success, msg = M.load_dictionary(path)
        if success then
            return true, msg
        end
    end

    return false, "Failed to load dictionary from all paths"
end

return M
