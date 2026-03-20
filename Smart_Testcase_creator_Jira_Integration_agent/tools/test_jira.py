import os
import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv

load_dotenv()

JIRA_BASE_URL = os.getenv("JIRA_BASE_URL")
JIRA_USER_EMAIL = os.getenv("JIRA_USER_EMAIL")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")

def test_jira_connection():
    if not JIRA_BASE_URL or not JIRA_USER_EMAIL or not JIRA_API_TOKEN:
        print("[FAIL] Missing Jira credentials in .env (JIRA_BASE_URL, JIRA_USER_EMAIL, JIRA_API_TOKEN)")
        return False
        
    url = f"{JIRA_BASE_URL.rstrip('/')}/rest/api/3/myself"
    
    try:
        response = requests.get(
            url,
            auth=HTTPBasicAuth(JIRA_USER_EMAIL, JIRA_API_TOKEN),
            headers={"Accept": "application/json"},
            timeout=10
        )
        if response.status_code == 200:
            user_data = response.json()
            print(f"[OK] Successfully connected to Jira as {user_data.get('displayName')} ({user_data.get('emailAddress')})")
            return True
        else:
            print(f"[FAIL] Jira connection failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"[FAIL] Error connecting to Jira: {e}")
        return False

if __name__ == "__main__":
    print(f"Testing Jira Connection to: {JIRA_BASE_URL}")
    test_jira_connection()
