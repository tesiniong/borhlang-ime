#!/bin/bash
# deploy_to_rime.sh
# 木蘭輸入法 - 部署到 Rime（Linux）
# Borhlang IME - Deploy to Rime (Linux)

set -e  # 發生錯誤時退出

echo "========================================"
echo "木蘭輸入法 - 部署到 Rime"
echo "Borhlang IME - Deploy to Rime"
echo "========================================"
echo

# 取得腳本所在目錄
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE_DIR="$SCRIPT_DIR/bannuaci"

echo "來源目錄: $SOURCE_DIR"
echo

# 檢查來源目錄是否存在
if [ ! -d "$SOURCE_DIR" ]; then
    echo "[錯誤] 找不到來源目錄: $SOURCE_DIR"
    exit 1
fi

# 偵測 Rime 目錄
RIME_DIR=""
RIME_TYPE=""

# 檢查 fcitx5-rime
if [ -d "$HOME/.local/share/fcitx5/rime" ]; then
    RIME_DIR="$HOME/.local/share/fcitx5/rime"
    RIME_TYPE="fcitx5"
# 檢查 ibus-rime
elif [ -d "$HOME/.config/ibus/rime" ]; then
    RIME_DIR="$HOME/.config/ibus/rime"
    RIME_TYPE="ibus"
# 檢查 fcitx-rime (舊版)
elif [ -d "$HOME/.config/fcitx/rime" ]; then
    RIME_DIR="$HOME/.config/fcitx/rime"
    RIME_TYPE="fcitx"
else
    echo "[錯誤] 找不到 Rime 配置目錄"
    echo
    echo "已嘗試以下路徑："
    echo "  - $HOME/.local/share/fcitx5/rime (fcitx5-rime)"
    echo "  - $HOME/.config/ibus/rime (ibus-rime)"
    echo "  - $HOME/.config/fcitx/rime (fcitx-rime)"
    echo
    echo "請確認已安裝 Rime 輸入法框架"
    exit 1
fi

echo "偵測到: $RIME_TYPE"
echo "目標目錄: $RIME_DIR"
echo

# 詢問用戶是否繼續
read -p "是否繼續部署？(y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "已取消部署"
    exit 0
fi

echo
echo "[步驟 1/3] 刪除舊檔案..."
echo

# 刪除可能存在的舊檔案
if [ -f "$RIME_DIR/borhlang_bannuaci_pure.dict.yaml" ]; then
    rm "$RIME_DIR/borhlang_bannuaci_pure.dict.yaml"
    echo "  已刪除: borhlang_bannuaci_pure.dict.yaml"
fi

echo
echo "[步驟 2/3] 複製新檔案..."
echo

# 複製 Schema 檔案
copy_file() {
    local src="$1"
    local dest="$2"
    local name="$3"

    if cp "$src" "$dest"; then
        echo "  [✓] $name"
        return 0
    else
        echo "  [✗] $name - 複製失敗"
        return 1
    fi
}

# 複製 Schema 檔案
copy_file "$SOURCE_DIR/borhlang_bannuaci.schema.yaml" "$RIME_DIR/" "borhlang_bannuaci.schema.yaml"
copy_file "$SOURCE_DIR/borhlang_bannuaci_han.schema.yaml" "$RIME_DIR/" "borhlang_bannuaci_han.schema.yaml"

# 複製詞庫檔案
copy_file "$SOURCE_DIR/borhlang_bannuaci.dict.yaml" "$RIME_DIR/" "borhlang_bannuaci.dict.yaml"
copy_file "$SOURCE_DIR/borhlang_bannuaci_han.dict.yaml" "$RIME_DIR/" "borhlang_bannuaci_han.dict.yaml"

# 創建 lua 子目錄（如果不存在）
mkdir -p "$RIME_DIR/lua"

# 複製 Lua 檔案
copy_file "$SOURCE_DIR/lua/bannuaci_filter.lua" "$RIME_DIR/lua/" "lua/bannuaci_filter.lua"
copy_file "$SOURCE_DIR/lua/comment_formatter.lua" "$RIME_DIR/lua/" "lua/comment_formatter.lua"
copy_file "$SOURCE_DIR/lua/reverse_lookup_helper.lua" "$RIME_DIR/lua/" "lua/reverse_lookup_helper.lua"
copy_file "$SOURCE_DIR/rime.lua" "$RIME_DIR/" "rime.lua"

echo
echo "[步驟 3/3] 部署完成！"
echo

# 根據不同的輸入法框架給出重新部署指示
echo "========================================"
echo "接下來請執行以下操作："
echo

case "$RIME_TYPE" in
    fcitx5)
        echo "1. 重新部署 Rime："
        echo "   方法A（命令列）："
        echo "     rm ~/.local/share/fcitx5/rime/default.yaml"
        echo "     fcitx5-remote -r"
        echo
        echo "   方法B（圖形介面）："
        echo "     右鍵點擊 fcitx5 托盤圖示"
        echo "     選擇「部署」或「Deploy」"
        echo
        echo "2. 等待部署完成（約 10-30 秒）"
        echo "3. 按 Ctrl+Space 切換輸入法"
        echo "4. 按 Ctrl+Shift+F 選擇輸入方案"
        echo "5. 選擇「興化平話字」開始使用"
        ;;
    ibus)
        echo "1. 重新部署 Rime："
        echo "   方法A（命令列）："
        echo "     rm ~/.config/ibus/rime/default.yaml"
        echo "     ibus-daemon -drx"
        echo
        echo "   方法B（圖形介面）："
        echo "     右鍵點擊 ibus 托盤圖示"
        echo "     選擇「部署」或「Deploy」"
        echo
        echo "2. 等待部署完成（約 10-30 秒）"
        echo "3. 按 Ctrl+Space 切換輸入法"
        echo "4. 按 F4 或 Ctrl+` 選擇輸入方案"
        echo "5. 選擇「興化平話字」開始使用"
        ;;
    fcitx)
        echo "1. 重新部署 Rime："
        echo "   命令列："
        echo "     rm ~/.config/fcitx/rime/default.yaml"
        echo "     fcitx-remote -r"
        echo
        echo "2. 等待部署完成（約 10-30 秒）"
        echo "3. 按 Ctrl+Space 切換輸入法"
        echo "4. 按 Ctrl+` 選擇輸入方案"
        echo "5. 選擇「興化平話字」開始使用"
        ;;
esac

echo "========================================"
echo

# 詢問是否立即部署（僅限 fcitx5 和 ibus）
if [ "$RIME_TYPE" = "fcitx5" ] || [ "$RIME_TYPE" = "ibus" ]; then
    read -p "是否現在立即重新部署？(y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "正在重新部署..."

        if [ "$RIME_TYPE" = "fcitx5" ]; then
            rm -f "$HOME/.local/share/fcitx5/rime/default.yaml"
            if command -v fcitx5-remote &> /dev/null; then
                fcitx5-remote -r
                echo "部署完成！"
            else
                echo "[警告] 找不到 fcitx5-remote 命令，請手動重新部署"
            fi
        elif [ "$RIME_TYPE" = "ibus" ]; then
            rm -f "$HOME/.config/ibus/rime/default.yaml"
            if command -v ibus-daemon &> /dev/null; then
                ibus-daemon -drx
                echo "部署完成！"
            else
                echo "[警告] 找不到 ibus-daemon 命令，請手動重新部署"
            fi
        fi
    fi
fi

echo
echo "部署腳本執行完畢"
