"""
ResearchGap AI - Academic Paper Discovery Service
==================================================
Discovers academic research papers from four major sources:
1. OpenAlex (https://openalex.org)
2. arXiv (https://arxiv.org)
3. Semantic Scholar (https://semanticscholar.org)
4. Crossref (https://crossref.org)

Architecture & Design Principles:
- Single Responsibility: Each search function handles exactly one academic source.
- Normalization: Every source produces standard paper dictionaries with identical keys.
- Reliability: If any API fails or rate-limits, others continue seamlessly.
- Concurrency: Uses standard library ThreadPoolExecutor for fast parallel queries.
- Clean Data: Reconstructs OpenAlex inverted index abstracts, cleans XML tags,
  and normalizes DOIs.
"""

import re
import html
import logging
import requests
import xml.etree.ElementTree as ET
from typing import List, Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

from config import config
from utils.text_cleaner import clean_text, normalize_doi, extract_year_from_date

logger = logging.getLogger("researchgap.paper_search")
logging.basicConfig(level=logging.INFO)


# =============================================================================
# HELPER FUNCTIONS FOR NORMALIZATION & TEXT CLEANING
# =============================================================================

def reconstruct_openalex_abstract(inverted_index: Optional[Dict[str, List[int]]]) -> str:
    """
    Reconstructs full text abstract from OpenAlex's inverted index format.
    
    OpenAlex stores abstracts as: {"Word": [0, 5], "another": [1], ...}
    This function places each word at its position and joins them.
    """
    if not inverted_index or not isinstance(inverted_index, dict):
        return ""
    
    position_map = {}
    for word, positions in inverted_index.items():
        if isinstance(positions, list):
            for pos in positions:
                position_map[pos] = word
                
    if not position_map:
        return ""
        
    sorted_positions = sorted(position_map.keys())
    ordered_words = [position_map[pos] for pos in sorted_positions]
    return clean_text(" ".join(ordered_words))


def strip_html_tags(text: str) -> str:
    """Removes HTML and XML tags (like Crossref JATS tags <jats:p>) from text."""
    if not text:
        return ""
    # Unescape HTML entities first (e.g. &lt; -> <)
    unescaped = html.unescape(text)
    # Remove XML / HTML tags
    cleaned = re.sub(r"<[^>]+>", " ", unescaped)
    return clean_text(cleaned)


# =============================================================================
# SOURCE 1: OPENALEX
# =============================================================================

def search_openalex(query: str, limit: int = 15) -> List[Dict[str, Any]]:
    """
    Searches the OpenAlex API for academic works.
    
    Documentation: https://docs.openalex.org/api-entities/works
    """
    papers = []
    url = "https://api.openalex.org/works"
    
    params = {
        "search": query,
        "per_page": min(limit, 50),
    }
    
    # Enter polite pool if email is provided
    email = config.get("OPENALEX_EMAIL")
    if email:
        params["mailto"] = email
        
    try:
        response = requests.get(
            url, 
            params=params, 
            timeout=config.get("API_TIMEOUT", 25),
            headers={"User-Agent": "ResearchGapAI/1.0 (mailto:info@researchgap.ai)"}
        )
        
        if response.status_code != 200:
            logger.warning(f"OpenAlex returned status code {response.status_code}")
            return []
            
        data = response.json()
        results = data.get("results", [])
        
        for item in results:
            title = item.get("title") or item.get("display_name")
            if not title:
                continue
                
            # Extract authors
            authorships = item.get("authorships", [])
            author_names = []
            for a in authorships:
                name = a.get("author", {}).get("display_name")
                if name:
                    author_names.append(name)
            authors_str = ", ".join(author_names)
            
            # Reconstruct abstract
            abstract = reconstruct_openalex_abstract(item.get("abstract_inverted_index"))
            
            # Extract publication date
            pub_date = item.get("publication_date") or str(item.get("publication_year") or "")
            
            # Extract DOI
            raw_doi = item.get("doi") or ""
            doi = normalize_doi(raw_doi)
            
            # Extract URL and PDF URL
            primary_loc = item.get("primary_location") or {}
            open_access = item.get("open_access") or {}
            
            landing_url = raw_doi or primary_loc.get("landing_page_url") or item.get("id") or ""
            pdf_url = open_access.get("oa_url") or primary_loc.get("pdf_url") or ""
            
            paper = {
                "title": clean_text(title),
                "authors": clean_text(authors_str),
                "abstract": abstract,
                "publication_date": pub_date,
                "doi": doi,
                "url": landing_url,
                "pdf_url": pdf_url or "",
                "source": "OpenAlex",
                "relevance_score": 1.0,
                "is_relevant": True,
            }
            papers.append(paper)
            
    except Exception as e:
        logger.error(f"Error querying OpenAlex: {e}")
        
    return papers


# =============================================================================
# SOURCE 2: ARXIV
# =============================================================================

def search_arxiv(query: str, limit: int = 15) -> List[Dict[str, Any]]:
    """
    Searches the arXiv API using its Atom XML feed.
    
    Documentation: https://info.arxiv.org/help/api/user-manual.html
    """
    papers = []
    url = "http://export.arxiv.org/api/query"
    
    # Format query for arXiv: search across all fields (all:...)
    cleaned_query = re.sub(r"[^\w\s]", " ", query).strip()
    formatted_query = f"all:{cleaned_query}"
    
    params = {
        "search_query": formatted_query,
        "start": 0,
        "max_results": min(limit, 50),
        "sortBy": "relevance",
        "sortOrder": "descending",
    }
    
    try:
        response = requests.get(
            url, 
            params=params, 
            timeout=config.get("API_TIMEOUT", 25)
        )
        
        if response.status_code != 200:
            logger.warning(f"arXiv returned status code {response.status_code}")
            return []
            
        root = ET.fromstring(response.text)
        ns = {
            "atom": "http://www.w3.org/2005/Atom",
            "arxiv": "http://arxiv.org/schemas/atom"
        }
        
        for entry in root.findall("atom:entry", ns):
            title_elem = entry.find("atom:title", ns)
            if title_elem is None or not title_elem.text:
                continue
                
            title = title_elem.text.strip().replace("\n", " ")
            
            # Extract summary/abstract
            summary_elem = entry.find("atom:summary", ns)
            abstract = summary_elem.text.strip().replace("\n", " ") if summary_elem is not None and summary_elem.text else ""
            
            # Extract authors
            author_names = []
            for author in entry.findall("atom:author", ns):
                name_elem = author.find("atom:name", ns)
                if name_elem is not None and name_elem.text:
                    author_names.append(name_elem.text.strip())
            authors_str = ", ".join(author_names)
            
            # Publication date (published format: YYYY-MM-DDTHH:MM:SSZ)
            pub_elem = entry.find("atom:published", ns)
            pub_date = pub_elem.text[:10] if pub_elem is not None and pub_elem.text else ""
            
            # DOI if present in arxiv namespace
            doi_elem = entry.find("arxiv:doi", ns)
            doi = normalize_doi(doi_elem.text) if doi_elem is not None and doi_elem.text else ""
            
            # Web URL and PDF URL
            id_elem = entry.find("atom:id", ns)
            landing_url = id_elem.text.strip() if id_elem is not None and id_elem.text else ""
            
            pdf_url = ""
            for link in entry.findall("atom:link", ns):
                if link.get("title") == "pdf" or link.get("type") == "application/pdf":
                    pdf_url = link.get("href", "")
                    break
            
            # If pdf link wasn't explicitly titled, derive it from arxiv id
            if not pdf_url and landing_url:
                pdf_url = landing_url.replace("/abs/", "/pdf/") + ".pdf"
                
            paper = {
                "title": clean_text(title),
                "authors": clean_text(authors_str),
                "abstract": clean_text(abstract),
                "publication_date": pub_date,
                "doi": doi,
                "url": landing_url,
                "pdf_url": pdf_url,
                "source": "arXiv",
                "relevance_score": 1.0,
                "is_relevant": True,
            }
            papers.append(paper)
            
    except Exception as e:
        logger.error(f"Error querying arXiv: {e}")
        
    return papers


# =============================================================================
# SOURCE 3: SEMANTIC SCHOLAR
# =============================================================================

def search_semantic_scholar(query: str, limit: int = 15) -> List[Dict[str, Any]]:
    """
    Searches the Semantic Scholar Academic Graph API.
    
    Documentation: https://api.semanticscholar.org/api-docs/graph
    """
    papers = []
    url = "https://api.semanticscholar.org/graph/v1/paper/search"
    
    params = {
        "query": query,
        "limit": min(limit, 50),
        "fields": "title,authors,abstract,year,publicationDate,externalIds,url,openAccessPdf",
    }
    
    headers = {
        "User-Agent": "ResearchGapAI/1.0 (academic-research-tool; mailto:info@researchgap.ai)"
    }
    
    # Use API key if provided in .env
    api_key = config.get("SEMANTIC_SCHOLAR_API_KEY")
    if api_key:
        headers["x-api-key"] = api_key
        
    try:
        response = requests.get(
            url, 
            params=params, 
            headers=headers, 
            timeout=config.get("API_TIMEOUT", 25)
        )
        
        if response.status_code == 429:
            logger.warning("Semantic Scholar rate limit reached (HTTP 429). Add SEMANTIC_SCHOLAR_API_KEY in .env for higher quota.")
            return []
            
        if response.status_code != 200:
            logger.warning(f"Semantic Scholar returned status code {response.status_code}")
            return []
            
        data = response.json()
        results = data.get("data", [])
        
        for item in results:
            title = item.get("title")
            if not title:
                continue
                
            # Extract authors
            authors = [a.get("name") for a in item.get("authors", []) if a.get("name")]
            authors_str = ", ".join(authors)
            
            # Extract publication date
            pub_date = item.get("publicationDate") or str(item.get("year") or "")
            
            # Extract DOI
            external_ids = item.get("externalIds") or {}
            raw_doi = external_ids.get("DOI") or ""
            doi = normalize_doi(raw_doi)
            
            # Extract PDF and page URL
            open_access_pdf = item.get("openAccessPdf") or {}
            pdf_url = open_access_pdf.get("url") or ""
            landing_url = item.get("url") or (f"https://doi.org/{doi}" if doi else "")
            
            paper = {
                "title": clean_text(title),
                "authors": clean_text(authors_str),
                "abstract": clean_text(item.get("abstract") or ""),
                "publication_date": pub_date,
                "doi": doi,
                "url": landing_url,
                "pdf_url": pdf_url,
                "source": "Semantic Scholar",
                "relevance_score": 1.0,
                "is_relevant": True,
            }
            papers.append(paper)
            
    except Exception as e:
        logger.error(f"Error querying Semantic Scholar: {e}")
        
    return papers


# =============================================================================
# SOURCE 4: CROSSREF
# =============================================================================

def search_crossref(query: str, limit: int = 15) -> List[Dict[str, Any]]:
    """
    Searches Crossref REST API for published academic papers.
    
    Documentation: https://api.crossref.org/swagger-ui/index.html
    """
    papers = []
    url = "https://api.crossref.org/works"
    
    params = {
        "query": query,
        "rows": min(limit, 50),
        "sort": "relevance",
        "order": "desc",
    }
    
    email = config.get("OPENALEX_EMAIL") or "info@researchgap.ai"
    headers = {
        "User-Agent": f"ResearchGapAI/1.0 (mailto:{email})"
    }
    
    try:
        response = requests.get(
            url, 
            params=params, 
            headers=headers, 
            timeout=config.get("API_TIMEOUT", 25)
        )
        
        if response.status_code != 200:
            logger.warning(f"Crossref returned status code {response.status_code}")
            return []
            
        data = response.json()
        items = data.get("message", {}).get("items", [])
        
        for item in items:
            title_list = item.get("title", [])
            if not title_list or not title_list[0]:
                continue
            title = title_list[0]
            
            # Extract authors
            authors = []
            for author in item.get("author", []):
                given = author.get("given", "").strip()
                family = author.get("family", "").strip()
                full_name = f"{given} {family}".strip()
                if full_name:
                    authors.append(full_name)
            authors_str = ", ".join(authors)
            
            # Extract publication date
            pub_date = ""
            created = item.get("created", {}).get("date-time", "")
            if created:
                pub_date = created[:10]
            elif "published-print" in item:
                parts = item["published-print"].get("date-parts", [[]])[0]
                pub_date = "-".join(str(p).zfill(2) for p in parts)
            elif "published-online" in item:
                parts = item["published-online"].get("date-parts", [[]])[0]
                pub_date = "-".join(str(p).zfill(2) for p in parts)
                
            # Extract DOI
            raw_doi = item.get("DOI", "")
            doi = normalize_doi(raw_doi)
            
            # Extract abstract (strip JATS XML markup like <jats:p>)
            raw_abstract = item.get("abstract", "")
            abstract = strip_html_tags(raw_abstract)
            
            # URLs
            landing_url = item.get("URL") or (f"https://doi.org/{doi}" if doi else "")
            
            # PDF Link check in link items
            pdf_url = ""
            for link in item.get("link", []):
                if link.get("content-type") == "application/pdf":
                    pdf_url = link.get("URL", "")
                    break
                    
            paper = {
                "title": clean_text(title),
                "authors": clean_text(authors_str),
                "abstract": abstract,
                "publication_date": pub_date,
                "doi": doi,
                "url": landing_url,
                "pdf_url": pdf_url,
                "source": "Crossref",
                "relevance_score": 1.0,
                "is_relevant": True,
            }
            papers.append(paper)
            
    except Exception as e:
        logger.error(f"Error querying Crossref: {e}")
        
    return papers


# =============================================================================
# MULTI-SOURCE CONCURRENT SEARCH ORCHESTRATOR
# =============================================================================

def search_all_sources(query: str, limit_per_source: int = 15) -> Dict[str, Any]:
    """
    Searches all four academic sources in parallel using ThreadPoolExecutor.
    
    Parameters:
        query: The search query string
        limit_per_source: Max papers to request per source
        
    Returns:
        Dictionary containing:
        - "papers": list of normalized paper dictionaries
        - "counts_by_source": dict with paper count per source
        - "total_found": total number of papers discovered
        - "query": the query used
    """
    logger.info(f"Starting multi-source academic paper search for: '{query}'")
    all_papers: List[Dict[str, Any]] = []
    counts_by_source = {
        "OpenAlex": 0,
        "arXiv": 0,
        "Semantic Scholar": 0,
        "Crossref": 0,
    }
    
    # Map sources to their search functions
    sources = [
        ("OpenAlex", search_openalex),
        ("arXiv", search_arxiv),
        ("Semantic Scholar", search_semantic_scholar),
        ("Crossref", search_crossref),
    ]
    
    # Execute searches concurrently across threads
    with ThreadPoolExecutor(max_workers=4) as executor:
        future_to_source = {
            executor.submit(func, query, limit_per_source): name
            for name, func in sources
        }
        
        for future in as_completed(future_to_source):
            source_name = future_to_source[future]
            try:
                source_papers = future.result()
                counts_by_source[source_name] = len(source_papers)
                all_papers.extend(source_papers)
                logger.info(f"Discovered {len(source_papers)} papers from {source_name}")
            except Exception as e:
                logger.error(f"Failed to fetch papers from {source_name}: {e}")
                counts_by_source[source_name] = 0
                
    logger.info(f"Total papers discovered across all sources: {len(all_papers)}")
    
    return {
        "papers": all_papers,
        "counts_by_source": counts_by_source,
        "total_found": len(all_papers),
        "query": query,
    }
