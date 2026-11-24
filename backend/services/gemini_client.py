"""
ResearchGap AI - Direct Google Gemini Client
=============================================
Provides clean, direct communication with the Google Gemini REST API using `requests`.

Why direct REST instead of LangChain or complex SDKs?
- Zero abstraction overhead: inspect exact payloads and responses.
- Complete control over parameters, timeouts, and headers.
- Structured JSON output enforcement via Gemini's native `response_mime_type: "application/json"`.
- Minimal dependencies (only Python's `requests` library).
"""

import time
import logging
import requests
from typing import Dict, Any, Optional
from config import config
from utils.helpers import safe_json_parse

logger = logging.getLogger("researchgap.gemini_client")
logging.basicConfig(level=logging.INFO)


class GeminiError(Exception):
    """Custom exception for Gemini API errors."""
    pass


class GeminiConfigError(GeminiError):
    """Raised when GEMINI_API_KEY is missing or invalid."""
    pass


_QUOTA_EXHAUSTED_UNTIL = 0.0
_QUOTA_ERROR_MSG = ""


def is_gemini_quota_exhausted() -> bool:
    """Returns True if the Google Gemini API has signaled quota exhaustion within cooldown window."""
    global _QUOTA_EXHAUSTED_UNTIL
    return time.time() < _QUOTA_EXHAUSTED_UNTIL


def call_gemini(
    prompt: str,
    system_instruction: Optional[str] = None,
    json_mode: bool = True,
    temperature: float = 0.2,
    max_retries: int = 1
) -> str:
    """
    Sends a generation request directly to the Google Gemini API.
    
    Parameters:
        prompt: The user prompt
        system_instruction: Optional system instruction to guide model behavior
        json_mode: If True, forces output in valid JSON format
        temperature: Sampling temperature (0.0 - 1.0, lower = more deterministic)
        max_retries: Number of retry attempts on rate limits or transient errors
        
    Returns:
        Raw text response from the model (or JSON string if json_mode=True)
    """
    global _QUOTA_EXHAUSTED_UNTIL, _QUOTA_ERROR_MSG
    
    if is_gemini_quota_exhausted():
        raise GeminiError(_QUOTA_ERROR_MSG or "Google Gemini quota cooldown active (HTTP 429).")

    api_key = config.get("GEMINI_API_KEY", "").strip()
    if not api_key:
        raise GeminiConfigError(
            "GEMINI_API_KEY is not configured in .env. "
            "Please obtain a free API key at https://makersuite.google.com/app/apikey "
            "and add GEMINI_API_KEY=your_key to your .env file."
        )
        
    model = config.get("GEMINI_MODEL", "gemini-flash-lite-latest")
    base_url = config.get("GEMINI_BASE_URL", "https://generativelanguage.googleapis.com/v1beta")
    params = {"key": api_key}
    
    # Construct generation config
    generation_config: Dict[str, Any] = {
        "temperature": temperature,
        "maxOutputTokens": 4096,
    }
    if json_mode:
        generation_config["response_mime_type"] = "application/json"
        
    # Construct request payload
    payload: Dict[str, Any] = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": prompt}]
            }
        ],
        "generationConfig": generation_config,
    }
    
    if system_instruction:
        payload["system_instruction"] = {
            "parts": [{"text": system_instruction}]
        }
        
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "ResearchGapAI/1.0",
    }
    
    candidate_models = [model]
    for alt in ["gemini-flash-lite-latest", "gemini-flash-latest"]:
        if alt not in candidate_models:
            candidate_models.append(alt)
            
    last_error = None
    
    for current_model in candidate_models:
        endpoint = f"{base_url}/models/{current_model}:generateContent"
        for attempt in range(max_retries + 1):
            try:
                logger.info(f"Calling Gemini model '{current_model}' (attempt {attempt + 1}/{max_retries + 1})...")
                response = requests.post(
                    endpoint,
                    params=params,
                    json=payload,
                    headers=headers,
                    timeout=config.get("API_TIMEOUT", 15)
                )
                
                # Check for quota exhaustion (429 RESOURCE_EXHAUSTED)
                if response.status_code == 429:
                    err_body = response.text
                    if "RESOURCE_EXHAUSTED" in err_body or "Quota" in err_body or "quota" in err_body:
                        _QUOTA_EXHAUSTED_UNTIL = time.time() + 60.0
                        _QUOTA_ERROR_MSG = "Google Gemini quota rate limit active (HTTP 429). Retrying in 60s."
                        logger.warning(f"Google Gemini rate limited: {_QUOTA_ERROR_MSG}. Fast-failing to deterministic fallback.")
                        raise GeminiError(_QUOTA_ERROR_MSG)
                    if attempt < max_retries:
                        time.sleep(2)
                        continue
                    else:
                        last_error = f"HTTP 429: {response.text}"
                        break
                        
                # Handle transient 500, 503 (server overloaded)
                if response.status_code in [500, 503]:
                    if attempt < max_retries:
                        logger.warning(f"Gemini model '{current_model}' returned HTTP {response.status_code}. Retrying in 1s...")
                        time.sleep(1)
                        continue
                    else:
                        logger.warning(f"Gemini model '{current_model}' exhausted retries with HTTP {response.status_code}. Trying next model...")
                        last_error = f"HTTP {response.status_code}: {response.text}"
                        break
                        
                if response.status_code != 200:
                    last_error = f"HTTP {response.status_code}: {response.text}"
                    break
                    
                data = response.json()
                candidates = data.get("candidates", [])
                if not candidates:
                    last_error = "Gemini returned no candidates in response."
                    break
                    
                first_candidate = candidates[0]
                content = first_candidate.get("content", {})
                parts = content.get("parts", [])
                
                if not parts or "text" not in parts[0]:
                    last_error = "Gemini returned empty text content."
                    break
                    
                return parts[0]["text"]
                
            except requests.exceptions.Timeout:
                if attempt < max_retries:
                    logger.warning(f"Gemini model '{current_model}' timed out. Retrying...")
                    time.sleep(1)
                    continue
                last_error = "Request timed out."
                break
            except requests.exceptions.RequestException as e:
                last_error = f"Network error: {str(e)}"
                break
                
    raise GeminiError(f"All Gemini models exhausted. Last error: {last_error}")


def call_gemini_json(
    prompt: str,
    system_instruction: Optional[str] = None,
    default_factory: Optional[Any] = None
) -> Dict[str, Any]:
    """
    Convenience wrapper that calls Gemini with JSON mode and parses the result into a Python dict.
    
    Parameters:
        prompt: The prompt text
        system_instruction: System instructions
        default_factory: Value to return if parsing fails (defaults to empty dict)
        
    Returns:
        Parsed dictionary from Gemini response
    """
    raw_text = call_gemini(
        prompt=prompt,
        system_instruction=system_instruction,
        json_mode=True
    )
    return safe_json_parse(raw_text, default=default_factory or {})
