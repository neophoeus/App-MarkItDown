# App-MarkItDown 待辦與追蹤清單

## 🔍 上游套件追蹤 (Upstream Tracking)

本專案的核心轉換引擎依賴於微軟開源的 `markitdown` 專案。
為確保本工具的轉換能力與相容性保持在最佳狀態，請定期追蹤該專案的更新動態。

- **官方 Repository**: [microsoft/markitdown](https://github.com/microsoft/markitdown)

### 追蹤重點

1. **新支援的檔案格式**: 關注官方是否新增了對其他副檔名的支援 (例如：EPUB, Notion匯出檔 等)。
2. **LLM 參數變化**: 關注 `MarkItDown(llm_client, llm_model)` 的介面是否有變更或支援更進階的 prompt injection 方式。
3. **效能優化**: 若官方發布了核心效能升級，應同步更新本專案 `requirements.txt` 中的 `markitdown[all]` 版本。

---

## 💡 未來功能構想 (Future Ideas)

*(這區塊可作為日後新功能開發的靈感庫)*

- 批次大量轉換功能 (Batch processing zip downloads)
- 針對翻譯功能加入語言選擇下拉選單
- 支援文件對話功能 (Chat with your document)
