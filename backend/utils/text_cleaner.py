"""
ResearchGap AI - Text Cleaning Utilities
==========================================
Functions to clean and normalize text extracted from papers and PDFs.

These utilities are used before sending text to Gemini and before
storing text in the database to ensure consistent, clean data.
"""

import re


def clean_text(text):
    """
    Cleans raw text by removing excessive whitespace, special characters,
    and normalizing line breaks.
    
    Parameters:
        text: Raw text string to clean
    
    Returns:
        Cleaned text string
    """
    if not text:
        return ""
    
    # Replace multiple newlines with a single newline
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    # Replace multiple spaces with a single space
    text = re.sub(r' {2,}', ' ', text)
    
    # Remove null bytes and other control characters (keep newlines and tabs)
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)
    
    # Strip leading/trailing whitespace
    text = text.strip()
    
    return text


def truncate_text(text, max_length=15000):
    """
    Truncates text to a maximum length while trying to break at a sentence.
    
    This is important because Gemini has input limits,
    and we don't want to send 100-page PDFs as raw text.
    
    Parameters:
        text: Text to truncate
        max_length: Maximum character count
    
    Returns:
        Truncated text with a note if truncation occurred
    """
    if not text or len(text) <= max_length:
        return text
    
    # Try to find the last sentence boundary before the limit
    truncated = text[:max_length]
    
    # Look for the last period followed by a space or newline
    last_sentence = truncated.rfind('. ')
    if last_sentence > max_length * 0.7:  # Only if it's not too far back
        truncated = truncated[:last_sentence + 1]
    
    return truncated + "\n\n[Text truncated due to length]"


def extract_year_from_date(date_string):
    """
    Extracts a 4-digit year from various date formats.
    
    Examples:
        "2024-01-15" → "2024"
        "2024" → "2024"
        "January 2024" → "2024"
        "" → ""
    """
    if not date_string:
        return ""
    
    # Look for a 4-digit year
    match = re.search(r'(19|20)\d{2}', str(date_string))
    if match:
        return match.group(0)
    
    return ""


def normalize_doi(doi):
    """
    Normalizes a DOI to a consistent format.
    
    DOIs can appear as:
        "10.1234/abcd"
        "https://doi.org/10.1234/abcd"
        "doi:10.1234/abcd"
    
    We normalize to just the DOI identifier: "10.1234/abcd"
    """
    if not doi:
        return ""
    
    doi = str(doi).strip()
    
    # Remove common prefixes
    prefixes = ["https://doi.org/", "http://doi.org/", "doi:", "DOI:"]
    for prefix in prefixes:
        if doi.startswith(prefix):
            doi = doi[len(prefix):]
    
    return doi.strip()
