import os
import requests
from dotenv import load_dotenv

load_dotenv()

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

def test_ollama_connection():
    try:
        url = f"{OLLAMA_BASE_URL.rstrip('/')}/api/tags"
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            models = response.json().get("models", [])
            model_names = [m.get("name") for m in models]
            if model_names:
                preview = ", ".join(model_names[:5])
                if len(model_names) > 5:
                    preview += "..."
                print(f"[OK] Ollama connection successful! Found {len(model_names)} models: {preview}")
                return True
            else:
                print("[OK] Ollama connection successful, but no models found. (Try running `ollama pull llama3`)")
                return True
        else:
            print(f"[FAIL] Ollama connection failed. Status: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"[FAIL] Ollama connection failed. Is Ollama running on {OLLAMA_BASE_URL}?")
        return False
    except Exception as e:
        print(f"[FAIL] Error communicating with Ollama: {e}")
        return False

if __name__ == "__main__":
    print(f"Testing Ollama Connection to: {OLLAMA_BASE_URL}")
    test_ollama_connection()
