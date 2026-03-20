# Findings

## Research
- Translating Selenium to Playwright using LLMs requires strategic prompting:
  - Specifying exact locator mappings (`By.ID` -> `page.locator()`, `getByRole()`).
  - Mapping explicit waits or thread sleeps into Playwright auto-waiting.
  - Converting synchronous Python/Java into asynchronous (`async`/`await`) Playwright TypeScript code.
- Smaller models (like `qwen3:4b` or `llama3:2:1b`) might require clear, role-based "system prompts" and potentially "few-shot" examples to maintain high consistency and reduce hallucinations.

## Discoveries
- Combining React (Frontend), Python (Backend API), and Ollama (LLM) creates a robust 3-layer web application. Python (e.g., FastAPI or Flask) is optimal for processing requests and communicating with the Ollama local server seamlessly. 
- Using Python 3.10 natively on Windows required handling cp1252 text encoding constraints; printing emojis in the console string buffers caused a crash, establishing a minor environmental rule to stick strictly to ASCII logs.

## Constraints
- Models are restricted to local Ollama (`qwen3:4b` / `llama3:2:1b`). The models must be pulled locally. (Verified: Models are available!)
- Input must be strictly Selenium Java or Selenium Python code; Output must be Playwright TypeScript.
- The UI must have two side-by-side editors and act polite/user-friendly.
- **Node.js**: The system does NOT currently have `node` installed on path, meaning we cannot easily initialize a standard React Vite/CRA project right now. Options include prompting the User to install Node.js or serving the React build via CDN in a simple HTML page if it's very lightweight.
