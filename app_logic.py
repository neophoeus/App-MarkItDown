import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Optional, Tuple
from urllib.parse import urlparse


PROJECT_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = PROJECT_DIR / "output"
INVALID_FILENAME_CHARS = re.compile(r"[^A-Za-z0-9._-]+")
MISSING_INPUT_MESSAGE = "Please upload a file or enter a URL first."
MISSING_GEMINI_KEY_MESSAGE = (
    "Error: Gemini API Key is required when 'Enable Image/PPTX Description' is checked.\n\n"
    "Please provide it in the textbox or set GEMINI_API_KEY in the .env file."
)


@dataclass(frozen=True)
class ConversionResult:
    success: bool
    content: str
    output_path: Optional[str] = None
    notification: Optional[str] = None
    notification_level: Optional[str] = None


def resolve_api_key(api_key_input: Optional[str]) -> str:
    if api_key_input and api_key_input.strip():
        return api_key_input.strip()
    return os.environ.get("GEMINI_API_KEY", "").strip()


def build_output_path(file_path: str, has_uploaded_file: bool) -> Path:
    OUTPUT_DIR.mkdir(exist_ok=True)

    if has_uploaded_file:
        source_name = Path(file_path).stem
    else:
        parsed = urlparse(file_path)
        source_name = Path(parsed.path).stem or parsed.netloc or "url_output"

    safe_name = INVALID_FILENAME_CHARS.sub("_", source_name).strip("._") or "output"
    safe_name = safe_name[:80]

    candidate = OUTPUT_DIR / f"{safe_name}.md"
    counter = 1
    while candidate.exists():
        candidate = OUTPUT_DIR / f"{safe_name}_{counter}.md"
        counter += 1

    return candidate


def resolve_source_path(
    file_obj: Optional[str], url_input: Optional[str]
) -> Tuple[bool, str]:
    if file_obj:
        return True, file_obj
    if url_input and url_input.strip():
        return True, url_input.strip()
    return False, MISSING_INPUT_MESSAGE


def process_conversion(
    file_obj: Optional[str],
    url_input: Optional[str],
    enable_gemini: bool,
    api_key_input: Optional[str],
    convert_file_fn: Callable[[str, bool, Optional[str]], Tuple[bool, str]],
) -> ConversionResult:
    has_source, source_value = resolve_source_path(file_obj, url_input)
    if not has_source:
        return ConversionResult(
            success=False,
            content=source_value,
            notification="請先上傳檔案或輸入 URL (Please upload a file or enter a URL first.)",
            notification_level="warning",
        )

    api_key = resolve_api_key(api_key_input)
    if enable_gemini and not api_key:
        return ConversionResult(
            success=False,
            content=MISSING_GEMINI_KEY_MESSAGE,
            notification="請輸入 Gemini API Key！(Gemini API Key is required.)",
            notification_level="warning",
        )

    success, result_content = convert_file_fn(source_value, enable_gemini, api_key)
    if not success:
        return ConversionResult(
            success=False,
            content=result_content,
            notification="轉換失敗，請查看原始碼區塊詳細資訊。(Conversion failed.)",
            notification_level="warning",
        )

    output_path = build_output_path(source_value, has_uploaded_file=bool(file_obj))
    with output_path.open("w", encoding="utf-8") as file_handle:
        file_handle.write(result_content)

    return ConversionResult(
        success=True,
        content=result_content,
        output_path=str(output_path),
        notification="轉換成功！(Conversion successful!)",
        notification_level="info",
    )


def process_post_processing(
    markdown_content: str,
    action: str,
    api_key_input: Optional[str],
    ai_post_process_fn: Callable[[str, str, str, str], Tuple[bool, str]],
    custom_prompt: str = "",
) -> ConversionResult:
    api_key = resolve_api_key(api_key_input)
    if not api_key:
        return ConversionResult(
            success=False,
            content=markdown_content,
            notification="AI 後製需要 Gemini API Key！",
            notification_level="warning",
        )

    if not markdown_content:
        return ConversionResult(
            success=False,
            content=markdown_content,
            notification="請先轉換文件後再使用 AI 後製功能。",
            notification_level="warning",
        )

    success, result = ai_post_process_fn(
        markdown_content, action, api_key, custom_prompt
    )
    if success:
        return ConversionResult(
            success=True,
            content=result,
            notification="AI 後製完成！",
            notification_level="info",
        )

    return ConversionResult(
        success=False,
        content=markdown_content,
        notification="AI 後製失敗。",
        notification_level="warning",
    )
