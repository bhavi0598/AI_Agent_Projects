# Streamlit UI Components SOP

**(Layer 1 Architecture)**

## Goal
Create a unified, aesthetic, entirely local UI utilizing Streamlit (`streamlit`). React is fully removed from this architecture.

## Page Structure
1. **Header**: Title, Subtitle, and local processing badges indicating privacy.
2. **Sidebar (Settings)**:
    - Model Selector (Radio or Selectbox reading from `OLLAMA_BASE_URL/api/tags`).
    - Status Indicator showing Ollama connection health.
3. **Main Content (Two Columns)**:
    - Left Column: "Source" settings. Select `Selenium Java` or `Selenium Python`. Includes `st.text_area` for pasting code.
    - Button: Centered "Convert to Playwright".
    - Right Column: "Destination" setting (locked to Playwright TypeScript). Includes `st.text_area` to display the output, or `st.code` for syntax-highlighted display.
4. **State Management**:
    - Manage `st.session_state` strictly to save the converted code against accidental re-renders when tweaking dropdowns.
5. **Errors/Validation**:
    - If empty code is submitted, show a warning.
    - If `qwen3:4b`/`llama3.2:1b` is not running, disable the convert button and show an error in the UI.

## File Mapping
- `app.py`: The Main UI orchestrator (Layer 2).
- It will import from `tools/llm_engine.py` (Layer 3) to execute logic deterministically.
