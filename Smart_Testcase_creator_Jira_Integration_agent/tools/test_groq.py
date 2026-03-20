import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def test_groq_connection():
    if not GROQ_API_KEY:
        print("[FAIL] Missing GROQ_API_KEY in .env")
        return False
        
    try:
        client = Groq(api_key=GROQ_API_KEY)
        
        print("Initiating tiny test request to Groq...")
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": "Say strictly 'Hello Groq'"}]
        )
        
        response_text = completion.choices[0].message.content
        print(f"[OK] Groq connection successful! Response from model: {response_text}")
        return True
    
    except Exception as e:
        print(f"[FAIL] Groq connection failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing Groq Connection...")
    test_groq_connection()
