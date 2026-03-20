# SOP: Test Case Creator Agent - Main Application Flow

## Goal
Provide a Streamlit-based UI that allows a QA engineer to:
1. Configure JIRA & LLM connections via sidebar
2. Fetch JIRA ticket details
3. Generate structured test cases using an LLM
4. View and copy results in a tabular format

## Architecture Layers

### Layer 1: UI (app.py)
- Streamlit sidebar: JIRA config, LLM provider toggle (Ollama/Groq), connection test buttons
- Main panel: Ticket input, data display, test case generation, tabular output
- State management via `st.session_state`

### Layer 2: Connection Management (tools/handshake.py)
- `test_jira_connection(base_url, email, api_token)` -> bool, message
- `test_groq_connection(api_key)` -> bool, message
- `test_ollama_connection(base_url)` -> bool, message, model_list
- All functions are stateless; credentials passed as arguments from UI

### Layer 3: Business Logic (tools/)
- `jira_client.py`: Fetch and parse JIRA ticket data into structured dict
- `llm_engine.py`: Build prompt context, call Groq or Ollama, parse tabular output

## Data Flow
```
User enters creds in sidebar
  -> handshake.py validates connection
  -> session_state stores connection status + creds (in-memory only)
  -> User enters JIRA ticket ID
  -> jira_client.py fetches ticket -> displays in table
  -> User clicks Generate
  -> llm_engine.py sends ticket context to LLM -> parses response
  -> Output displayed in editable table (copy-friendly)
```

## Error Handling
- Timeouts: Groq=30s, Ollama=120s
- Retries: 3 attempts with exponential backoff
- All errors surface as Streamlit toast/error messages

## Security
- Credentials live ONLY in `st.session_state` (in-memory, per-session)
- Never written to disk or local storage
- Session ends = credentials gone
