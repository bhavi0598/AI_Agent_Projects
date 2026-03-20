# findings.md - Research, Discoveries, Constraints

## Initial Requirements Analysis (Phase 0)
- **Target Use Case:** Automating test case generation by reading JIRA tickets and prompting an LLM (Cloud/Local).
- **Core Integrations:**
  - JIRA REST API v3: to fetch Summary, Description, Acceptance Criteria, Priority, Status, Assignee, Labels.
  - Groq API: for fast cloud models. Timeout: 30s.
  - Ollama REST API (`http://localhost:11434`): for local models with dynamic model tags fetching. Timeout: 120s.
- **Security Constraints:** MUST NEVER store credentials in `localStorage` or open files. Use backend environment variables or OS secure storage (`keyring` in Python or encrypted configs). Do NOT persist credentials after session in plaintext.
- **Architectural Shift Notice:** The task requires both a "Frontend (Streamlit)" and "Backend Python REST API/service layer" OR tightly coupled logic depending on how Streamlit handles state.
- **Failures & Recoveries expected:** 
  - LLMs can fail or generate bad JSON. Retry up to 3 times with exponential backoff.
  - Require the LLM output strictly in tabular rows for easy Excel consumption.
- **UI Constraints:**
  - Validations using Regex for JIRA Tickets: `[A-Z]+-\d+`.
  - Sidebar for configurations (JIRA settings + LLM provider settings).
  - Main view inactive until configuration connection is tested and verified.

## Tech Stack Considerations
- Python 3.x
- Streamlit (UI)
- FastAPI / requests (Networking)
- Python `keyring` / `cryptography` (Secure storage on OS level)
- Groq python client / raw requests for Ollama.
