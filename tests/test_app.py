import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


APP_DIR = Path(__file__).resolve().parents[1]
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

import app_logic


class AppHelpersTests(unittest.TestCase):
    def test_resolve_api_key_prefers_input(self):
        with patch.dict(os.environ, {"GEMINI_API_KEY": "env-key"}, clear=False):
            self.assertEqual(app_logic.resolve_api_key("  typed-key  "), "typed-key")

    def test_resolve_api_key_falls_back_to_env(self):
        with patch.dict(os.environ, {"GEMINI_API_KEY": "  env-key  "}, clear=False):
            self.assertEqual(app_logic.resolve_api_key("   "), "env-key")

    def test_build_output_path_sanitizes_name_and_avoids_overwrite(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_output_dir = Path(temp_dir)
            existing = temp_output_dir / "My_File_Name.md"
            existing.write_text("existing", encoding="utf-8")

            with patch.object(app_logic, "OUTPUT_DIR", temp_output_dir):
                result = app_logic.build_output_path(
                    "https://example.com/My File@Name.pdf", has_uploaded_file=False
                )

            self.assertEqual(result.name, "My_File_Name_1.md")


class ProcessConversionTests(unittest.TestCase):
    def test_process_conversion_requires_api_key_for_gemini(self):
        with patch.dict(os.environ, {}, clear=True):
            result = app_logic.process_conversion(
                file_obj="demo.pdf",
                url_input="",
                enable_gemini=True,
                api_key_input="",
                convert_file_fn=lambda *_args: (True, "unused"),
            )

        self.assertFalse(result.success)
        self.assertIn("Gemini API Key is required", result.content)
        self.assertIsNone(result.output_path)
        self.assertEqual(result.notification_level, "warning")

    def test_process_conversion_requires_source(self):
        result = app_logic.process_conversion(
            file_obj=None,
            url_input="   ",
            enable_gemini=False,
            api_key_input="",
            convert_file_fn=lambda *_args: (True, "unused"),
        )

        self.assertFalse(result.success)
        self.assertEqual(result.content, app_logic.MISSING_INPUT_MESSAGE)
        self.assertEqual(result.notification_level, "warning")

    def test_process_conversion_writes_output_file(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_output_dir = Path(temp_dir)

            convert_file_mock = patch(
                "app_logic.build_output_path",
                return_value=temp_output_dir / "report.final.md",
            )
            with convert_file_mock as build_output_path_mock:
                result = app_logic.process_conversion(
                    file_obj="C:/docs/report.final.pdf",
                    url_input="",
                    enable_gemini=False,
                    api_key_input="",
                    convert_file_fn=lambda path, use_llm, api_key: (True, "# hello"),
                )

            build_output_path_mock.assert_called_once_with(
                "C:/docs/report.final.pdf", has_uploaded_file=True
            )
            self.assertTrue(result.success)
            self.assertEqual(result.content, "# hello")
            self.assertIsNotNone(result.output_path)
            written_path = Path(result.output_path)
            self.assertTrue(written_path.exists())
            self.assertEqual(written_path.read_text(encoding="utf-8"), "# hello")


class ProcessPostProcessingTests(unittest.TestCase):
    def test_process_post_processing_requires_api_key(self):
        with patch.dict(os.environ, {}, clear=True):
            result = app_logic.process_post_processing(
                markdown_content="# body",
                action="summarize",
                api_key_input="",
                ai_post_process_fn=lambda *_args: (True, "unused"),
            )

        self.assertFalse(result.success)
        self.assertEqual(result.content, "# body")
        self.assertEqual(result.notification_level, "warning")

    def test_process_post_processing_requires_markdown(self):
        result = app_logic.process_post_processing(
            markdown_content="",
            action="summarize",
            api_key_input="key",
            ai_post_process_fn=lambda *_args: (True, "unused"),
        )

        self.assertFalse(result.success)
        self.assertEqual(result.content, "")
        self.assertEqual(result.notification_level, "warning")

    def test_process_post_processing_returns_processed_content(self):
        result = app_logic.process_post_processing(
            markdown_content="# body",
            action="summarize",
            api_key_input=" key ",
            ai_post_process_fn=lambda markdown, action, api_key, custom_prompt: (
                True,
                f"processed:{markdown}:{action}:{api_key}:{custom_prompt}",
            ),
            custom_prompt="note",
        )

        self.assertTrue(result.success)
        self.assertEqual(result.content, "processed:# body:summarize:key:note")
        self.assertEqual(result.notification_level, "info")


if __name__ == "__main__":
    unittest.main()
