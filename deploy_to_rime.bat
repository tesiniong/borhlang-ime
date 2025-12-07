@echo off
chcp 65001 >nul
echo ========================================
echo 木蘭輸入法 - 部署到 Rime
echo Borhlang IME - Deploy to Rime
echo ========================================
echo.

REM 設定來源和目標路徑
set SOURCE_DIR=%~dp0bannuaci
set RIME_DIR=%APPDATA%\Rime

echo 來源目錄: %SOURCE_DIR%
echo 目標目錄: %RIME_DIR%
echo.

REM 檢查來源目錄是否存在
if not exist "%SOURCE_DIR%" (
    echo [錯誤] 找不到來源目錄: %SOURCE_DIR%
    pause
    exit /b 1
)

REM 檢查目標目錄是否存在
if not exist "%RIME_DIR%" (
    echo [錯誤] 找不到 Rime 目錄: %RIME_DIR%
    echo 請確認已安裝小狼毫輸入法
    pause
    exit /b 1
)

echo [步驟 1/3] 刪除舊檔案...
echo.

REM 刪除可能存在的舊檔案
if exist "%RIME_DIR%\borhlang_bannuaci_pure.dict.yaml" (
    del "%RIME_DIR%\borhlang_bannuaci_pure.dict.yaml"
    echo   已刪除: borhlang_bannuaci_pure.dict.yaml
)

echo [步驟 2/3] 複製新檔案...
echo.

REM 複製 Schema 檔案
copy /Y "%SOURCE_DIR%\borhlang_bannuaci.schema.yaml" "%RIME_DIR%\" >nul
if %errorlevel% equ 0 (
    echo   [✓] borhlang_bannuaci.schema.yaml
) else (
    echo   [✗] borhlang_bannuaci.schema.yaml - 複製失敗
)

copy /Y "%SOURCE_DIR%\borhlang_bannuaci_han.schema.yaml" "%RIME_DIR%\" >nul
if %errorlevel% equ 0 (
    echo   [✓] borhlang_bannuaci_han.schema.yaml
) else (
    echo   [✗] borhlang_bannuaci_han.schema.yaml - 複製失敗
)

REM 複製詞庫檔案
copy /Y "%SOURCE_DIR%\borhlang_bannuaci.dict.yaml" "%RIME_DIR%\" >nul
if %errorlevel% equ 0 (
    echo   [✓] borhlang_bannuaci.dict.yaml
) else (
    echo   [✗] borhlang_bannuaci.dict.yaml - 複製失敗
)

copy /Y "%SOURCE_DIR%\borhlang_bannuaci_han.dict.yaml" "%RIME_DIR%\" >nul
if %errorlevel% equ 0 (
    echo   [✓] borhlang_bannuaci_han.dict.yaml
) else (
    echo   [✗] borhlang_bannuaci_han.dict.yaml - 複製失敗
)

REM 創建 lua 子目錄（如果不存在）
if not exist "%RIME_DIR%\lua" mkdir "%RIME_DIR%\lua"

REM 複製 Lua 檔案
copy /Y "%SOURCE_DIR%\lua\bannuaci_filter.lua" "%RIME_DIR%\lua\" >nul
if %errorlevel% equ 0 (
    echo   [✓] lua\bannuaci_filter.lua
) else (
    echo   [✗] lua\bannuaci_filter.lua - 複製失敗
)

copy /Y "%SOURCE_DIR%\rime.lua" "%RIME_DIR%\" >nul
if %errorlevel% equ 0 (
    echo   [✓] rime.lua
) else (
    echo   [✗] rime.lua - 複製失敗
)

echo.
echo [步驟 3/3] 部署完成！
echo.
echo ========================================
echo 接下來請執行以下操作：
echo.
echo 1. 在 Rime 輸入法圖示上點擊右鍵
echo 2. 選擇「重新部署」
echo 3. 等待部署完成（約 10-30 秒）
echo 4. 按 F4 或 Ctrl+` 選擇輸入方案
echo 5. 選擇「興化平話字」開始使用
echo ========================================
echo.
pause
