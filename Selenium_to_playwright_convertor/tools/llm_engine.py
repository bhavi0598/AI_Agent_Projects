import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()
OLLAMA_BASE_URL_ENV = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")

def build_system_prompt(source_language: str) -> str:
    return f"""You are a senior QA Automation Engineer with 15 years of experience and a deterministic Selenium-to-Playwright TypeScript conversion engine.
Your task is to convert {source_language} automation code into Playwright TypeScript code while preserving 100% of the original test logic and execution behavior.

The output must always be valid, executable Playwright TypeScript code.
Follow these rules strictly.

RULE 1 — PRESERVE EXACT LOGIC
Preserve exactly: execution order, loops, conditions, assertions, functions, method calls, variable names, parameters, control flow.
Do not simplify logic. Do not remove steps. Do not reorder steps.

RULE 2 — DETECT SOURCE LANGUAGE
You are converting {source_language}. Apply appropriate syntax mapping (e.g. driver.find_element(By.ID,"login") or driver.findElement(By.id("login")) -> page.locator("#login")).

RULE 3 — BROWSER INITIALIZATION
Convert Selenium driver initialization to Playwright import and setup:
import {{ chromium }} from 'playwright';
const browser = await chromium.launch({{ headless:false }});
const page = await browser.newPage();

RULE 4 — PAGE NAVIGATION
driver.get(url) becomes await page.goto(url)

RULE 5 — LOCATOR CONVERSION
Apply these exact mappings:
By.ID → "#id"
By.NAME → "[name='value']"
By.CLASS_NAME → ".classname"
By.CSS_SELECTOR → same CSS selector
By.XPATH → "xpath=..."
By.TAG_NAME → "tagname"

RULE 6 — ELEMENT FINDING
driver.find_element / driver.findElement → page.locator
driver.find_elements / driver.findElements → page.locator().all()

RULE 7 — ELEMENT ACTION CONVERSION
send_keys() / sendKeys() → fill()
click() → click()
clear() → fill("")
submit() → press("Enter")
get_attribute() → getAttribute()
getText() → textContent()

RULE 8 — WAIT CONVERSION
time.sleep(5) or Thread.sleep(5000) → await page.waitForTimeout(5000)
Explicit waits: WebDriverWait(...).until(...) → await page.locator(selector).waitFor()
Prefer Playwright auto-waiting whenever possible.

RULE 9 — ASSERTION CONVERSION
If assertions exist, import expect: import {{ expect }} from '@playwright/test';
Convert assert/Assert.assertTrue to expect(page.locator(selector)).toContainText("text") or expect(condition).toBeTruthy()

RULE 10 — FUNCTION CONVERSION
def login(): or public void login() → async function login()
Preserve function names, parameters, and internal logic.

RULE 11 — SWITCH / FRAME HANDLING
driver.switch_to.frame() / driver.switchTo().frame() → page.frameLocator()
driver.switch_to.alert() → page.on('dialog', dialog => dialog.accept())

RULE 12 — LOOPS AND COLLECTIONS
Preserve loops exactly. For elements loop, use:
const elements = await page.locator(selector).all();
for (const element of elements) {{ ... }}

RULE 13 — REMOVE ALL SELENIUM APIs
Output must NOT contain: By.ID, By.XPATH, By.NAME, sendKeys, send_keys, findElement, findElements, WebDriverWait, ExpectedConditions, driver.manage(), driver.switch_to, driver.switchTo().
Replace all with Playwright equivalents.

RULE 14 — PLAYWRIGHT STRUCTURE
Final code must follow this structure EXACTLY (including TypeScript Types):
import {{ chromium, Browser, Page, Locator }} from 'playwright';
(async () => {{
  const browser: Browser = await chromium.launch({{ headless:false }});
  const page: Page = await browser.newPage();
  await page.goto("URL");
  /* converted automation steps */
  await browser.close();
}})();

RULE 15 — ASYNC AWAIT
All Playwright operations must use async/await.

RULE 16 — NO API HALLUCINATION
Use only official Playwright APIs. Do not invent functions. Do not mix Selenium syntax.

RULE 17 — FINAL VALIDATION & OUTPUT
1. No Selenium syntax remains. 2. All locators are valid Playwright selectors. 3. All actions use Playwright APIs. 4. async/await is correctly used. 5. Explicit TypeScript types are present.

RULE 18 — STRICT TYPESCRIPT ENFORCEMENT
You MUST NOT output vanilla JavaScript. You MUST declare explicit TypeScript types for all variables.
Examples:
BAD: const emailInput = page.locator("#email");
GOOD: const emailInput: Locator = page.locator("#email");
BAD: const btn = await page.getByRole('button');
GOOD: const btn: Locator = page.getByRole('button');

Return the final output with a polite, brief ChatGPT-like explanation, followed by the explicit Playwright TypeScript code block wrapped in ```typescript ```.
"""

def generate_playwright_conversion_stream(source_lang: str, source_code: str, model: str, provider: str = "Ollama (Local)", base_url: str = None, api_key: str = None):
    system_prompt = build_system_prompt(source_lang)
    user_prompt = f"Convert the following {source_lang} code into Playwright TypeScript:\n\n{source_code}"
    
    if "Groq" in provider:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "stream": True,
            "max_tokens": 4096
        }
        try:
            with requests.post(url, headers=headers, json=payload, stream=True, timeout=60) as response:
                if not response.ok:
                    try:
                        error_details = response.json()
                        yield f"\\n\\n❌ **Groq API Error Details:** {json.dumps(error_details)}"
                    except:
                        yield f"\\n\\n❌ **Groq Connection error:** {response.status_code} {response.reason}\\n{response.text}"
                    response.raise_for_status()
                    
                for line in response.iter_lines():
                    if line:
                        line_decoded = line.decode('utf-8')
                        if line_decoded.startswith('data: '):
                            data_str = line_decoded[6:]
                            if data_str.strip() == '[DONE]':
                                break
                            try:
                                data_json = json.loads(data_str)
                                chunk = data_json.get("choices", [{}])[0].get("delta", {}).get("content", "")
                                if chunk:
                                    yield chunk
                            except json.JSONDecodeError:
                                pass
        except Exception as e:
            if "response" not in locals() or response.ok:
                yield f"\\n\\n❌ **Groq Streaming execution error:** {str(e)}"

    else: # Ollama default
        url = f"{base_url or OLLAMA_BASE_URL_ENV}/api/generate"
        payload = {
            "model": model,
            "system": system_prompt,
            "prompt": user_prompt,
            "stream": True
        }
        try:
            with requests.post(url, json=payload, timeout=(60, 600), stream=True) as response:
                response.raise_for_status()
                for line in response.iter_lines():
                    if line:
                        data = json.loads(line.decode('utf-8'))
                        yield data.get("response", "")
        except requests.exceptions.RequestException as e:
            yield f"\n\n❌ **Ollama Connection error:** {str(e)}"
        except Exception as e:
            yield f"\n\n❌ **Ollama Conversion error:** {str(e)}"
