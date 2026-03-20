import ollama
from prompt import SYSTEM_PROMPT

def chat_llm(messages):
    try:
        stream = ollama.chat(
            model="qwen3:4b", 
            messages=[{"role": "system", "content": SYSTEM_PROMPT}] + messages,
            stream=True
        )
        for chunk in stream:
            yield chunk["message"]["content"]
    except Exception as e:
        yield f"Error: {str(e)}"
