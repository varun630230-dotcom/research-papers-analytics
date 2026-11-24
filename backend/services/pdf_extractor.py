"""
ResearchGap AI - PDF Text Extraction Service
=============================================
Safely downloads and extracts full text from open-access academic PDFs using PyPDF.

Key Capabilities:
1. Streaming download with strict size capping (prevents memory exhaustion on large files)
2. Signature verification (ensures downloaded file starts with %PDF)
3. Page-by-page text extraction with page limits (e.g. max 20 pages)
4. Graceful handling of encrypted, password-protected, or corrupted PDFs
5. Detection of scanned/raster-only PDFs (plain text < 100 chars across pages)
6. Automatic fallback to paper abstract when PDF is unavailable or paywalled
7. Strict character budget truncation (capped at 15,000 chars) for Gemini input
"""

import io
import logging
import requests
import pypdf
from typing import Dict, Any, Optional, Tuple, List
from concurrent.futures import ThreadPoolExecutor, as_completed

from config import config
from utils.text_cleaner import clean_text, truncate_text

logger = logging.getLogger("researchgap.pdf_extractor")
logging.basicConfig(level=logging.INFO)


# =============================================================================
# 1. SAFE PDF DOWNLOADER
# =============================================================================

def download_pdf_bytes(
    pdf_url: str, 
    max_size_bytes: int = 10 * 1024 * 1024,
    timeout_seconds: int = 20
) -> Tuple[Optional[bytes], str]:
    """
    Safely downloads a PDF from a URL into memory with size limits.
    
    Parameters:
        pdf_url: Direct URL to the PDF document
        max_size_bytes: Maximum allowed file size (default: 10 MB)
        timeout_seconds: Network request timeout
        
    Returns:
        (pdf_bytes, status_message)
    """
    if not pdf_url or not pdf_url.strip().startswith(("http://", "https://")):
        return None, "Invalid or missing PDF URL"
        
    headers = {
        "User-Agent": "ResearchGapAI/1.0 (academic-research-tool; mailto:info@researchgap.ai)",
        "Accept": "application/pdf,application/octet-stream,*/*",
    }
    
    try:
        # Use stream=True to check Content-Length before downloading entire body
        response = requests.get(
            pdf_url, 
            headers=headers, 
            stream=True, 
            timeout=timeout_seconds,
            allow_redirects=True
        )
        
        if response.status_code != 200:
            return None, f"HTTP {response.status_code} ({response.reason})"
            
        # Check Content-Length header if reported
        content_length = response.headers.get("Content-Length")
        if content_length and int(content_length) > max_size_bytes:
            return None, f"File size ({int(content_length)} bytes) exceeds limit ({max_size_bytes} bytes)"
            
        # Download in chunks to enforce size limit dynamically
        chunks = []
        downloaded = 0
        for chunk in response.iter_content(chunk_size=32 * 1024):
            downloaded += len(chunk)
            if downloaded > max_size_bytes:
                return None, f"Download exceeded maximum size limit of {max_size_bytes // (1024 * 1024)}MB"
            chunks.append(chunk)
            
        pdf_bytes = b"".join(chunks)
        
        # Verify PDF magic signature (%PDF-)
        if not pdf_bytes.startswith(b"%PDF"):
            # Check if it was an HTML login/paywall redirect
            if b"<html" in pdf_bytes[:500].lower():
                return None, "URL returned HTML landing page instead of PDF (likely paywall or login required)"
            return None, "File does not have a valid PDF header (%PDF-)"
            
        return pdf_bytes, "Downloaded successfully"
        
    except requests.exceptions.Timeout:
        return None, "Download timed out"
    except requests.exceptions.RequestException as e:
        return None, f"Network error: {str(e)}"
    except Exception as e:
        return None, f"Unexpected error during download: {str(e)}"


# =============================================================================
# 2. PYPDF TEXT EXTRACTION
# =============================================================================

def extract_text_from_pdf_bytes(
    pdf_bytes: bytes, 
    max_pages: int = 20
) -> Dict[str, Any]:
    """
    Extracts text from PDF bytes using PyPDF.
    
    Handles:
    - Encrypted/password protected PDFs
    - Scanned/raster image-only PDFs
    - Malformed or corrupt PDF streams
    
    Returns:
        Structured dictionary with extraction metrics and text.
    """
    if not pdf_bytes:
        return {
            "status": "error",
            "text": "",
            "page_count": 0,
            "pages_processed": 0,
            "char_count": 0,
            "is_scanned_or_image": False,
            "is_encrypted": False,
            "message": "Empty PDF input",
        }
        
    try:
        stream = io.BytesIO(pdf_bytes)
        reader = pypdf.PdfReader(stream)
        
        # Check encryption
        if reader.is_encrypted:
            try:
                # Attempt empty password decryption (common for open-access PDF permissions)
                reader.decrypt("")
            except Exception:
                return {
                    "status": "encrypted",
                    "text": "",
                    "page_count": len(reader.pages) if hasattr(reader, "pages") else 0,
                    "pages_processed": 0,
                    "char_count": 0,
                    "is_scanned_or_image": False,
                    "is_encrypted": True,
                    "message": "PDF is encrypted or password-protected",
                }
                
        total_pages = len(reader.pages)
        pages_to_extract = min(total_pages, max_pages)
        extracted_pages = []
        
        for i in range(pages_to_extract):
            try:
                page = reader.pages[i]
                page_text = page.extract_text() or ""
                if page_text.strip():
                    extracted_pages.append(page_text.strip())
            except Exception as page_err:
                logger.warning(f"Error extracting page {i+1}: {page_err}")
                continue
                
        full_text = "\n\n".join(extracted_pages)
        full_text = clean_text(full_text)
        char_count = len(full_text)
        
        # Detect scanned/image-only PDFs:
        # If the document has pages, but extracted text is tiny (< 100 characters total across pages),
        # it is almost certainly a raster scan without an embedded text layer.
        is_scanned = (total_pages > 0 and char_count < 100)
        
        if is_scanned:
            return {
                "status": "scanned",
                "text": full_text,
                "page_count": total_pages,
                "pages_processed": pages_to_extract,
                "char_count": char_count,
                "is_scanned_or_image": True,
                "is_encrypted": False,
                "message": "PDF appears to be scanned or contains non-extractable raster images (OCR not configured).",
            }
            
        return {
            "status": "success",
            "text": full_text,
            "page_count": total_pages,
            "pages_processed": pages_to_extract,
            "char_count": char_count,
            "is_scanned_or_image": False,
            "is_encrypted": False,
            "message": f"Successfully extracted {char_count} characters across {pages_to_extract} pages.",
        }
        
    except pypdf.errors.PdfReadError as e:
        return {
            "status": "corrupt",
            "text": "",
            "page_count": 0,
            "pages_processed": 0,
            "char_count": 0,
            "is_scanned_or_image": False,
            "is_encrypted": False,
            "message": f"PyPDF read error (corrupted or malformed PDF): {str(e)}",
        }
    except Exception as e:
        return {
            "status": "error",
            "text": "",
            "page_count": 0,
            "pages_processed": 0,
            "char_count": 0,
            "is_scanned_or_image": False,
            "is_encrypted": False,
            "message": f"Extraction failed: {str(e)}",
        }


# =============================================================================
# 3. HIGH-LEVEL PAPER EXTRACTION WITH FALLBACK
# =============================================================================

def extract_paper_content(
    paper: Dict[str, Any], 
    max_length: int = 15000
) -> Dict[str, Any]:
    """
    Extracts content for a single paper:
    - If pdf_url is present, downloads and extracts PDF text.
    - If PDF extraction succeeds and text length > abstract, uses PDF text.
    - If PDF is unavailable, paywalled, scanned, or invalid, falls back to abstract.
    - Truncates to max_length (default 15,000 chars) for Gemini processing budget.
    - Preserves all original paper metadata without alteration.
    
    Returns:
        Updated paper dictionary with 'content_for_analysis' and 'extraction_info'.
    """
    paper_copy = dict(paper)
    pdf_url = paper_copy.get("pdf_url", "")
    abstract = paper_copy.get("abstract", "")
    
    extraction_info = {
        "has_pdf_url": bool(pdf_url),
        "extraction_attempted": False,
        "extraction_status": "no_pdf_url",
        "content_source": "abstract",
        "char_count": len(abstract),
        "message": "Using paper abstract",
    }
    
    extracted_text = ""
    
    if pdf_url:
        extraction_info["extraction_attempted"] = True
        logger.info(f"Downloading PDF for: '{paper_copy.get('title', '')[:50]}...'")
        
        pdf_bytes, dl_msg = download_pdf_bytes(
            pdf_url, 
            max_size_bytes=config.get("MAX_PDF_SIZE", 10 * 1024 * 1024)
        )
        
        if pdf_bytes:
            result = extract_text_from_pdf_bytes(pdf_bytes, max_pages=20)
            extraction_info["extraction_status"] = result["status"]
            extraction_info["page_count"] = result["page_count"]
            extraction_info["message"] = result["message"]
            
            if result["status"] == "success" and len(result["text"]) > len(abstract):
                extracted_text = result["text"]
                extraction_info["content_source"] = "pdf_text"
                extraction_info["char_count"] = len(extracted_text)
            elif result["status"] == "scanned":
                extraction_info["message"] = "Scanned PDF detected without OCR; falling back to abstract."
            else:
                extraction_info["message"] = f"PDF extraction yielded minimal text; falling back to abstract."
        else:
            extraction_info["extraction_status"] = "download_failed"
            extraction_info["message"] = f"Download failed: {dl_msg}; falling back to abstract."
            
    # Decide final content to provide for downstream AI analysis
    final_raw_content = extracted_text if extracted_text else abstract
    
    # Apply safe sentence-aware truncation
    final_content = truncate_text(
        final_raw_content, 
        max_length=max_length
    )
    
    paper_copy["pdf_text"] = extracted_text
    paper_copy["content_for_analysis"] = final_content
    paper_copy["extraction_info"] = extraction_info
    
    return paper_copy


def batch_extract_papers(
    papers: List[Dict[str, Any]], 
    max_to_extract: int = 5,
    max_workers: int = 3
) -> List[Dict[str, Any]]:
    """
    Extracts text for a batch of papers concurrently.
    To preserve bandwidth and processing speed, prioritizes the top 'max_to_extract'
    papers that have valid PDF URLs.
    
    Parameters:
        papers: List of paper dictionaries (assumed pre-sorted by relevance)
        max_to_extract: Number of PDF papers to fully download and extract
        max_workers: Concurrent download threads
        
    Returns:
        Updated list of papers with extracted content.
    """
    logger.info(f"Starting batch PDF extraction for up to {max_to_extract} papers...")
    processed_papers: List[Dict[str, Any]] = []
    
    pdf_candidates = [
        (i, p) for i, p in enumerate(papers) 
        if p.get("pdf_url")
    ][:max_to_extract]
    
    candidate_indices = {i for i, _ in pdf_candidates}
    
    # Process papers with PDF concurrently
    extracted_map = {}
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_idx = {
            executor.submit(extract_paper_content, paper): idx
            for idx, paper in pdf_candidates
        }
        
        for future in as_completed(future_to_idx):
            idx = future_to_idx[future]
            try:
                enriched = future.result()
                extracted_map[idx] = enriched
            except Exception as e:
                logger.error(f"Error extracting paper index {idx}: {e}")
                # Fallback on original paper
                extracted_map[idx] = extract_paper_content(papers[idx])
                
    # Reassemble list in original order
    for i, paper in enumerate(papers):
        if i in extracted_map:
            processed_papers.append(extracted_map[i])
        else:
            # Paper was not chosen for full PDF extraction; populate default content
            p_copy = dict(paper)
            p_copy["content_for_analysis"] = truncate_text(p_copy.get("abstract", ""))
            p_copy["extraction_info"] = {
                "has_pdf_url": bool(p_copy.get("pdf_url")),
                "extraction_attempted": False,
                "content_source": "abstract",
                "message": "Using paper abstract",
            }
            processed_papers.append(p_copy)
            
    return processed_papers
