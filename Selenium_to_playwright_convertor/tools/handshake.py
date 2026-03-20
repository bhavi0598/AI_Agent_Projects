import os
import requests
import json
from pathlib import Path

# Load minimum config
ENV_FILE = Path(__file__).parent.parent / '.env'
env_vars = {}
if ENV_FILE.exists():
    with open(ENV_FILE, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                key, val = line.split('=', 1)
                env_vars[key] = val

OLLAMA_BASE_URL = env_vars.get('OLLAMA_BASE_URL', 'http://localhost:11434')
DEFAULT_MODEL = env_vars.get('DEFAULT_MODEL', 'qwen3:4b')

def check_ollama():
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
        if response.status_code == 200:
            data = response.json()
            models = [m['name'] for m in data.get('models', [])]
            return {"status": "success", "models": models}
        return {"status": "error", "message": f"HTTP {response.status_code}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def ping_model(model_name):
    try:
        payload = {
            "model": model_name,
            "prompt": "Say 'Handshake successful' and nothing else.",
            "stream": False
        }
        response = requests.post(f"{OLLAMA_BASE_URL}/api/generate", json=payload, timeout=20)
        if response.status_code == 200:
            data = response.json()
            return {"status": "success", "response": data.get('response', '').strip()}
        return {"status": "error", "message": f"HTTP {response.status_code}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    print(f"--- B.L.A.S.T Handshake Initiated ---")
    print(f"Checking Ollama at {OLLAMA_BASE_URL}...")
    
    health = check_ollama()
    if health['status'] == 'success':
        print(f"[OK] Ollama is RUNNING.")
        print(f"[OK] Available local models: {', '.join(health['models'])}")
        
        if DEFAULT_MODEL in health['models']:
            print(f"Checking {DEFAULT_MODEL} inference...")
            ping_res = ping_model(DEFAULT_MODEL)
            if ping_res['status'] == 'success':
                print(f"[OK] Inference {DEFAULT_MODEL} successful: {ping_res['response']}")
            else:
                print(f"[ERROR] Inference failed: {ping_res['message']}")
        else:
            print(f"[ERROR] Target model {DEFAULT_MODEL} not found in Ollama!")
    else:
        print(f"[ERROR] Ollama connection failed: {health['message']}")
