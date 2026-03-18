# App-MarkItDown

[English](#english) | [繁體中文](#繁體中文)

---

<a id="english"></a>

## 📄 App-MarkItDown (English)

Convert virtually any document (PDF, Word, Excel, PowerPoint, Images) into clean, structured Markdown.
Powered by Microsoft's `markitdown` and enhanced with **Google Gemini** for multimodal capabilities (interpreting images and slide contents).

### ✨ Features

- **Universal Support**: Convert PDF, DOCX, XLSX, PPTX, and various image formats to Markdown.
- **URL to Markdown**: Simply paste a URL to automatically fetch and convert web pages into clean Markdown.
- **AI-Enhanced Conversion**: Built-in integration with Google Gemini AI to analyze and extract text from images and presentation slides during conversion.
- **AI Post-Processing Toolset**: After conversion, use Gemini to automatically generate summaries, translate content, polish formatting, or rebuild complex tables with a single click.
- **User-Friendly Web UI**: Easy-to-use Gradio web interface. No CLI commands required.
- **Local Output**: Your files are processed locally and saved cleanly in a dedicated `output` folder.
- **One-Click Startup**: Includes a batch script that automatically sets up the Python virtual environment, installs dependencies, and launches the app.

### 🚀 Getting Started

#### Prerequisites

- Python 3.8+ installed on your Windows system.
- _(Optional but recommended)_ Google Gemini API Key for image/PPTX interpretation. Get one from [Google AI Studio](https://aistudio.google.com/).

#### Installation & Usage

1. Clone this repository or download the source code.
2. Double-click `start.bat`.
3. The script will automatically:
   - Create a Python virtual environment (`.venv`).
   - Install all required dependencies from `requirements.txt`.
   - Launch the Gradio web server.
4. The web interface will open automatically in your default browser (usually at `http://localhost:7860`).

#### API Key Configuration

You can provide your Gemini API Key in two ways:

1. **(Recommended) via `.env` file**: Open the `.env` file (created automatically from `.env.example` on the first run) and paste your key: `GEMINI_API_KEY=your_api_key_here`. It will be loaded automatically on startup.
2. **via Web UI**: Paste your key directly into the "Advanced Settings (Gemini AI)" section on the application webpage.

### 🧱 Project Structure

- `app.py`: Gradio UI and event wiring only.
- `app_logic.py`: UI-independent workflow logic for input validation, output file generation, conversion flow, and AI post-processing flow.
- `converter.py`: MarkItDown conversion and Gemini/OpenAI-compatible API integration.
- `tests/test_app.py`: Unit tests for workflow logic in `app_logic.py`.
- `tests/test_converter.py`: Unit tests for conversion and AI post-processing logic.
- `tests/support.py`: Lightweight stubs that let tests run without requiring Gradio or MarkItDown to be installed.

### 🧪 Running Tests

From the `App-MarkItDown` folder:

```bash
python -m unittest discover -s tests -v
```

The current tests focus on:

- API key fallback behavior
- output filename sanitization and collision handling
- conversion flow validation and output writing
- AI post-processing guard clauses and successful response handling
- Gemini model wiring for conversion and post-processing

---

<a id="繁體中文"></a>

## 📄 App-MarkItDown (繁體中文)

將幾乎所有的文件格式（PDF、Word、Excel、PowerPoint、圖片）轉換為乾淨、結構化的 Markdown 語法。
底層採用微軟的 `markitdown` 核心，並整合 **Google Gemini AI** 提供強大的多模態視覺解析能力（精準理解圖片與簡報內容）。

### ✨ 特色功能

- **全格式支援**：一鍵轉換 PDF、DOCX、XLSX、PPTX 及多種圖片格式為 Markdown。
- **URL 轉 Markdown**：直接貼上網頁連結，自動抓取網頁內容並轉換為乾淨的 Markdown 格式。
- **AI 視覺增強**：內建 Google Gemini 整合，能自動分析並提取圖片及簡報文件中的隱含文字與描述。
- **AI 後製工坊**：轉換完成後，可一鍵讓 Gemini 為您產生摘要、雙語翻譯、重新排版潤稿、或精準重建複雜表格。
- **優雅的網頁介面**：使用 Gradio 打造的 Web UI，操作直覺，免敲指令即可輕鬆使用。
- **本地端處理**：檔案於本地端轉換，轉出的檔案會整齊歸檔於 `output` 資料夾中。
- **一鍵啟動**：內建 `start.bat` 啟動腳本，完全自動化建置虛擬環境與安裝依賴套件。

### 🚀 開始使用

#### 系統需求

- 已安裝 Python 3.8 或以上版本的 Windows 系統。
- （選用但強烈建議）取得 Google Gemini API Key 以解鎖圖片與簡報的視覺解析功能。可至 [Google AI Studio](https://aistudio.google.com/) 免費申請。

#### 安裝與執行

1. 下載或 Clone 本專案。
2. 雙擊執行 `start.bat`。
3. 腳本將會自動執行以下步驟：
   - 建立 Python 虛擬環境 (`.venv`)。
   - 自動安裝 `requirements.txt` 中所有的必備套件。
   - 啟動 Gradio 網頁伺服器。
4. 網頁介面將會自動在預設的瀏覽器中開啟（預設為 `http://localhost:7860`）。

#### API Key 設定方式

您可以透過以下兩種方式設定 Gemini API Key：

1. **(推薦) 透過 `.env` 檔案設定**：初次執行後會自動產生 `.env` 檔，使用文字編輯器打開它並填入您的金鑰：`GEMINI_API_KEY=你的金鑰`。下次啟動時便會自動載入。
2. **透過網頁介面填寫**：啟動並進入網頁後，直接將金鑰貼到畫面上的「Advanced Settings (Gemini AI)」欄位中即可。

### 🧱 專案結構

- `app.py`：只負責 Gradio 介面與事件綁定。
- `app_logic.py`：與 UI 無關的流程邏輯，包含輸入驗證、輸出檔名處理、轉換流程與 AI 後製流程。
- `converter.py`：MarkItDown 轉換與 Gemini API 整合。
- `tests/test_app.py`：針對 `app_logic.py` 的單元測試。
- `tests/test_converter.py`：針對轉換與 AI 後製邏輯的單元測試。
- `tests/support.py`：提供輕量 stub，讓測試不必依賴 Gradio 或 MarkItDown 的實際安裝。

### 🧪 測試方式

在 `App-MarkItDown` 目錄下執行：

```bash
python -m unittest discover -s tests -v
```

目前測試主要覆蓋：

- API key fallback 行為
- 輸出檔名清洗與重名避讓
- 轉換流程驗證與輸出寫檔
- AI 後製的防呆分支與成功回應
- Gemini 模型設定是否正確接入轉換與後製流程

---

### 🛠️ Built With / 核心技術

- [Gradio](https://gradio.app/)
- [Microsoft MarkItDown](https://github.com/microsoft/markitdown)
- [Google Gemini API](https://ai.google.dev/)
