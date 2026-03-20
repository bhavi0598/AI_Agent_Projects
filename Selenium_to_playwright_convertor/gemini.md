# Project Constitution

## Data Schemas

### Input JSON Structure (Frontend to Backend)
```json
{
  "source_language": "Selenium Java | Selenium Python",
  "source_code": "<raw_code_string>",
  "model": "qwen3:4b | llama3:2:1b"
}
```

### Output JSON Structure (Backend to Frontend)
```json
{
  "target_language": "Playwright TypeScript",
  "converted_code": "<converted_typescript_code>",
  "error": "<error_message_if_any>"
}
```

## Behavioral Rules
1. **User Interaction**: The frontend must be user-friendly, with explicit, polite status messages.
2. **Deterministic Processing**: The backend must explicitly validate the `model` and `source_language` choices prior to LLM delegation.
3. **Automated Conversion**: The LLM prompt must specifically mandate conversion of Selenium locator/wait logic into idiomatic Playwright TypeScript logic (`async/await`, auto-waiting).
4. **Resilience**: The backend must handle execution errors or LLM timeouts gracefully and return them to the UI properly.

## Architectural Invariants
1. **Frontend**: Streamlit-based UI featuring dual-editor panes (Source vs. Converted) and dropdowns for language/model selection. A user-friendly and aesthetically pleasing interface is paramount.
2. **Backend**: Python-based logic utilizing Streamlit as both the UI layer and request handler to process the tool invocations.
3. **Privacy**: 100% localized execution. Under no circumstances should any code or data leave the local machine. Ensure no external APIs (like OpenAI or Anthropic) are called.
4. **LLM Integration**: Strict localized execution using Ollama API, utilizing `qwen3:4b` or `llama3:2:1b` models.
5. **Source of Truth**: The script pasted in the source editor window serves as the primary data to be processed upon the 'convert code' trigger.

## Maintenance Log
- **Phase 5 Deployment Completed**: Initial release built and automated directly via `run_app.bat`.
- **Environment Context**: Python is inherently managing Streamlit processes. The model fallback structure operates based on `OLLAMA_BASE_URL` defined within the `.env`. If you deploy Ollama to a separate internal VM, adjust this variable there.
- **Troubleshooting**: If UI buttons are unresponsive, `tools/handshake.py` can be explicitly run from CLI to diagnose strict network connections to the Local LLM.
