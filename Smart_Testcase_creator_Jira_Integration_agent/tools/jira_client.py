"""
jira_client.py - Fetch and parse JIRA ticket data into structured dict.
Stateless: credentials passed as arguments.
"""

import re
import requests
from requests.auth import HTTPBasicAuth


def validate_ticket_id(ticket_id: str) -> bool:
    """Validate JIRA ticket ID format: PROJECT-123"""
    return bool(re.match(r'^[A-Z]+-\d+$', ticket_id.strip().upper()))


def fetch_ticket(base_url: str, email: str, api_token: str, ticket_id: str):
    """
    Fetch a JIRA ticket by its key.
    Returns: (success, ticket_data_dict | error_message)
    """
    ticket_id = ticket_id.strip().upper()

    if not validate_ticket_id(ticket_id):
        return False, "Invalid ticket ID format. Expected format: PROJECT-123 (e.g., VWO-456)"

    url = f"{base_url.rstrip('/')}/rest/api/3/issue/{ticket_id}?expand=names"

    try:
        response = requests.get(
            url,
            auth=HTTPBasicAuth(email, api_token),
            headers={"Accept": "application/json"},
            timeout=15
        )

        if response.status_code == 200:
            data = response.json()
            fields = data.get("fields", {})
            names = data.get("names", {})

            # Parse description - handle Atlassian Document Format (ADF)
            description_raw = fields.get("description")
            description_text = _parse_adf(description_raw) if isinstance(description_raw, dict) else (description_raw or "No description")

            # Parse acceptance criteria using exact custom field names
            acceptance_criteria = _extract_acceptance_criteria(description_text, fields, names)

            # Build structured ticket data
            ticket_data = {
                "key": data.get("key", ticket_id),
                "summary": fields.get("summary", "N/A"),
                "description": description_text,
                "priority": fields.get("priority", {}).get("name", "N/A") if fields.get("priority") else "N/A",
                "status": fields.get("status", {}).get("name", "N/A") if fields.get("status") else "N/A",
                "assignee": fields.get("assignee", {}).get("displayName", "Unassigned") if fields.get("assignee") else "Unassigned",
                "labels": fields.get("labels", []),
                "acceptance_criteria": acceptance_criteria,
                "issue_type": fields.get("issuetype", {}).get("name", "N/A") if fields.get("issuetype") else "N/A",
            }

            return True, ticket_data

        elif response.status_code == 404:
            return False, f"Ticket '{ticket_id}' not found."
        elif response.status_code == 401:
            return False, "Authentication failed. Re-check your JIRA credentials."
        elif response.status_code == 403:
            return False, f"Access denied to ticket '{ticket_id}'."
        else:
            return False, f"Failed to fetch ticket (HTTP {response.status_code})."

    except requests.exceptions.Timeout:
        return False, "Request timed out while fetching ticket."
    except requests.exceptions.ConnectionError:
        return False, "Could not reach JIRA server."
    except Exception as e:
        return False, f"Unexpected error: {str(e)}"


def _parse_adf(adf_node):
    """
    Recursively parse Atlassian Document Format (ADF) JSON into plain text.
    """
    if adf_node is None:
        return ""

    if isinstance(adf_node, str):
        return adf_node

    text_parts = []

    if isinstance(adf_node, dict):
        node_type = adf_node.get("type", "")
        
        # Text node
        if node_type == "text":
            return adf_node.get("text", "")

        # Process children/content
        content = adf_node.get("content", [])
        for child in content:
            child_text = _parse_adf(child)
            if child_text:
                text_parts.append(child_text)

        # Add formatting based on node type
        joined = " ".join(text_parts)
        if node_type == "paragraph":
            return joined + "\n"
        elif node_type == "heading":
            level = adf_node.get("attrs", {}).get("level", 1)
            return "#" * level + " " + joined + "\n"
        elif node_type == "bulletList":
            return joined
        elif node_type == "orderedList":
            return joined
        elif node_type == "listItem":
            return "- " + joined + "\n"
        elif node_type == "codeBlock":
            return "```\n" + joined + "\n```\n"
        else:
            return joined

    if isinstance(adf_node, list):
        for item in adf_node:
            text_parts.append(_parse_adf(item))
        return " ".join(text_parts)

    return str(adf_node)


def _extract_acceptance_criteria(description_text: str, fields: dict, names: dict):
    """
    Try to extract acceptance criteria from:
    1. Custom fields mapping to 'Acceptance Criteria' name (robust method)
    2. Description text fallback
    """
    # 1. Target the exact custom field by its display name from Jira schema
    for field_key, field_name in names.items():
        name_lower = field_name.lower().strip()
        if "acceptance criteria" in name_lower or name_lower == "ac":
            value = fields.get(field_key)
            if value:
                if isinstance(value, str):
                    return value.strip()
                elif isinstance(value, dict):
                    parsed = _parse_adf(value)
                    if parsed:
                        return parsed.strip()
                elif isinstance(value, list) and len(value) > 0:
                    # sometimes lists of objects
                    if isinstance(value[0], dict):
                        return _parse_adf({"type": "doc", "content": value}).strip()
                    else:
                        return " ".join([str(v) for v in value]).strip()

    # 2. Fallback: Check if the description has an AC section manually
    if description_text:
        patterns = [
            r'(?i)acceptance\s*criteria[:\s]*\n?(.*?)(?=\n\s*\n|\Z)',
            r'(?i)ac[:\s]*\n?(.*?)(?=\n\s*\n|\Z)',
            r'(?i)given\s+.*?when\s+.*?then\s+.*',
        ]
        for pattern in patterns:
            match = re.search(pattern, description_text, re.DOTALL)
            if match:
                return match.group(0).strip()

    return "Not explicitly defined in ticket."
