# Project Constitution (gemini.md)

## 🎯 Target Goal (North Star)
A deterministic, full-stack Streamlit web application that automates Test Case Generation using structured Jira ticket data and LLM Models (Ollama and Groq).

## 📊 Data Schemas (Input/Output shapes)

### 1. Jira Ticket Metadata (Internal State & LLM Context)
```json
{
  "key": "VWO-123",
  "summary": "String",
  "description": "String",
  "priority": "String",
  "status": "String",
  "assignee": "String",
  "labels": ["String"],
  "acceptanceCriteria": "String (Parsed/Custom Field)"
}
```

### 2. LLM Prompt Configuration (Context Shape)
```json
{
  "provider": "groq|ollama",
  "model": "String",
  "temperature": 0.0,
  "system_prompt": "You are a QA Lead Engineer...",
  "ticket_context": { "..." }
}
```

### 3. Test Case Output (LLM JSON Target Shape)
```json
{
  "testCases": [
    {
      "testCaseId": "Number",
      "testCaseName": "String",
      "steps": "String (numbered steps)",
      "expectedStepDescription": "String",
      "actualStepDescription": "String"
    }
  ]
}
```

## 📜 Behavioral Rules & Architectural Invariants
1. **Security**: Never expose or cache API keys in the frontend state or local unencrypted storage. Use environment variables (.env) or python keyring securely.
2. **Deterministic UI**: The Test Case Generator panel is locked/inactive until both Jira & Provider connection validations pass.
3. **Resiliency**: LLM calls must have timeout configs (Groq=30s, Ollama=120s) and a hard retry mechanism (max 3 times with exponential backoff) mapped to fallback UI errors.
4. **Data Delivery Payload**: Final output MUST strictly be tabular in Streamlit, ready for copy/pasting into Excel. Ensure unique, sequential IDs for each test case row.
5. **No Guessing**: All errors must be logged cleanly in `.tmp/` or stdout during validation. 

## 📝 Maintenance Log
- *v0.1.0*: Initial Phase 0 Memory Initialized. Waiting on Blueprint confirmation.
