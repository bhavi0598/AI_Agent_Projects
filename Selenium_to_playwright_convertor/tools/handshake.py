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

OLLAMA_BASE_URL_ENV = env_vars.get('OLLAMA_BASE_URL', 'http://localhost:11434')

def check_ollama(base_url=None):
    target_url = base_url if base_url else OLLAMA_BASE_URL_ENV
    try:
        response = requests.get(f"{target_url}/api/tags", timeout=5)
        if response.status_code == 200:
            data = response.json()
            models = [m['name'] for m in data.get('models', [])]
            return {"status": "success", "models": models}
        return {"status": "error", "message": f"HTTP {response.status_code}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def ping_model(model_name, base_url=None):
    target_url = base_url if base_url else OLLAMA_BASE_URL_ENV
    try:
        payload = {
            "model": model_name,
            "prompt": "Say 'Handshake successful' and nothing else.",
            "stream": False
        }
        response = requests.post(f"{target_url}/api/generate", json=payload, timeout=20)
        if response.status_code == 200:
            data = response.json()
            return {"status": "success", "response": data.get('response', '').strip()}
        return {"status": "error", "message": f"HTTP {response.status_code}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    health = check_ollama()
    print(health)
