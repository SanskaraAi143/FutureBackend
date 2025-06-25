import re
import json
from typing import Any, Optional

def extract_untrusted_json(result_text: str) -> Optional[Any]:
    r"""
    Extract and parse JSON array from within the result string using regex \[.*\].
    Handles escaped double quotes.
    Args:
        result_text (str): The result string containing the JSON array.
    Returns:
        Parsed JSON data (list or dict), or None if not found/parsable.
    """
    match = re.search(r"\[.*\]", result_text, re.DOTALL)
    if match:
        json_str = match.group(0).strip()
        # Unescape double quotes if present
        if '\\"' in json_str:
            json_str = json_str.replace('\\"', '"')
        try:
            return json.loads(json_str)
        except Exception as e:
            print(f"[extract_untrusted_json] JSON parsing failed: {e}\njson_str: {json_str}")
            return None
    return None
