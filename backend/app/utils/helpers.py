import uuid
import json
import re

def generate_id() -> str:
    return uuid.uuid4().hex

def normalize_title(title: str) -> str:
    if not title:
        return ""
    return re.sub(r'[^a-z0-9]', '', title.lower())

def titles_similar(t1: str, t2: str) -> bool:
    nt1 = normalize_title(t1)
    nt2 = normalize_title(t2)
    if not nt1 or not nt2:
        return False
    # Simple substring check or exact match
    return nt1 == nt2 or nt1 in nt2 or nt2 in nt1

def safe_json_loads(text: str) -> dict:
    try:
        match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', text)
        if match:
            text = match.group(1)
        return json.loads(text)
    except Exception as e:
        # Fallback empty dict
        print(f"JSON parse error: {e}")
        return {}

def truncate_text(text: str, max_length: int) -> str:
    if not text:
        return ""
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."
