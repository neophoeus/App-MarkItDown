import sys
import types


class DummyContext:
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False


class DummyComponent(DummyContext):
    def click(self, *args, **kwargs):
        return None


def _component_factory(*args, **kwargs):
    return DummyComponent(*args, **kwargs)


def install_test_stubs() -> None:
    if "dotenv" not in sys.modules:
        dotenv_module = types.ModuleType("dotenv")
        dotenv_module.load_dotenv = lambda *args, **kwargs: None
        sys.modules["dotenv"] = dotenv_module

    if "openai" not in sys.modules:
        openai_module = types.ModuleType("openai")

        class OpenAI:
            def __init__(self, *args, **kwargs):
                self.args = args
                self.kwargs = kwargs

        openai_module.OpenAI = OpenAI
        sys.modules["openai"] = openai_module

    if "markitdown" not in sys.modules:
        markitdown_module = types.ModuleType("markitdown")

        class MarkItDown:
            def __init__(self, *args, **kwargs):
                self.args = args
                self.kwargs = kwargs

            def convert(self, *_args, **_kwargs):
                raise NotImplementedError("test stub")

        markitdown_module.MarkItDown = MarkItDown
        sys.modules["markitdown"] = markitdown_module

    if "gradio" not in sys.modules:
        gradio_module = types.ModuleType("gradio")
        gradio_module.Blocks = DummyContext
        gradio_module.Row = DummyContext
        gradio_module.Column = DummyContext
        gradio_module.Tabs = DummyContext
        gradio_module.Tab = DummyContext
        gradio_module.Accordion = DummyContext
        gradio_module.Markdown = _component_factory
        gradio_module.File = _component_factory
        gradio_module.Textbox = _component_factory
        gradio_module.Checkbox = _component_factory
        gradio_module.Button = _component_factory
        gradio_module.Code = _component_factory
        gradio_module.DownloadButton = _component_factory
        gradio_module.State = _component_factory
        gradio_module.Warning = lambda *args, **kwargs: None
        gradio_module.Info = lambda *args, **kwargs: None
        gradio_module.update = lambda **kwargs: kwargs
        gradio_module.themes = types.SimpleNamespace(Soft=lambda: object())
        sys.modules["gradio"] = gradio_module
