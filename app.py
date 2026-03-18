import os

import gradio as gr
from dotenv import load_dotenv
from app_logic import process_conversion, process_post_processing
from converter import convert_file, ai_post_process

# Load environment variables from .env file
load_dotenv()


def _notify(result):
    if result.notification_level == "info" and result.notification:
        gr.Info(result.notification)
    elif result.notification_level == "warning" and result.notification:
        gr.Warning(result.notification)


# Define Gradio interface
with gr.Blocks(title="MarkItDown Web UI", theme=gr.themes.Soft()) as demo:
    gr.Markdown(
        """
        # 📄 App-MarkItDown
        Convert virtually any document (PDF, Word, Excel, PowerPoint, Images) into clean Markdown.  
        Powered by Microsoft's `markitdown` and enhanced with **Google Gemini**.
        """
    )

    with gr.Row():
        with gr.Column(scale=1):
            with gr.Tabs() as input_tabs:
                with gr.Tab("📁 Upload File"):
                    file_input = gr.File(label="Upload Document", type="filepath")
                with gr.Tab("🌐 Paste URL"):
                    url_input = gr.Textbox(
                        label="URL",
                        placeholder="https://example.com/document.pdf",
                        lines=1,
                    )

            with gr.Accordion("Advanced Settings (Gemini AI)", open=True):
                enable_gemini = gr.Checkbox(
                    label="Enable Image/PPTX Description (requires API Key)",
                    value=False,
                    info="Use Gemini to interpret images and slides into text.",
                )
                api_key_input = gr.Textbox(
                    label="Gemini API Key",
                    placeholder="Enter your API Key here (or set GEMINI_API_KEY in .env)",
                    type="password",
                    value=os.environ.get("GEMINI_API_KEY", ""),
                )

            convert_btn = gr.Button("Convert to Markdown", variant="primary")

        with gr.Column(scale=2):
            with gr.Tabs():
                with gr.Tab("Preview"):
                    output_markdown = gr.Markdown(
                        "Converted content will appear here..."
                    )
                with gr.Tab("Markdown Source"):
                    output_code = gr.Code(label="Source", language="markdown", lines=20)

            # === 新增：AI 後製工坊 ===
            with gr.Accordion("🤖 AI Post-Processing", open=False):
                with gr.Row():
                    btn_summarize = gr.Button("📝 摘要", size="sm")
                    btn_translate_zh = gr.Button("🇹🇼 翻中文", size="sm")
                    btn_translate_en = gr.Button("🇺🇸 翻英文", size="sm")
                    btn_polish = gr.Button("🧹 潤稿", size="sm")
                    btn_rebuild = gr.Button("📊 表格重建", size="sm")
                with gr.Row():
                    custom_prompt_input = gr.Textbox(
                        label="自訂 AI 指令 (Custom Prompt)",
                        placeholder="例如：請把所有金額換算成台幣...",
                        lines=2,
                    )
                    btn_custom = gr.Button(
                        "🚀 執行自訂指令", variant="primary", size="sm"
                    )
            # === 結束 ===

            download_btn = gr.DownloadButton(
                label="Download Generated Markdown", visible=False
            )

    # Update both preview and source code views
    current_markdown = gr.State("")

    def handle_post_process(markdown_content, action, api_key_input, custom_prompt=""):
        gr.Info("AI 處理中，請稍候...")
        result = process_post_processing(
            markdown_content,
            action,
            api_key_input,
            ai_post_process,
            custom_prompt,
        )
        _notify(result)
        return result.content, result.content, result.content

    # 綁定每個按鈕
    for btn, action in [
        (btn_summarize, "summarize"),
        (btn_translate_zh, "translate_zh"),
        (btn_translate_en, "translate_en"),
        (btn_polish, "polish"),
        (btn_rebuild, "rebuild_tables"),
    ]:
        btn.click(
            fn=lambda md, key, a=action: handle_post_process(md, a, key),
            inputs=[current_markdown, api_key_input],
            outputs=[output_markdown, output_code, current_markdown],
        )

    btn_custom.click(
        fn=lambda md, key, prompt: handle_post_process(md, "custom", key, prompt),
        inputs=[current_markdown, api_key_input, custom_prompt_input],
        outputs=[output_markdown, output_code, current_markdown],
    )

    def handle_conversion(file, url, use_llm, key):
        result = process_conversion(file, url, use_llm, key, convert_file)
        _notify(result)
        if result.output_path:
            return (
                result.content,
                result.content,
                gr.update(value=result.output_path, visible=True),
                result.content,
            )
        else:
            return (
                result.content,
                result.content,
                gr.update(value=None, visible=False),
                result.content,
            )

    convert_btn.click(
        fn=handle_conversion,
        inputs=[file_input, url_input, enable_gemini, api_key_input],
        outputs=[output_markdown, output_code, download_btn, current_markdown],
    )

if __name__ == "__main__":
    print("Starting Gradio server...")
    print(
        "If it doesn't open automatically, navigate to http://localhost:7860 in your browser."
    )

    # Launch the app
    demo.launch(
        inbrowser=True,
        server_name="127.0.0.1",
        server_port=7860,
        favicon_path="favicon.ico",
    )
