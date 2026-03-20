# Findings

## Research
- Goal: Local LLM Testcase generator using Ollama.

## Discoveries
- **Model**: Specific usage of `llama3.2:1b` requested.
- **Integration**: Ollama API.
- **UI**: "UI chat" requested.
- **Template**: Needs to be defined in code.

## Constraints
- Local execution (Windows).
- Must use Ollama.
- **Potential Issue**: CORS when calling Ollama directly from a browser. May need a lightweight proxy or browser config. Or we can use a server-side route (Next.js would handle this well, or a simple Express backend).

