import os
from typing import Optional, Tuple
from markitdown import MarkItDown
from openai import OpenAI
import traceback

def convert_file(file_path: str, use_llm: bool = False, api_key: Optional[str] = None) -> Tuple[bool, str]:
    """
    Converts a file to Markdown using MarkItDown.
    
    Args:
        file_path: The path to the file to convert.
        use_llm: Whether to use an LLM for image descriptions.
        api_key: The API key for Gemini (required if use_llm is True).
        
    Returns:
        A tuple of (success_boolean, output_text_or_error_message)
    """
    try:
        if use_llm and api_key:
            # Gemini provides an OpenAI-compatible endpoint
            client = OpenAI(
                api_key=api_key,
                base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
            )
            # Using Gemini 3 Flash preview for multimodal tasks
            md = MarkItDown(llm_client=client, llm_model="gemini-3.0-flash-preview")
        else:
            md = MarkItDown()
            
        result = md.convert(file_path)
        return True, result.text_content
        
    except Exception as e:
        error_msg = f"Conversion failed: {str(e)}\n\nDetails:\n{traceback.format_exc()}"
        print(error_msg)
        return False, error_msg

def ai_post_process(markdown_content: str, action: str, api_key: str, custom_prompt: str = "") -> Tuple[bool, str]:
    """
    使用 Gemini AI 對已轉換的 Markdown 進行後製處理。
    
    Args:
        markdown_content: 要處理的 Markdown 文字。
        action: 處理類型 ("summarize", "translate_zh", "translate_en", "polish", "rebuild_tables", "custom")。
        api_key: Gemini API Key。
        custom_prompt: 自訂指令 (僅 action="custom" 時使用)。
    
    Returns:
        A tuple of (success_boolean, processed_text_or_error_message)
    """
    PROMPTS = {
        "summarize": "請為以下 Markdown 文件產生一份簡潔的摘要（TL;DR），以繁體中文撰寫，放在文件最前面，用 ## 摘要 作為標題。保留原文不變，只在頂部加上摘要區塊。",
        "translate_zh": "請將以下 Markdown 文件翻譯為繁體中文。保留所有 Markdown 格式、程式碼區塊和連結不變。",
        "translate_en": "Please translate the following Markdown document to English. Preserve all Markdown formatting, code blocks, and links.",
        "polish": "請潤飾以下 Markdown 文件：修正格式問題、補齊遺漏的標題層級、清理多餘的空行或雜訊、改善可讀性。輸出完整的修改後 Markdown。",
        "rebuild_tables": "請檢查以下 Markdown 文件中的表格。如果表格格式凌亂或不完整，請重新結構化為正確的 Markdown 表格語法。其餘內容保持不變。",
    }
    
    if action == "custom":
        system_prompt = custom_prompt
    else:
        system_prompt = PROMPTS.get(action, "")
    
    if not system_prompt:
        return False, "Unknown action or empty custom prompt."
    
    try:
        client = OpenAI(
            api_key=api_key,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
        )
        
        response = client.chat.completions.create(
            model="gemini-2.5-flash",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": markdown_content}
            ],
            temperature=0.3
        )
        
        return True, response.choices[0].message.content
        
    except Exception as e:
        error_msg = f"AI processing failed: {str(e)}\n\n{traceback.format_exc()}"
        print(error_msg)
        return False, error_msg
