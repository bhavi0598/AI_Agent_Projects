# 🔄 Selenium to Playwright Auto-Converter (Local Offline Agent)

Welcome to the **Selenium to Playwright Auto-Converter**! This project is an incredibly powerful, 100% locally hosted AI agent designed to help QA engineers automatically translate their old Selenium code (Java or Python) into modern, idiomatic Playwright TypeScript code using local Large Language Models (LLMs).

It was designed with a **privacy-first** approach: absolutely zero code leaves your computer. No OpenAI, no Anthropic, no cloud APIs. Everything runs on your own hardware via **Ollama**.

---

## 🏗️ Project Architecture

```mermaid
graph TD
    User([👨‍💻 User]) -->|Pastes Selenium Code| UI(🖥️ Streamlit Frontend - app.py)
    
    subgraph Python Backend 🐍
    UI -->|Triggers Conversion| Backend(⚙️ LLM Engine - tools/llm_engine.py)
    UI -->|Validates Connection| Handshake(🤝 Handshake - tools/handshake.py)
    end
    
    subgraph Local Environment 💻
    Backend -->|Streaming HTTP Request| Ollama(🦙 Ollama Server)
    Handshake -->|Ping & Check Models| Ollama
    Ollama -->|Loads Model into RAM| Model[(🧠 qwen3:4b / llama3.2:1b)]
    end
    
    Model -->|Generates Playwright TS Chunk by Chunk| Backend
    Backend -->|Streams Text back to UI| UI
    UI -->|Shows ChatGPT-like typing effect| User
```

---

## 📂 Folder Structure

Here is how the project is organized. It strictly follows a customized architecture format called **B.L.A.S.T.** (Blueprint, Link, Architect, Stylize, Trigger) ensuring high reliability.

```text
Selenium_to_playwright_convertor/
│
├── 🏃‍♂️ run_app.bat               # Easy 1-click startup script for Windows.
├── 🖥️ app.py                    # The Streamlit Frontend UI Application.
├── 📄 requirements.txt          # Python dependencies (Streamlit, requests, dotenv).
├── 🔒 .env                      # Simple configuration variables (like the Ollama URL).
│
├── tools/                       # Operational Python Scripts (The "Engine").
│   ├── llm_engine.py          # The script that talks to the LLM and manages the prompts.
│   └── handshake.py           # The script that checks if Ollama is awake and ready.
│
├── architecture/                # Documentation on our internal rules.
│   ├── translation_logic.md   # System Prompt strategies & syntax maps.
│   └── ui_components.md       # Notes on how the UI should behave.
│
└── 📝 Markdown Documents        # Project Memory (task_plan.md, progress.md, gemini.md)
```

---

## ⚙️ How the Code Works (File by File)

If you are a beginner, here is exactly what is happening under the hood when you run this project!

### 1. `run_app.bat` (The Starter)
This is a Windows batch file designed to make your life easy. 
When you double-click it, it quickly checks:
1. Do you have Python installed?
2. Are the libraries in `requirements.txt` downloaded? (It installs them quietly if not).
3. Is your Ollama application actually running in the background?
Finally, it runs `streamlit run app.py` to pop the user interface open in your web browser.

### 2. `app.py` (The Face of the App)
This file uses the **Streamlit** library to draw the UI you see on screen using simple Python commands. 
- It creates a sidebar for you to select which AI Model you want to use.
- It splits the page into two columns (Left side for your Input Code, Right side for the AI's Output Code).
- When you click "Convert", this file grabs your code, hands it to `llm_engine.py`, and waits for the AI to start "typing" back its answer, streaming it live onto the screen.

### 3. `tools/handshake.py` (The Checker)
Before the UI even loads, this script quietly knocks on Ollama's door (`localhost:11434`) and asks, *"Are you awake? What models do you have ready?"* 
If Ollama is sleeping or you didn't download any models, this tells `app.py` to show you a big red error so you know exactly what is wrong.

### 4. `tools/llm_engine.py` (The Brain)
This is where the magic happens. 
- It houses a massive, highly specific **17-Rule System Prompt**. This prompt explicitly tells the LLM the exact rules of QA Automation (e.g., *Always convert `driver.get` to `await page.goto`*, *Remove all Thread.sleeps*, etc.).
- It takes your pasted Selenium code, wraps it together with the 17 Rules, and sends an HTTP `POST` request to your local Ollama server.
- **Streaming Mode:** It tells Ollama to `stream=True`, meaning instead of waiting 2 minutes for the AI to finish thinking and sending one massive block of text, the AI sends the text word-by-word the instant it thinks of it. This creates the "ChatGPT" typing effect you see on screen!

### 5. `.env` (The Secrets/Variables file)
This handles configurations. Right now, it tells our Python code where to find Ollama locally. 
*(E.g., `OLLAMA_BASE_URL=http://localhost:11434`). If you ever move your AI to a giant server down the hall, you just change that URL here, and the app instantly redirects there!*

---

## 🚀 Getting Started

To run this application, you need to ensure you have two things on your computer:
1. **Python 3.10+** (To run the Streamlit UI logic).
2. **Ollama** installed (The engine to run the AI), with at least one model pulled locally.

### Step 1: Download AI Models
Ensure your Ollama app is running, open a terminal, and download a model to your hard drive:
```bash
ollama run qwen3:4b
# or
ollama run llama3.2:1b
```

### Step 2: Open the Application
Navigate to this project folder, and simply double click:
```text
run_app.bat
```
*(Or run `.\run_app.bat` inside your Terminal/Command Prompt).*

Your browser will pop open automatically. Just select your model, paste your Selenium code on the left, and watch the AI seamlessly convert it to Playwright TypeScript on the right!
