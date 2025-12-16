# 木蘭輸入法 Borhlang IME

基於 [Rime](https://rime.im/) 的莆仙語輸入法專案。

**Borhlang** 是「木蘭」的莆仙話拼音，木蘭溪是莆田市最重要的河流。

## 專案簡介

本專案的目標是為莆仙語使用者提供完整、準確的輸入法，支援兩套羅馬字系統：

1. **興化平話字（Báⁿ-uā-ci̍）**：19世紀末傳教士創造的羅馬字書寫系統，曾是記錄莆田話的重要文字，有完整的聖經譯本和報刊文獻。
2. **莆仙話拼音（Pouseng Ping'ing）**：現代莆仙語圈子最常用的羅馬字方案，能準確標記多種莆仙語方言。

## 目前進度

### ✅ 已完成

#### 興化平話字（Báⁿ-uā-ci̍）
基於莆田城區口音（19世紀末標準）
- 純平話字輸出模式（平話字在上，漢字在下）
- 漢字輸出模式（漢字在上，平話字註釋）
- 基礎詞庫（23,000+ 詞條，自動從莆仙話拼音詞庫、聖經中提取和轉換）
- 支援簡拼、模糊音、聲調省略等功能

#### 莆仙話拼音（Pouseng Ping'ing）
基於莆田城區口音（現代標準）
- ✅ **莆田話（Pouleng）** - 已完成
  - 完整詞庫（24,000+ 詞條）
  - 類普拼式模糊音（方便初學者）
  - 簡碼輸入（提高輸入速度）
  - 支援變調和聲母類化檢索

### 🚧 計劃中
- **莆仙話拼音（Pouseng Ping'ing）** - 其他方言點
  - 江口（Gangngao）
  - 南日（Nangnih）
  - 東海（Dangngai）
  - 仙遊（Sengniu）
  - 游洋（Iuyang）
  - 楓亭（Horngneng）

## 專案特色

### 興化平話字（Báⁿ-uā-ci̍）

- **雙模式輸出**：可選擇輸出純平話字或漢字
- **完整的聲調標記**：使用變音符號精確標記七個聲調
- **便捷輸入**：特殊字元可用 ASCII 字母組合輸入
  - `a̤` (a 加下點)：輸入 `aa` 或 `ar`
  - `e̤` (e 加下點)：輸入 `ee` 或 `er` 或 `oe`
  - `o̤` (o 加下點)：輸入 `oo` 或 `or`
  - `ṳ` (u 加下點)：輸入 `y` 或 `uu` 或 `ur`
  - `ⁿ` (上標 n)：輸入 `nn`
- **簡拼支援**：可用首字母快速輸入（如 `b` → `ba`, `báⁿ`, `ba̍h` 等）
- **模糊音支援**：自動處理常見的音韻混淆（如 `ang`/`an` 等）
- **漢語拼音反查**：用 `` ` `` 開啟反查功能

### 莆仙話拼音（Pouseng Ping'ing）

- **無聲調輸入**：輸入時不需要標註聲調，候選詞自動顯示聲調數字
- **類普拼式支援**：不熟悉莆仙話拼音的使用者可用類似漢語拼音的寫法
  - `ao` → `au`（豆 dao → dau）
  - `ian` → `ieng`（咸 gian → gieng）
  - `iao` → `ieo`（藥 iao → ieo）
  - 以及更多...（詳見方案說明）
- **簡碼輸入**：複雜韻母可用簡化寫法（如 `jo` → `zyor` 紙）
- **顎化音支援**：z/c/s 可寫成 j/q/x（如 `ji` → `zi` 字）
- **鼻音韻尾簡化**：可省略 -ng 的 g（如 `an` → `ang` 安）
- **入聲韻尾模糊**：-h 和 -k 可互換或省略
- **簡拼支援**：首字母縮寫快速輸入（如 `pt` → 莆田）
- **漢語拼音反查**：用 `` ` `` 開啟反查功能

## 安裝說明

### 前置需求

安裝 Rime 輸入法引擎：
- **Windows**：[小狼毫](https://rime.im/download/)
- **macOS**：[鼠鬚管](https://rime.im/download/)
- **Linux**：[中州韻](https://rime.im/download/)
- **Android**：[同文輸入法](https://github.com/osfans/trime) 或 [Fcitx5-Android](https://github.com/fcitx5-android/fcitx5-android)
- **iOS**：[Hamster](https://github.com/imfuxiao/Hamster)

### 安裝步驟

1. **下載本專案**
   ```bash
   git clone https://github.com/yourusername/borhlang-ime.git
   ```

2. **複製檔案到 Rime 使用者資料夾**

   找到您的 Rime 使用者資料夾：
   - Windows (小狼毫)：`%APPDATA%\Rime`
   - macOS (鼠鬚管)：`~/Library/Rime`
   - Linux (中州韻)：`~/.config/ibus/rime` 或 `~/.local/share/fcitx5/rime`
   - Android (同文)：`/sdcard/rime`

   複製以下檔案到使用者資料夾：
   ```bash
   # 興化平話字方案
   cp bannuaci/borhlang_bannuaci.dict.yaml [Rime使用者資料夾]/
   cp bannuaci/borhlang_bannuaci.schema.yaml [Rime使用者資料夾]/
   cp bannuaci/borhlang_bannuaci_han.dict.yaml [Rime使用者資料夾]/
   cp bannuaci/borhlang_bannuaci_han.schema.yaml [Rime使用者資料夾]/
   cp bannuaci/rime.lua [Rime使用者資料夾]/
   cp bannuaci/lua/bannuaci_filter.lua [Rime使用者資料夾]/lua

   # 莆仙話拼音方案（莆田話）
   cp pouseng_pinging/borhlang_pouleng.schema.yaml [Rime使用者資料夾]/
   cp pouseng_pinging/borhlang_pouleng.dict.yaml [Rime使用者資料夾]/
   ```

3. **部署 Rime**
   - Windows/macOS/Linux：在輸入法圖示上點擊「重新部署」
   - Android：在同文輸入法設定中點擊「部署」

4. **啟用輸入方案**
   - 按 `F4` 或 `Ctrl+\``（反引號）開啟方案選單
   - 勾選想要使用的方案：
     - 「興化平話字」或「興化平話字（漢字）」
     - 「莆仙話拼音・莆田」

## 使用方法

### 興化平話字基本輸入

直接輸入興化平話字的拼音（可省略聲調）：

```
輸入：bannuaci          → 候選：báⁿ-uā-ci̍ 平話字
輸入：pocheng          → 候選：pó-chéng 莆田
輸入：hinghuanang     → 候選：hing-hua̍-náng 興化儂
```

### 莆仙話拼音基本輸入

直接輸入莆仙話拼音（不需要聲調）：

```
輸入：pouceng          → 候選：莆田 pou²ceng²
輸入：hinghua         → 候選：興化 hing¹hua⁴
輸入：siabuei         → 候選：食飯 sia²buei⁵
```

類普拼式輸入（方便初學者）：

```
輸入：gian            → 候選：咸 gieng²（使用 ian 代替 ieng）
輸入：ji              → 候選：字 zi⁵（使用 ji 代替 zi）
```

### 特殊字元輸入

輸入帶特殊符號的字母時，可使用以下便捷方式：

| 正確寫法 | 便捷輸入 | 範例 |
|---------|---------|------|
| a̤ | `aa` 或 `ar` | `baa` → `ba̤` |
| e̤ | `ee` 或 `er` 或 `oe` | `see` → `se̤` |
| o̤ | `oo` 或 `or` | `doo` → `do̤` |
| ṳ | `y` 或 `uu` 或 `ur` | `syng` → `sṳng` |
| ⁿ | `nn` | `bann` → `baⁿ` |

### 聲調輸入

興化平話字有七個聲調，使用變音符號標記。輸入時**可以省略聲調**，輸入法會自動匹配所有聲調的候選詞。

**如需指定特定聲調**，可使用以下按鍵（數字鍵已被選詞功能佔用，故使用字母鍵）：

| 調類 | 標記 | 範例 | 輸入方式 | 指定聲調輸入 |
|-----|------|------|---------|-------------|
| 第一調（陰平） | 無標記 | `a` | `a` | `a` (待補) |
| 第二調（陽平） | ´ (acute) | `á` | `a`（省略聲調）| `aq` |
| 第三調（上聲） | ˆ (circumflex) | `â` | `a`（省略聲調）| `av` |
| 第四調（陰去） | ̍ (vertical line) | `a̍` | `a`（省略聲調）| `aj` |
| 第五調（陽去） | ¯ (macron) | `ā` | `a`（省略聲調）| `af` |
| 第六調（陰入） | 無標記或 ¯ | `ah`, `āh` | `ah` | `ah6` 或 `ah` |
| 第七調（陽入） | ̍ | `a̍h` | `ah`（省略聲調）| `ahj` |

**聲調按鍵說明**：
- `q` = 第2調（陽平 ´）
- `v` = 第3調（上聲 ˆ）
- `j` = 第4調/第7調（陰去/陽入 ̍）
- `f` = 第5調（陽去 ¯）

**範例**：
- 輸入 `baq` → 只顯示第2調的候選詞：`bá`（爬）
- 輸入 `bav` → 只顯示第3調的候選詞：`bâ`（把）
- 輸入 `ba` → 顯示所有聲調的候選詞：`ba`、`bá`、`bâ`、`ba̍`、`bā` 等

### 簡拼輸入

支援首字母縮寫：

```
輸入：b    → 候選：ba, báⁿ, ba̍h, ...
輸入：pt   → 候選：Pó-tiáⁿ 莆田
輸入：buc  → 候選：Báⁿ-uā-ci̍ 平話字
```

### 漢語拼音反查

用反引號 `` ` `` 開啟漢語拼音反查功能：

```
輸入：`putian'   → 顯示「莆田」的興化平話字讀音
```

### 切換方案

按 `F4` 或 `Ctrl+\``（反引號）可在不同輸入方案間切換：

- **興化平話字**（borhlang_bannuaci）：輸出純平話字
- **興化平話字（漢字）**（borhlang_bannuaci_han）：輸出漢字，平話字註釋
- **莆仙話拼音・莆田**（borhlang_pouleng）：輸出漢字，莆仙話拼音註釋

## 詞庫資訊

### 興化平話字詞庫

- **來源**：自動從莆仙話拼音詞庫轉換，並整合多個來源
- **單字資料**：基於維基詞典的莆仙語讀音資料（11,000+ 漢字）
- **詞條數量**：27,000+ 詞條（漢字輸出模式）、20,000+ 詞條（純羅馬字模式）
- **音韻基礎**：莆田城區口音（19世紀末標準）
- **詞庫來源**：
  - 基礎詞庫（人工整理，~23,000 詞條）
  - 維基詞典短語（自動提取，~4,000 詞條）
  - 興化聖經（自動提取，~920 詞條，權重較低）
- **轉換說明**：
  - 使用音韻對應規則自動轉換莆仙話拼音為興化平話字
  - 考慮聲母類化現象，智慧反推原始讀音
  - 對照維基詞典資料驗證轉換結果
  - 部分詞條可能需要人工校對（詳見 `bannuaci/conversion_log_v3.txt`）

### 莆仙話拼音詞庫

- **來源**：[hinghwa-ime](https://github.com/e-dialect/hinghwa-ime) 莆仙話拼音詞庫，整合多個來源
- **編纂者**：芽油（字詞錄入整理）、子善（程式技術）
- **詞條數量**：27,000+ 詞條（合併版）
- **音韻基礎**：莆田城區口音（現代標準）
- **詞庫來源**：
  - 基礎詞庫（人工整理）
  - 維基詞典短語（自動提取）
  - 興化聖經（自動提取，權重上限 300）
- **參考資料**：
  - 《莆田縣誌》同音字表
  - 《莆田市誌》同音字表
  - 《莆仙方言簡明詞彙》
  - 《莆田市誌》分類詞表
  - 維基詞典莆仙語讀音資料
  - 興化平話字聖經（1912 年版）

## 專案結構

```
borhlang-ime/
├── README.md                 # 本檔案
├── LICENSE                   # MPL 2.0 授權
├── build_dicts.bat           # 一鍵更新詞表（Windows）
├── deploy_to_rime.bat        # 部署到 Rime（Windows）
├── bannuaci/                 # 興化平話字方案
│   ├── borhlang_bannuaci.schema.yaml       # 純平話字輸出（使用 Lua）
│   ├── borhlang_bannuaci_han.schema.yaml   # 漢字輸出
│   ├── borhlang_bannuaci.dict.yaml         # 詞庫（Lua 格式）
│   ├── lua/bannuaci_filter.lua             # Lua 智慧過濾器
│   ├── rime.lua                            # Lua 入口檔案
│   ├── conversion_log.txt                  # 詞庫轉換日誌
│   └── README.md                           # 興化平話字說明文件
├── pouseng_pinging/          # 莆仙話拼音方案
│   ├── borhlang_pouleng.schema.yaml        # 莆田話方案
│   ├── borhlang_pouleng.dict.yaml          # 莆田話詞庫（25,000+ 詞條，合併版）
│   └── README.md                           # 莆仙話拼音說明文件
├── data/                     # 原始資料與中間檔案
│   ├── cpx-pron-data.lua                   # 維基詞典字音資料
│   ├── psp_to_buc.py                       # 拼音轉換核心模組
│   ├── romanization_converter.py           # 羅馬字系統轉換器
│   ├── puxian_initials.json                # 聲母表
│   ├── puxian_rhymes.json                  # 韻母表
│   ├── bible_data.json                     # 興化平話字聖經（結構化 JSON）
│   ├── vocab_from_wikt.yaml                # 從維基詞典提取的詞彙
│   └── vocab_from_bible.yaml               # 從聖經提取的詞彙
├── docs/                     # 文檔與數據源
│   └── puxian_phrases_from_wikt.txt        # 維基詞典短語資料
├── tools/                    # 開發工具
│   ├── build_all_dicts.py                  # 一鍵更新詞表（主腳本）
│   ├── extract_vocab_from_wikt.py          # 從維基詞典提取詞彙
│   ├── extract_vocab_from_bible.py         # 從聖經提取詞彙
│   ├── convert_dict_v3.py                  # 莆拼→平話字轉換
│   └── generate_pure_bannuaci_dict.py      # 生成 Lua 格式詞庫
└── hinghwa-ime/              # 參考資料（原 hinghwa-ime 專案）
```

## 貢獻指南

歡迎對本專案做出貢獻！您可以：

- 🐛 回報問題：在 [Issues](../../issues) 頁面回報錯誤或提出建議
- 📝 改善詞庫：提供更準確的讀音或補充缺失的詞彙
- 🌍 擴充方言：協助開發其他莆仙語方言點的輸入方案
- 📖 完善文件：改善說明文件、增加使用範例

### 詞庫校對與更新

本專案詞庫來自多個來源，自動合併：

1. **基礎詞庫** (`pouseng_pinging/borhlang_pouleng.dict.yaml`) - 人工整理
2. **維基詞典** (`docs/puxian_phrases_from_wikt.txt`) - 短語與詞彙（~4,000 詞條）
3. **聖經文本** (`data/bible_data.json`) - 興化聖經結構化資料，取自 [hinghua-singging](https://github.com/tesiniong/hinghua-singging)（~920 詞條）

**更新詞庫流程：**

1. 編輯任一資料源檔案
2. 執行 `build_dicts.bat`（Windows）或 `python tools/build_all_dicts.py`
3. 檢查 `bannuaci/conversion_log.txt` 查看轉換警告
4. 執行 `deploy_to_rime.bat` 部署到 Rime

**人工校對：**

轉換日誌 `bannuaci/conversion_log.txt` 列出了需要人工確認的詞條。如果您發現錯誤，歡迎提交 Pull Request 修正。

## 致謝

本專案參考並使用了以下資源：

- **hinghwa-ime**：原莆仙話拼音輸入法專案，提供了寶貴的詞庫資料
- **維基詞典**：提供莆仙語漢字讀音資料
- **Rime 輸入法框架**：優秀的開源輸入法平台
- 所有為莆仙語保存和推廣做出貢獻的前輩學者和語言愛好者

## 授權

本專案採用 [Mozilla Public License 2.0 (MPL-2.0)](LICENSE) 授權。

---

## 附錄：興化平話字拼寫規則簡表

### 聲母（15個）

| 平話字 | IPA | 範例 |
|-------|-----|------|
| b | /p/ | ba 巴 |
| p | /pʰ/ | pa 怕 |
| m | /m/ | ma 明 |
| d | /t/ | da 打 |
| t | /tʰ/ | ta 他 |
| n | /n/ | na 拿 |
| l | /l/ | la 拉 |
| g | /k/ | ga 家 |
| k | /kʰ/ | ka 客 |
| ng | /ŋ/ | nga 雅 |
| h | /h/ | ha 蝦 |
| c | /ts/ | ca 昨 |
| ch | /tsʰ/ | cha 冊 |
| s | /ɬ/ | sa 沙 |
| (零聲母) | - | a 亞 |

### 聲調（7個）

| 調類 | 調值(今) | 標記方式 | 範例 |
|-----|------|---------|------|
| 陰平 | 533 | 無標記 | a |
| 陽平 | 13 | acute (´) | á |
| 上聲 | 453 | circumflex (ˆ) | â |
| 陰去 | 42 | vertical line below (̍) | a̍ |
| 陽去 | 21 | macron (¯) | ā |
| 陰入 | 1 | 無標記或 | ah |
| 陽入 | 5 | vertical line below | a̍h |

### 特殊符號

- **◌̤** (combining diaeresis below)：用於 a̤, e̤, o̤
- **ṳ** (u with dot below)：特殊元音 (Unicode已預組)
- **ⁿ** (superscript n)：鼻化標記

## 已知問題

### 純興化平話字

- 無法輸入大寫開頭的詞彙
- 分音節輸入不在詞庫的詞彙時，不會自動添加連字號