import os
import gradio as gr
from dotenv import load_dotenv
from converter import convert_file

# Load environment variables from .env file
load_dotenv()

def process_file(file_obj, enable_gemini, api_key_input):
    if not file_obj:
        gr.Warning("請先上傳檔案 (Please upload a file first.)")
        return "Please upload a file first.", None
        
    # Determine API key to use
    api_key = api_key_input.strip() if api_key_input and api_key_input.strip() else os.environ.get("GEMINI_API_KEY")
    
    if enable_gemini and not api_key:
        gr.Warning("請輸入 Gemini API Key！(Gemini API Key is required.)")
        return "Error: Gemini API Key is required when 'Enable Image/PPTX Description' is checked.\n\nPlease provide it in the textbox or set GEMINI_API_KEY in the .env file.", None
        
    # file_obj in Gradio could be a string (filepath) or a File object depending on type="filepath"
    # When using `type="filepath"`, `file_obj` is directly the string path.
    file_path = file_obj
    
    success, result_content = convert_file(file_path, enable_gemini, api_key)
    
    if success:
        gr.Info("轉換成功！(Conversion successful!)")
        
        # Create an output directory in the project folder
        project_dir = os.path.dirname(os.path.abspath(__file__))
        output_dir = os.path.join(project_dir, "output")
        os.makedirs(output_dir, exist_ok=True)
        
        try:
            original_filename = os.path.basename(file_path)
            base_name, _ = os.path.splitext(original_filename)
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
            file_input = gr.File(label="Upload Document", type="filepath")
            
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
                    
            download_btn = gr.DownloadButton(label="Download Generated Markdown", visible=False)

    # Update both preview and source code views
    def handle_conversion(file, use_llm, key):
        content, file_path = process_file(file, use_llm, key)
        if file_path:
            return content, content, gr.DownloadButton(value=file_path, visible=True)
        else:
            return content, content, gr.DownloadButton(value=None, visible=False)

    convert_btn.click(
        fn=handle_conversion,
        inputs=[file_input, enable_gemini, api_key_input],
        outputs=[output_markdown, output_code, download_btn]
    )

if __name__ == "__main__":
    print("Starting Gradio server...")
    print("If it doesn't open automatically, navigate to http://localhost:7860 in your browser.")
    
    # Launch the app
    demo.launch(inbrowser=True, server_name="127.0.0.1", server_port=7860)
