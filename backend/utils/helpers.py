"""
ResearchGap AI - Helper Utilities
===================================
General-purpose helper functions used across the application.
"""

import json
import re
from datetime import datetime


def safe_json_parse(text, default=None):
    """
    Safely parses a JSON string, returning a default value on failure.
    
    This is crucial for parsing Gemini API responses, which sometimes
    include markdown code fences or extra text around the JSON.
    
    Parameters:
        text: String that should contain JSON
        default: Value to return if parsing fails (defaults to empty dict)
    
    Returns:
        Parsed Python object (dict/list) or the default value
    """
    if default is None:
        default = {}
    
    if not text:
        return default
    
    # First, try direct parsing
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    
    # Gemini sometimes wraps JSON in markdown code fences like:
    # ```json
    # {"key": "value"}
    # ```
    # Try to extract JSON from code fences
    json_match = re.search(r'```(?:json)?\s*\n?(.*?)\n?```', text, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group(1).strip())
        except json.JSONDecodeError:
            pass
    
    # Try to find the first { or [ and parse from there
    for start_char, end_char in [("{", "}"), ("[", "]")]:
        start_idx = text.find(start_char)
        end_idx = text.rfind(end_char)
        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            try:
                return json.loads(text[start_idx:end_idx + 1])
            except json.JSONDecodeError:
                pass
    
    return default


def format_timestamp(timestamp_str=None):
    """
    Returns a human-readable timestamp.
    If no timestamp provided, returns the current time.
    """
    if timestamp_str:
        try:
            dt = datetime.fromisoformat(timestamp_str)
            return dt.strftime("%B %d, %Y at %I:%M %p")
        except (ValueError, TypeError):
            return timestamp_str
    
    return datetime.now().strftime("%B %d, %Y at %I:%M %p")


def build_search_queries(topic, keywords="", domain=""):
    """
    Generates search query variations from user input.
    
    Academic APIs work better with well-formed queries.
    This function creates multiple query strings to maximize
    the chance of finding relevant papers.
    
    Parameters:
        topic: Main research topic
        keywords: Comma-separated additional keywords
        domain: Research domain
    
    Returns:
        List of search query strings
    """
    queries = []
    
    # Primary query: the topic itself
    queries.append(topic.strip())
    
    # If keywords provided, combine topic with keywords
    if keywords:
        keyword_list = [kw.strip() for kw in keywords.split(",") if kw.strip()]
        if keyword_list:
            # Topic + first few keywords
            combined = f"{topic} {' '.join(keyword_list[:3])}"
            queries.append(combined)
    
    # If domain provided, combine topic with domain
    if domain:
        domain_query = f"{topic} {domain}"
        if domain_query not in queries:
            queries.append(domain_query)
    
    # Remove duplicate queries
    seen = set()
    unique_queries = []
    for q in queries:
        q_lower = q.lower().strip()
        if q_lower not in seen:
            seen.add(q_lower)
            unique_queries.append(q)
    
    return unique_queries
