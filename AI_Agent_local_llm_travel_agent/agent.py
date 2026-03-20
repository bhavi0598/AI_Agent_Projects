from llm import chat_llm

def agent_reply(state, user_input):
    # Check if the last message in history is already the user input to avoid duplicates
    if not state["chat_history"] or state["chat_history"][-1].get("content") != user_input:
        state["chat_history"].append({"role": "user", "content": user_input})
    
    # Generate response stream
    response_stream = chat_llm(state["chat_history"])
    
    full_response = ""
    for chunk in response_stream:
        full_response += chunk
        yield chunk

    # Append assistant response after streaming is complete
    state["chat_history"].append({"role": "assistant", "content": full_response})
    return full_response
