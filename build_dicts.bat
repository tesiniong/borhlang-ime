@echo off
chcp 65001 >nul
echo ========================================
echo 木蘭輸入法詞表一鍵更新
echo Borhlang IME - Dictionary Builder
echo ========================================
echo.
echo 正在更新所有詞表...
echo.

python tools/build_all_dicts.py

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo [成功] 所有詞表已更新！
    echo ========================================
    echo.
    echo 生成的檔案：
    echo   1. pouseng_pinging/borhlang_pouleng.dict.yaml
    echo   2. bannuaci/borhlang_bannuaci_han.dict.yaml
    echo   3. bannuaci/borhlang_bannuaci.dict.yaml
    echo.
    echo 接下來：
    echo   - 執行 deploy_to_rime.bat 部署到 Rime
    echo   - 或檢查 bannuaci/conversion_log.txt 查看轉換記錄
    echo.
) else (
    echo.
    echo ========================================
    echo [失敗] 詞表更新失敗
    echo ========================================
    echo.
    echo 請檢查錯誤訊息
    echo.
)

pause
