# task_plan.md - Phases, Goals, and Checklists

## 🟢 Phase 0: Protocol 0 - Initialization [COMPLETED]
- [X] Create `task_plan.md`, `findings.md`, `progress.md`
- [X] Initialize `gemini.md` as Project Constitution
- [X] Define Initial Data Schema in `gemini.md`
- [X] Answer Discovery Questions based on User Input

## 🏗️ Phase 1: B - Blueprint (Vision & Logic)
- [ ] Define precise REST API endpoints for the Python Backend (JIRA fetch, LLM generate)
- [ ] Design stream response parsing logic (if applicable)
- [ ] Define exact Streamlit component breakdown (Sidebar, Main Panel, Output Table)
- [ ] Receive User Approval for Blueprint

## ⚡ Phase 2: L - Link (Connectivity)
- [ ] Setup `tools/jira_client.py` and verify JIRA API connection
- [ ] Setup `tools/llm_client.py` and verify Groq connection
- [ ] Validate Ollama local connection (`http://localhost:11434/api/tags`)

## ⚙️ Phase 3: A - Architect (The 3-Layer Build)
- [ ] Write SOPs in `.md` format under `architecture/` for JIRA parsing and LLM handling
- [ ] Setup Python REST Backend (FastAPI / Flask) OR directly integrate inside Streamlit depending on validation
- [ ] Create tools for credentials management securely (keychain/encrypted config)
- [ ] Create tests and validations

## ✨ Phase 4: S - Stylize (Refinement & UI)
- [ ] Map Streamlit Theme (Clean QA-style, blue/gray palette)
- [ ] Add toast notifications, loading skeletons, and interactive state markers
- [ ] Implement Ctrl+Enter / Ctrl+Shift+S shortcuts
- [ ] Structure the tabular data correctly for easy Excel copy

## 🛰️ Phase 5: T - Trigger (Deployment)
- [ ] Final end-to-end testing
- [ ] Write Maintenance Guide & Local Dev Setup Instructions
