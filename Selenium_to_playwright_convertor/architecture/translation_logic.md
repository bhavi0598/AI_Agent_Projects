# Translation Logic SOP

**(Layer 1 Architecture)**

## Goal
To orchestrate a deterministic local LLM environment that strictly converts Selenium code (Java/Python) to idiomatic Playwright TypeScript.

## Rules & Constraints
1. **Absolutely Local**: The entire inference process will happen via Ollama REST API over `http://localhost:11434`. No external requests.
2. **Context Window Limitations**: `qwen3:4b` and `llama3.2:1b` have practical constraints on reasoning. The System Prompt must be heavily structured, utilizing specific "Do Not" statements.
3. **No Hallucinations (Markdown Only)**: The LLM output should strictly return ```typescript ... ``` formatted code underneath a polite explanation.

## System Prompt Blueprint
The system prompt injects exact constraints on the models utilizing a robust 17-Rule strict validation prompt engineered specifically for local LLMs:

```text
You are a senior QA Automation Engineer with 15 years of experience...
[Enforces 17 Strict Rules covering:]
1. Exact logic preservation
2. Source language detection
3. Browser initialization loops
4. Exact Locator Mappings (By.ID to #id, etc)
5. Strict Wait conversion strategies
6. Disallowing hallucinated Selenium APIs (findElement, sendKeys, ExpectedConditions).
7. Enforcing an explicit async/await wrapped typescript structure.
[See tools/llm_engine.py for complete prompt string]
```

## Parsing Output
1. The tool `llm_engine.py` will hit Ollama generate API as a stream.
2. It yields chunks instantly back to the `app.py` UI mimicking a ChatGPT-like typewriter effect.
3. The UI allows users to review the reasoning and the code logic side-by-side.

## Dependencies Tracker
- Required modules: `requests`, `json`
- Env Vars: `OLLAMA_BASE_URL`
