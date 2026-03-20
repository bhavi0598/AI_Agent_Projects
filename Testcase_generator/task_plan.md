# Task Plan

## Phases
- [ ] Phase 1: Initialization & Planning
- [ ] Phase 2: Core Development
- [ ] Phase 3: Testing & Polish

## Goals
- Create a local LLM Testcase generator using Ollama.

## Checklists
### Phase 1: Planning & Setup
- [x] Create project memory files (`task_plan.md`, `findings.md`, `gemini.md`)
- [x] Receive user prompt (North Star)
- [x] Define Data Schema in `gemini.md`
- [ ] **Discovery**: Confirm Template structure and UI preference (Web vs CLI - assuming Web based on "UI chat")
- [ ] **Technical Check**: Verify Ollama is running and `llama3.2:1b` is pulled.
- [x] **Blueprint**: Create `implementation_plan.md` (Blueprint).
- [ ] **Approval**: User approves the Blueprint.

### Phase 2: Core Development (The "Engine")
- [ ] Create `app.py` (Flask Server).
- [ ] Implement the prompt template module (Python).
- [ ] Create the API connector service for Ollama (Python `requests`).

### Phase 3: UI Development (The "Face")
- [ ] Create `static/index.html` (Native HTML).
- [ ] Create `static/style.css` (Premium Glassmorphism).
- [ ] Create `static/script.js` (Frontend Logic).

### Phase 4: Testing & Polish
- [ ] End-to-end test (Input -> Output).
- [ ] Refine the Prompt Template for better quality.
- [ ] Final UI Polish.

