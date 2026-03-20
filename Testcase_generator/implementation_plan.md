# Implementation Plan - Local LLM Testcase Generator

## Architecture
**Stack**: MERN-lite (Vite + React + Node/Express) calling Local Ollama.

### 1. Frontend (The "Face")
- **Technology**: Native HTML5, CSS3, JavaScript (ES6+).
- **Hosting**: Served statically by the Python Backend.
- **Styling**: Vanilla CSS with "Glassmorphism" and "Neon/Dark" aesthetics.
- **Why**: `npm` is not available, so we cannot use a build step (Vite/React). We will build a high-quality "Vanilla" app.

### 2. Backend (The "Brain Proxy")
- **Framework**: Python (Flask).
- **Purpose**:
    - Serve the Frontend files.
    - Handle CORS (if needed) and Proxy requests to Ollama.
    - Inject the **Prompt Template**.
- **Endpoints**:
    - `GET /`: Serves the Chat UI.
    - `POST /api/generate`: Recieves `{ input: string }` -> Returns `{ testCases: string/json }`.

### 3. AI Integration
- **Model**: `llama3.2:1b`.
- **Prompt Strategy**:
    - **System**: "You are a QA automation expert. Output ONLY valid JSON/Markdown formatted test cases..."
    - **Template**:
      ```text
      Given the following User Requirement:
      {{USER_INPUT}}

      Generate 3-5 comprehensive test cases covering positive, negative, and edge scenarios.
      Format: [Standard JSON Structure defined in gemini.md]
      ```

## Step-by-Step Implementation

### Step 1: Backend Setup (Python)
1. Use existing `server/` directory (or repurpose).
2. Create `app.py`.
3. Install dependencies: `pip install flask requests`.
4. Implement `/api/generate` to talk to Ollama.

### Step 2: Frontend Setup (Static)
1. Create `static/` and `templates/` structure.
2. Create `index.html` (The Shell).
3. Create `style.css` (The Aesthetics).
4. Create `app.js` (The Logic).

### Step 3: UI Implementation
1. Write the HTML structure.
2. Apply Glassmorphism CSS (Backdrop filter, translucent colors).
3. Write JS to `fetch('/api/generate')` and render results.


### Step 4: Refinement
1. Improve the System Prompt for better test case quality.
2. Add "Copy to Clipboard" for the test cases.
3. Final Aesthetic Polish (Animations).
