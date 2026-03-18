# Changelog

## v1.3 - 2026-03-18

- Updated Gemini integration to use current Gemini 3 Flash model IDs for conversion and post-processing.
- Extracted UI-independent workflow logic into `app_logic.py` to separate Gradio wiring from application behavior.
- Hardened API key fallback, output filename sanitization, collision handling, and empty AI response handling.
- Added unit tests covering conversion flow, post-processing flow, filename generation, and Gemini model wiring.
- Expanded README with project structure and local test instructions.

## v1.2

- Added URL conversion and AI post-processing toolset.

## v1.1

- Initial repository version with output folder handling and download support.
