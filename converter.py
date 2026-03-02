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
