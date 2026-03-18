import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch


APP_DIR = Path(__file__).resolve().parents[1]
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from support import install_test_stubs

install_test_stubs()

import converter


class ConvertFileTests(unittest.TestCase):
    def test_convert_file_without_llm_uses_plain_markitdown(self):
        fake_result = SimpleNamespace(text_content="# converted")
        fake_markitdown = Mock()
        fake_markitdown.convert.return_value = fake_result

        with patch.object(
            converter, "MarkItDown", return_value=fake_markitdown
        ) as markitdown_cls:
            success, content = converter.convert_file("sample.pdf")

        self.assertTrue(success)
        self.assertEqual(content, "# converted")
        markitdown_cls.assert_called_once_with()
        fake_markitdown.convert.assert_called_once_with("sample.pdf")

    def test_convert_file_with_llm_passes_current_model(self):
        fake_result = SimpleNamespace(text_content="# converted")
        fake_markitdown = Mock()
        fake_markitdown.convert.return_value = fake_result

        with patch.object(
            converter, "_create_gemini_client", return_value="client"
        ) as client_factory, patch.object(
            converter, "MarkItDown", return_value=fake_markitdown
        ) as markitdown_cls:
            success, content = converter.convert_file(
                "sample.pdf", use_llm=True, api_key="  api-key  "
            )

        self.assertTrue(success)
        self.assertEqual(content, "# converted")
        client_factory.assert_called_once_with("api-key")
        markitdown_cls.assert_called_once_with(
            llm_client="client", llm_model=converter.MARKITDOWN_LLM_MODEL
        )


class AiPostProcessTests(unittest.TestCase):
    def test_ai_post_process_rejects_unknown_action(self):
        success, content = converter.ai_post_process("body", "missing", "key")

        self.assertFalse(success)
        self.assertEqual(content, "Unknown action or empty custom prompt.")

    def test_ai_post_process_requires_non_empty_custom_prompt(self):
        success, content = converter.ai_post_process("body", "custom", "key", "   ")

        self.assertFalse(success)
        self.assertEqual(content, "Unknown action or empty custom prompt.")

    def test_ai_post_process_uses_current_model(self):
        fake_client = Mock()
        fake_client.chat.completions.create.return_value = SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content="processed"))]
        )

        with patch.object(
            converter, "_create_gemini_client", return_value=fake_client
        ) as client_factory:
            success, content = converter.ai_post_process(
                "body", "translate_en", "  key  "
            )

        self.assertTrue(success)
        self.assertEqual(content, "processed")
        client_factory.assert_called_once_with("key")
        fake_client.chat.completions.create.assert_called_once()
        _, kwargs = fake_client.chat.completions.create.call_args
        self.assertEqual(kwargs["model"], converter.POST_PROCESS_MODEL)
        self.assertEqual(kwargs["messages"][1]["content"], "body")

    def test_ai_post_process_rejects_empty_response_content(self):
        fake_client = Mock()
        fake_client.chat.completions.create.return_value = SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content=""))]
        )

        with patch.object(converter, "_create_gemini_client", return_value=fake_client):
            success, content = converter.ai_post_process("body", "translate_en", "key")

        self.assertFalse(success)
        self.assertEqual(content, "AI processing returned empty content.")


if __name__ == "__main__":
    unittest.main()
