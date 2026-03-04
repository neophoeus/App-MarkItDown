import os
import gradio as gr
from dotenv import load_dotenv
from converter import convert_file, ai_post_process

# Load environment variables from .env file
load_dotenv()

def process_file(file_obj, url_input, enable_gemini, api_key_input):
    if file_obj:
        file_path = file_obj
    elif url_input and url_input.strip():
        file_path = url_input.strip()
    else:
        gr.Warning("請先上傳檔案或輸入 URL (Please upload a file or enter a URL first.)")
        return "Please upload a file or enter a URL first.", None
        
    # Determine API key to use
    api_key = api_key_input.strip() if api_key_input and api_key_input.strip() else os.environ.get("GEMINI_API_KEY")
    
    if enable_gemini and not api_key:
        gr.Warning("請輸入 Gemini API Key！(Gemini API Key is required.)")
        return "Error: Gemini API Key is required when 'Enable Image/PPTX Description' is checked.\n\nPlease provide it in the textbox or set GEMINI_API_KEY in the .env file.", None
        
    success, result_content = convert_file(file_path, enable_gemini, api_key)
    
    if success:
        gr.Info("轉換成功！(Conversion successful!)")
        
        # Create an output directory in the project folder
        project_dir = os.path.dirname(os.path.abspath(__file__))
        output_dir = os.path.join(project_dir, "output")
        os.makedirs(output_dir, exist_ok=True)
        
        try:
            if file_obj:
                original_filename = os.path.basename(file_path)
                base_name, _ = os.path.splitext(original_filename)
            else:
                from urllib.parse import urlparse
                parsed = urlparse(file_path)
                base_name = parsed.path.split("/")[-1] or parsed.netloc
                base_name = base_name.replace(".", "_") if base_name else "url_output"
        except Exception:
            base_name = "output"
            
        output_filename = f"{base_name}.md"
        output_path = os.path.join(output_dir, output_filename)
        
        # Avoid overwriting existing files by appending a number
        counter = 1
        while os.path.exists(output_path):
            output_filename = f"{base_name}_{counter}.md"
            output_path = os.path.join(output_dir, output_filename)
            counter += 1
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(result_content)
            
        return result_content, output_path
    else:
        gr.Warning("轉換失敗，請查看原始碼區塊詳細資訊。(Conversion failed.)")
        return result_content, None

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
                        lines=1
                    )
            
            with gr.Accordion("Advanced Settings (Gemini AI)", open=True):
                enable_gemini = gr.Checkbox(
                    label="Enable Image/PPTX Description (requires API Key)", 
                    value=False,
                    info="Use Gemini to interpret images and slides into text."
                )
                api_key_input = gr.Textbox(
                    label="Gemini API Key", 
                    placeholder="Enter your API Key here (or set GEMINI_API_KEY in .env)", 
                    type="password",
                    value=os.environ.get("GEMINI_API_KEY", "")
                )
                
            convert_btn = gr.Button("Convert to Markdown", variant="primary")
            
        with gr.Column(scale=2):
            with gr.Tabs():
                with gr.Tab("Preview"):
                    output_markdown = gr.Markdown("Converted content will appear here...")
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
                        lines=2
                    )
                    btn_custom = gr.Button("🚀 執行自訂指令", variant="primary", size="sm")
            # === 結束 ===
            
            download_btn = gr.DownloadButton(label="Download Generated Markdown", visible=False)

    # Update both preview and source code views
    current_markdown = gr.State("")

    def handle_post_process(markdown_content, action, api_key_input, custom_prompt=""):
        api_key = api_key_input.strip() if api_key_input and api_key_input.strip() else os.environ.get("GEMINI_API_KEY")
        if not api_key:
            gr.Warning("AI 後製需要 Gemini API Key！")
            return markdown_content, markdown_content, markdown_content
        if not markdown_content:
            gr.Warning("請先轉換文件後再使用 AI 後製功能。")
            return markdown_content, markdown_content, markdown_content
        
        gr.Info("AI 處理中，請稍候...")
        success, result = ai_post_process(markdown_content, action, api_key, custom_prompt)
        
        if success:
            gr.Info("AI 後製完成！")
            return result, result, result  # 更新 preview, source, state
        else:
            gr.Warning("AI 後製失敗。")
            return markdown_content, markdown_content, markdown_content

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
            outputs=[output_markdown, output_code, current_markdown]
        )

    btn_custom.click(
        fn=lambda md, key, prompt: handle_post_process(md, "custom", key, prompt),
        inputs=[current_markdown, api_key_input, custom_prompt_input],
        outputs=[output_markdown, output_code, current_markdown]
    )

    def handle_conversion(file, url, use_llm, key):
        content, file_path = process_file(file, url, use_llm, key)
        if file_path:
            return content, content, gr.DownloadButton(value=file_path, visible=True), content
        else:
            return content, content, gr.DownloadButton(value=None, visible=False), content

    convert_btn.click(
        fn=handle_conversion,
        inputs=[file_input, url_input, enable_gemini, api_key_input],
        outputs=[output_markdown, output_code, download_btn, current_markdown]
    )

if __name__ == "__main__":
    print("Starting Gradio server...")
    print("If it doesn't open automatically, navigate to http://localhost:7860 in your browser.")
    
    # Launch the app
    demo.launch(inbrowser=True, server_name="127.0.0.1", server_port=7860, favicon_path="favicon.ico")
