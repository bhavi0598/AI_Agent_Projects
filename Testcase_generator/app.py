from flask import Flask, request, jsonify, render_template
import requests
import json

app = Flask(__name__)

# Configuration
OLLAMA_API_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3.2:1b"

TESTCASE_PROMPT = """You are an expert QA Automation Engineer. 
Your task is to convert the User's Requirement into a structured list of Test Cases.
Return ONLY valid JSON. 

Structure your response EXACTLY as follows:
{
    "testCases": [
        {
            "id": "TC-001",
            "title": "Title of the test case",
            "description": "Description of what is being tested",
            "preconditions": "String describing state (e.g. 'User is on login page'). If none, use 'None'.",
            "steps": ["Step 1", "Step 2"],
            "expected_result": "String describing expected outcome",
            "type": "Positive" 
        }
    ]
}

IMPORTANT RULES:
1. 'steps' must be a simple ARRAY OF STRINGS. Do NOT use objects like {"step": "text"}.
2. 'preconditions' must be a STRING. Do NOT return null.
3. Return raw JSON only. No markdown formatting.
"""


CHAT_PROMPT = """You are a friendly and helpful AI assistant. 
Engage in a casual, polite conversation with the user. Keep your answers concise and helpful."""

MATH_PROMPT = """You are a Math AI Helper. 
Your goal is to solve mathematical problems including Addition, Subtraction, Multiplication, Division, Percentages, Simple Interest (S.I.), and Compound Interest (C.I.).

Rules:
1. Show the formula used (if applicable).
2. Show the step-by-step calculation.
3. State the final answer clearly.
"""

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/generate', methods=['POST'])
def generate_response():
    from flask import Response, stream_with_context
    import time
    
    data = request.json
    user_input = data.get('input', '')
    mode = data.get('mode', 'testcase') # testcase, chat, math
    
    if not user_input:
        return jsonify({"error": "No input provided"}), 400

    # Select Prompt and Configuration
    system_prompt = TESTCASE_PROMPT
    is_json_mode = False

    if mode == 'testcase':
        system_prompt = TESTCASE_PROMPT
        is_json_mode = True
    elif mode == 'chat':
        system_prompt = CHAT_PROMPT
    elif mode == 'math':
        system_prompt = MATH_PROMPT

    full_prompt = f"{system_prompt}\n\nUser Input: {user_input}"

    def generate():
        try:
            payload = {
                "model": MODEL_NAME,
                "prompt": full_prompt,
                "stream": True  # Enable streaming
            }
            
            # Only enforce JSON format for testcases
            if is_json_mode:
                payload["format"] = "json"
            
            response = requests.post(OLLAMA_API_URL, json=payload, stream=True)
            response.raise_for_status()
            
            # Stream the response
            for line in response.iter_lines():
                if line:
                    chunk = json.loads(line)
                    if 'response' in chunk:
                        token = chunk['response']
                        # Send each token as SSE (Server-Sent Events)
                        yield f"data: {json.dumps({'token': token, 'done': chunk.get('done', False)})}\n\n"
                        
        except requests.exceptions.RequestException as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return Response(stream_with_context(generate()), mimetype='text/event-stream')

if __name__ == '__main__':
    import webbrowser
    from threading import Timer
    import os
    
    def open_browser():
        webbrowser.open_new("http://localhost:3000")

    # Only open browser once (not when reloader restarts)
    if os.environ.get('WERKZEUG_RUN_MAIN') != 'true':
        Timer(1.5, open_browser).start()
    
    app.run(debug=True, port=3000)
