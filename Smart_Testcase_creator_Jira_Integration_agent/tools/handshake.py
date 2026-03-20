"""
handshake.py - Centralized connection establishment and validation
for JIRA, Groq, and Ollama services.

All functions are stateless - credentials are passed as arguments.
Returns tuple: (success: bool, message: str, extra_data: dict|None)
"""

import requests
from requests.auth import HTTPBasicAuth


def test_jira_connection(base_url: str, email: str, api_token: str):
    """
    Test JIRA connection by fetching the authenticated user's profile.
    Returns: (success, message, user_data)
    """
    if not base_url or not email or not api_token:
        return False, "All fields are required (Base URL, Email, API Token).", None

    url = f"{base_url.rstrip('/')}/rest/api/3/myself"

    try:
        response = requests.get(
            url,
            auth=HTTPBasicAuth(email, api_token),
            headers={"Accept": "application/json"},
            timeout=10
        )
        if response.status_code == 200:
            user_data = response.json()
            display_name = user_data.get("displayName", "Unknown")
            user_email = user_data.get("emailAddress", "")
            return True, f"Connected as {display_name} ({user_email})", user_data
        elif response.status_code == 401:
            return False, "Authentication failed. Check your email and API token.", None
        elif response.status_code == 403:
            return False, "Access forbidden. Check your permissions.", None
        elif response.status_code == 404:
            return False, "JIRA instance not found. Check your Base URL.", None
        else:
            return False, f"Connection failed (HTTP {response.status_code}).", None
    except requests.exceptions.Timeout:
        return False, "Connection timed out. Check your Base URL.", None
    except requests.exceptions.ConnectionError:
        return False, "Could not reach JIRA server. Check your Base URL and network.", None
    except Exception as e:
        return False, f"Unexpected error: {str(e)}", None


def test_groq_connection(api_key: str):
    """
    Test Groq connection by making a minimal chat completion request.
    Returns: (success, message, None)
    """
    if not api_key:
        return False, "Groq API Key is required.", None

    try:
        from groq import Groq
        client = Groq(api_key=api_key)

        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": "Reply with exactly: OK"}],
            max_tokens=5,
            temperature=0
        )

        response_text = completion.choices[0].message.content.strip()
        return True, f"Connected to Groq successfully. Model responded: '{response_text}'", None

    except Exception as e:
        error_msg = str(e)
        if "authentication" in error_msg.lower() or "api key" in error_msg.lower():
            return False, "Invalid Groq API Key.", None
        return False, f"Groq connection failed: {error_msg}", None


def test_ollama_connection(base_url: str = "http://localhost:11434"):
    """
    Test Ollama connection by fetching available models.
    Returns: (success, message, model_list)
    """
    if not base_url:
        base_url = "http://localhost:11434"

    try:
        url = f"{base_url.rstrip('/')}/api/tags"
        response = requests.get(url, timeout=5)

        if response.status_code == 200:
            models = response.json().get("models", [])
            model_names = [m.get("name") for m in models]
            if model_names:
                return True, f"Connected! Found {len(model_names)} model(s).", model_names
            else:
                return True, "Connected, but no models installed. Run 'ollama pull <model>' to add one.", []
        else:
            return False, f"Ollama responded with HTTP {response.status_code}.", None
    except requests.exceptions.ConnectionError:
        return False, f"Cannot reach Ollama at {base_url}. Is it running?", None
    except Exception as e:
        return False, f"Error: {str(e)}", None


def fetch_groq_models(api_key: str):
    """
    Fetch list of available Groq models.
    Returns: list of model id strings
    """
    if not api_key:
        return []
    try:
        from groq import Groq
        client = Groq(api_key=api_key)
        models_response = client.models.list()
        model_ids = sorted([m.id for m in models_response.data])
        return model_ids
    except Exception:
        # Fallback to common models
        return [
            "llama-3.3-70b-versatile",
            "llama-3.1-8b-instant",
            "mixtral-8x7b-32768",
            "gemma2-9b-it",
        ]
