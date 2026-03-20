# Project Constitution

## North Star
Local LLM Testcase Generator using Ollama (`llama3.2:1b`) with a dedicated Chat UI.

## Data Schemas
### Test Case Object
```json
{
  "id": "TC-001",
  "title": "Short descriptive title",
  "description": "What is being tested",
  "preconditions": "State before test",
  "steps": [
    "Step 1 action",
    "Step 2 action"
  ],
  "expected_result": "Expected outcome"
}
```

### LLM Interaction
- **Input**: User Requirements / Story
- **System Prompt**: Enforced Template logic
- **Model**: `llama3.2:1b`

- (To be defined after receiving user prompt)

## Behavioral Rules
- **User Experience**: Rich, "premium" Chat UI (Vite/React).
- **Core Logic**: User Input -> Template Injection -> Ollama API -> Formatted Output.
- **Model constraint**: Must use `llama3.2:1b`.

## Architectural Invariants
- **Frontend**: Vite + React (Vanilla CSS for styling as per system rules, unless Tailwind requested).
- **AI Engine**: Ollama running locally at `localhost:11434` (standard port).
- **Storage**: Template is hardcoded/stored in source.
- **Protocol**: Protocol 0 is active.

