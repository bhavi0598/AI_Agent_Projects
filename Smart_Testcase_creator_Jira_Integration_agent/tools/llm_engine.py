"""
llm_engine.py - LLM-powered test case generation engine.
Supports both Groq (cloud) and Ollama (local) providers.
Handles prompt construction, API calls, retries, response parsing.
Includes streaming support for real-time output display.
"""

import re
import time
import json
import requests


# ─── System Prompt ───────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are a QA Lead Engineer with 20 years of experience.
Generate comprehensive and structured test cases based on the provided JIRA ticket.

STRICT OUTPUT RULES:
1. Return ONLY a valid JSON array of test case objects. No markdown, no explanation, no extra text.
2. Each test case object must have exactly these keys:
   - "testCaseId": sequential integer (1, 2, 3, ...)
   - "testCaseName": short descriptive name
   - "steps": numbered steps as a sequential interger (e.g. 1,2,3,4 etc)
   - "expectedStepDescription": what the tester should do in detail
   - "actualStepDescription": expected system behavior from a real-user perspective

3. Cover ALL of the following:
   - Positive scenarios (happy path)
   - Negative scenarios (invalid inputs, unauthorized access, etc.)

4. Ensure:
   - No duplicate test case IDs
   - Logical step sequencing
   - Clear and actionable steps
   - Steps are written from the perspective of a manual tester


Output Format Instructions:

Generate test cases strictly in the following grouped tabular format only.

Columns:
- Unique Test Case ID
- Test Case Name
- Steps
- Expected Step Description
- Actual Step Description

Rules:
1. Unique Test Case ID must be numeric (1, 2, 3...) and should not repeat across different test cases.
2. Unique Test Case ID and Test Case Name should be written only once per test case.
3. For subsequent steps of the same test case, leave "Unique Test Case ID" and "Test Case Name" cells blank.
4. Steps must be sequential numbers (1, 2, 3...).
5. Cover positive, negative, and edge cases.
6. Output must be in table format only (no extra explanation).

Example Output:

| Unique Test Case ID | Test Case Name | Steps | Expected Step Description | Actual Step Description |
|--------------------|---------------|-------|---------------------------|-------------------------|
| 1 | Verify user login with valid credentials | 1 | Navigate to login page | Login page should be displayed |
|  |  | 2 | Enter valid username and password | Credentials should be accepted |
|  |  | 3 | Click on Login button | User should be redirected to dashboard |
| 2 | Verify login with invalid password | 1 | Navigate to login page | Login page should be displayed |
|  |  | 2 | Enter valid username and invalid password | System should accept input |
|  |  | 3 | Click on Login button | Error message should be displayed |
| 3 | Verify login with empty fields | 1 | Navigate to login page | Login page should be displayed |
|  |  | 2 | Leave username and password blank | Fields remain empty |
|  |  | 3 | Click on Login button | Validation message should be shown |

IMPORTANT: Return ONLY the markdown table. No extra explanation, no code fences."""


# ─── Prompt Builder ──────────────────────────────────────────────────────────

def build_prompt(ticket_data: dict) -> str:
    """Build the user prompt with JIRA ticket context."""
    prompt = f"""Generate comprehensive test cases for the following JIRA ticket:

TICKET KEY: {ticket_data.get('key', 'N/A')}
SUMMARY: {ticket_data.get('summary', 'N/A')}
ISSUE TYPE: {ticket_data.get('issue_type', 'N/A')}
PRIORITY: {ticket_data.get('priority', 'N/A')}
STATUS: {ticket_data.get('status', 'N/A')}

DESCRIPTION:
{ticket_data.get('description', 'No description provided.')}

ACCEPTANCE CRITERIA:
{ticket_data.get('acceptance_criteria', 'Not explicitly defined.')}

LABELS: {', '.join(ticket_data.get('labels', [])) or 'None'}

Instructions:
- Analyze the Acceptance Criteria thoroughly
- Extract QA Scope from the description
- Identify test scenarios from the steps mentioned
- Generate ALL possible functional test cases
- Follow the exact markdown table output format specified in the system prompt
- Cover positive, negative, and edge case scenarios"""

    return prompt


# ─── Groq Provider (Non-Streaming) ───────────────────────────────────────────

def generate_via_groq(api_key: str, model: str, ticket_data: dict, temperature: float = 0.1):
    """
    Generate test cases using Groq cloud API (non-streaming).
    Returns: (success, test_cases_list | error_message, raw_response)
    """
    from groq import Groq

    client = Groq(api_key=api_key)
    user_prompt = build_prompt(ticket_data)

    max_retries = 3
    for attempt in range(max_retries):
        try:
            completion = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temperature,
                max_tokens=4096,
                timeout=30
            )

            raw_response = completion.choices[0].message.content.strip()
            test_cases = _parse_llm_response(raw_response)

            if test_cases:
                return True, test_cases, raw_response
            else:
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                return False, "Failed to parse test cases from LLM response.", raw_response

        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
                continue
            return False, f"Groq API error after {max_retries} attempts: {str(e)}", None


# ─── Groq Provider (Streaming) ───────────────────────────────────────────────

def generate_via_groq_stream(api_key: str, model: str, ticket_data: dict, temperature: float = 0.1):
    """
    Generator that yields chunks of text from Groq streaming API.
    Yields: (chunk_text, is_done, final_result)
      - During streaming: (chunk_text, False, None)
      - On completion:    ("", True, (success, test_cases, raw_response))
    """
    from groq import Groq

    client = Groq(api_key=api_key)
    user_prompt = build_prompt(ticket_data)

    max_retries = 3
    for attempt in range(max_retries):
        try:
            stream = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temperature,
                max_tokens=4096,
                timeout=30,
                stream=True,
            )

            full_response = ""
            for chunk in stream:
                delta = chunk.choices[0].delta
                if delta and delta.content:
                    text = delta.content
                    full_response += text
                    yield text, False, None

            # Parse the complete response
            test_cases = _parse_llm_response(full_response)
            if test_cases:
                yield "", True, (True, test_cases, full_response)
                return
            else:
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                yield "", True, (False, "Failed to parse test cases from LLM response.", full_response)
                return

        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
                continue
            yield "", True, (False, f"Groq API error after {max_retries} attempts: {str(e)}", None)
            return


# ─── Ollama Provider (Non-Streaming) ─────────────────────────────────────────

def generate_via_ollama(base_url: str, model: str, ticket_data: dict, temperature: float = 0.1):
    """
    Generate test cases using local Ollama instance (non-streaming).
    Returns: (success, test_cases_list | error_message, raw_response)
    """
    url = f"{base_url.rstrip('/')}/api/chat"
    user_prompt = build_prompt(ticket_data)

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ],
        "stream": False,
        "options": {
            "temperature": temperature
        }
    }

    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = requests.post(url, json=payload, timeout=120)

            if response.status_code == 200:
                result = response.json()
                raw_response = result.get("message", {}).get("content", "")
                test_cases = _parse_llm_response(raw_response)

                if test_cases:
                    return True, test_cases, raw_response
                else:
                    if attempt < max_retries - 1:
                        time.sleep(2 ** attempt)
                        continue
                    return False, "Failed to parse test cases from LLM response.", raw_response
            else:
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                return False, f"Ollama returned HTTP {response.status_code}.", None

        except requests.exceptions.Timeout:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
                continue
            return False, "Ollama request timed out after 120s.", None
        except requests.exceptions.ConnectionError:
            return False, f"Cannot reach Ollama at {base_url}.", None
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
                continue
            return False, f"Ollama error after {max_retries} attempts: {str(e)}", None


# ─── Ollama Provider (Streaming) ─────────────────────────────────────────────

def generate_via_ollama_stream(base_url: str, model: str, ticket_data: dict, temperature: float = 0.1):
    """
    Generator that yields chunks of text from Ollama streaming API.
    Yields: (chunk_text, is_done, final_result)
      - During streaming: (chunk_text, False, None)
      - On completion:    ("", True, (success, test_cases, raw_response))
    """
    url = f"{base_url.rstrip('/')}/api/chat"
    user_prompt = build_prompt(ticket_data)

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ],
        "stream": True,
        "options": {
            "temperature": temperature
        }
    }

    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = requests.post(url, json=payload, timeout=120, stream=True)

            if response.status_code == 200:
                full_response = ""
                for line in response.iter_lines():
                    if line:
                        try:
                            chunk_data = json.loads(line)
                            content = chunk_data.get("message", {}).get("content", "")
                            if content:
                                full_response += content
                                yield content, False, None

                            # Check if done
                            if chunk_data.get("done", False):
                                break
                        except json.JSONDecodeError:
                            continue

                # Parse complete response
                test_cases = _parse_llm_response(full_response)
                if test_cases:
                    yield "", True, (True, test_cases, full_response)
                    return
                else:
                    if attempt < max_retries - 1:
                        time.sleep(2 ** attempt)
                        continue
                    yield "", True, (False, "Failed to parse test cases from LLM response.", full_response)
                    return
            else:
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                yield "", True, (False, f"Ollama returned HTTP {response.status_code}.", None)
                return

        except requests.exceptions.Timeout:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
                continue
            yield "", True, (False, "Ollama request timed out after 120s.", None)
            return
        except requests.exceptions.ConnectionError:
            yield "", True, (False, f"Cannot reach Ollama at {base_url}.", None)
            return
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
                continue
            yield "", True, (False, f"Ollama error after {max_retries} attempts: {str(e)}", None)
            return


# ─── Response Parser ─────────────────────────────────────────────────────────

def _parse_llm_response(raw_response: str):
    """
    Parse LLM response into a list of test case dicts.
    Handles: markdown tables (grouped rows), JSON arrays, and mixed formats.
    """
    if not raw_response:
        return None

    cleaned = raw_response.strip()

    # ── Strategy 1: Parse Markdown Table ──
    table_result = _parse_markdown_table(cleaned)
    if table_result:
        return table_result

    # ── Strategy 2: Try JSON (fallback) ──
    json_cleaned = re.sub(r'^```(?:json)?\s*\n?', '', cleaned)
    json_cleaned = re.sub(r'\n?```\s*$', '', json_cleaned).strip()

    try:
        parsed = json.loads(json_cleaned)
        if isinstance(parsed, list):
            return _validate_json_test_cases(parsed)
        elif isinstance(parsed, dict) and "testCases" in parsed:
            return _validate_json_test_cases(parsed["testCases"])
    except json.JSONDecodeError:
        pass

    # Try to find JSON array in the response
    match = re.search(r'\[[\s\S]*\]', json_cleaned)
    if match:
        try:
            parsed = json.loads(match.group())
            if isinstance(parsed, list):
                return _validate_json_test_cases(parsed)
        except json.JSONDecodeError:
            pass

    return None


def _parse_markdown_table(text: str):
    """
    Parse a markdown table with grouped rows into a flat list of test case dicts.
    Handles the format where Test Case ID and Name appear only on the first row
    of each test case, and subsequent step rows have those cells blank.
    """
    lines = text.strip().split("\n")

    # Find table lines (lines starting with |)
    table_lines = [line.strip() for line in lines if line.strip().startswith("|")]

    if len(table_lines) < 3:  # Need header + separator + at least 1 data row
        return None

    # Skip header row and separator row (---|---)
    data_lines = []
    header_found = False
    for line in table_lines:
        # Check if this is the separator row
        if re.match(r'^\|[\s\-:|]+\|$', line):
            header_found = True
            continue
        if header_found:
            data_lines.append(line)

    if not data_lines:
        # Try without separator detection (just skip first 2 lines)
        if len(table_lines) > 2:
            data_lines = table_lines[2:]
        else:
            return None

    # Parse each data row
    test_cases = []
    current_tc_id = None
    current_tc_name = None

    for line in data_lines:
        # Split by | and strip whitespace
        cells = [cell.strip() for cell in line.split("|")]
        # Remove empty strings from start/end (due to leading/trailing |)
        cells = [c for c in cells if c != "" or cells.index(c) not in [0, len(cells) - 1]]
        # Clean up: remove leading/trailing empty entries
        while cells and cells[0] == "":
            cells.insert(0, "")
            break
        cells = line.split("|")
        cells = [c.strip() for c in cells]
        # Remove first and last empty strings from split
        if cells and cells[0] == "":
            cells = cells[1:]
        if cells and cells[-1] == "":
            cells = cells[:-1]

        if len(cells) < 5:
            continue

        tc_id_raw = cells[0].strip()
        tc_name_raw = cells[1].strip()
        step_raw = cells[2].strip()
        expected_raw = cells[3].strip()
        actual_raw = cells[4].strip()

        # Update current test case if ID is provided (non-empty)
        if tc_id_raw:
            try:
                current_tc_id = int(tc_id_raw)
            except ValueError:
                # Try extracting number
                num_match = re.search(r'\d+', tc_id_raw)
                if num_match:
                    current_tc_id = int(num_match.group())
                else:
                    continue

        if tc_name_raw:
            current_tc_name = tc_name_raw

        if current_tc_id is None:
            continue

        # Parse step number
        try:
            step_num = int(step_raw)
        except ValueError:
            num_match = re.search(r'\d+', step_raw)
            step_num = int(num_match.group()) if num_match else 0

        test_cases.append({
            "testCaseId": current_tc_id,
            "testCaseName": current_tc_name or f"Test Case {current_tc_id}",
            "steps": step_num,
            "expectedStepDescription": expected_raw,
            "actualStepDescription": actual_raw,
        })

    return test_cases if test_cases else None


def _validate_json_test_cases(test_cases: list):
    """Validate and normalize JSON test case list (fallback parser)."""
    if not test_cases or not isinstance(test_cases, list):
        return None

    validated = []
    seen_ids = set()

    for i, tc in enumerate(test_cases):
        if not isinstance(tc, dict):
            continue

        tc_id = tc.get("testCaseId", i + 1)
        if tc_id in seen_ids:
            tc_id = max(seen_ids) + 1 if seen_ids else 1
        seen_ids.add(tc_id)

        validated.append({
            "testCaseId": tc_id,
            "testCaseName": tc.get("testCaseName", tc.get("test_case_name", f"Test Case {tc_id}")),
            "steps": tc.get("steps", tc.get("step", "N/A")),
            "expectedStepDescription": tc.get("expectedStepDescription", tc.get("expected_step_description", "N/A")),
            "actualStepDescription": tc.get("actualStepDescription", tc.get("actual_step_description", "N/A")),
        })

    return validated if validated else None
