"""
ResearchGap AI - Paper Filtering & Deduplication Service
=========================================================
Implements clean, understandable algorithms for:
1. Paper Deduplication (DOI matching, normalized title matching, Jaccard similarity)
2. Relevance Scoring (weighted keyword matching across titles and abstracts)
3. Publication Year Filtering
4. Research Domain Filtering
5. Top-K Paper Ranking

Why direct Python without vector databases or embedding models?
- Fast, transparent, and easy to explain.
- No heavy C/C++ dependencies or multi-gigabyte models.
- Predictable: you can see exactly which keywords contributed to the relevance score.
"""

import re
import string
from typing import List, Dict, Any, Tuple, Optional, Set
from utils.text_cleaner import clean_text, normalize_doi, extract_year_from_date


# =============================================================================
# 1. TEXT NORMALIZATION & SIMILARITY HELPERS
# =============================================================================

def normalize_title_for_comparison(title: str) -> str:
    """
    Normalizes a title by lowercasing, stripping punctuation, and collapsing whitespace.
    Used for reliable deduplication comparison across different academic sources.
    
    Example:
        "Federated Learning: A Survey." -> "federated learning a survey"
    """
    if not title:
        return ""
    # Lowercase
    cleaned = title.lower()
    # Replace punctuation with spaces
    cleaned = re.sub(r"[^\w\s]", " ", cleaned)
    # Collapse multiple whitespace characters into a single space
    cleaned = " ".join(cleaned.split())
    return cleaned.strip()


def calculate_jaccard_similarity(text1: str, text2: str) -> float:
    """
    Calculates Jaccard similarity between the unique word sets of two texts.
    Range: 0.0 (no shared words) to 1.0 (identical word sets).
    
    Formula: |words1 ∩ words2| / |words1 ∪ words2|
    """
    words1 = set(normalize_title_for_comparison(text1).split())
    words2 = set(normalize_title_for_comparison(text2).split())
    
    if not words1 or not words2:
        return 0.0
        
    intersection = words1.intersection(words2)
    union = words1.union(words2)
    return len(intersection) / len(union)


def extract_search_terms(text: str) -> Set[str]:
    """
    Extracts meaningful search terms from a string, filtering out short stopwords.
    """
    stopwords = {
        "a", "an", "the", "and", "or", "in", "on", "at", "for", "with",
        "of", "to", "by", "from", "up", "about", "into", "over", "after",
        "is", "are", "was", "were", "be", "been", "being", "have", "has",
        "had", "do", "does", "did", "this", "that", "these", "those"
    }
    
    cleaned = normalize_title_for_comparison(text)
    words = cleaned.split()
    return {w for w in words if len(w) > 2 and w not in stopwords}


# =============================================================================
# 2. DEDUPLICATION ENGINE
# =============================================================================

def is_duplicate(paper1: Dict[str, Any], paper2: Dict[str, Any], similarity_threshold: float = 0.85) -> bool:
    """
    Determines if two papers represent the same publication based on:
    1. Exact DOI match (if DOI is present in both)
    2. Exact normalized title match
    3. High title Jaccard word similarity (>= 85%)
    """
    doi1 = normalize_doi(paper1.get("doi", ""))
    doi2 = normalize_doi(paper2.get("doi", ""))
    
    # 1. Exact DOI match
    if doi1 and doi2 and doi1.lower() == doi2.lower():
        return True
        
    title1 = paper1.get("title", "")
    title2 = paper2.get("title", "")
    
    norm1 = normalize_title_for_comparison(title1)
    norm2 = normalize_title_for_comparison(title2)
    
    if not norm1 or not norm2:
        return False
        
    # 2. Exact normalized title match
    if norm1 == norm2:
        return True
        
    # 3. High Jaccard title similarity
    similarity = calculate_jaccard_similarity(title1, title2)
    if similarity >= similarity_threshold:
        return True
        
    return False


def merge_two_papers(primary: Dict[str, Any], secondary: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merges duplicate records into a single enriched paper:
    - Retains the longest abstract
    - Retains PDF URL if one has it and the other doesn't
    - Combines source names (e.g. 'arXiv, Crossref')
    - Retains DOI if available
    """
    merged = dict(primary)
    
    # Keep the longer abstract
    abs1 = primary.get("abstract", "")
    abs2 = secondary.get("abstract", "")
    if len(abs2) > len(abs1):
        merged["abstract"] = abs2
        
    # Ensure PDF URL is preserved
    if not merged.get("pdf_url") and secondary.get("pdf_url"):
        merged["pdf_url"] = secondary["pdf_url"]
        
    # Ensure DOI is preserved
    if not merged.get("doi") and secondary.get("doi"):
        merged["doi"] = secondary["doi"]
        
    # Ensure URL is preserved
    if not merged.get("url") and secondary.get("url"):
        merged["url"] = secondary["url"]
        
    # Combine sources if different
    src1 = primary.get("source", "")
    src2 = secondary.get("source", "")
    sources = set([s.strip() for s in src1.split(",") if s.strip()])
    sources.add(src2.strip())
    merged["source"] = ", ".join(sorted(sources))
    
    return merged


def remove_duplicate_papers(papers: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], int]:
    """
    Deduplicates a list of papers while preserving ordering.
    
    Returns:
        (unique_papers, duplicates_removed_count)
    """
    unique_papers: List[Dict[str, Any]] = []
    duplicates_count = 0
    
    for paper in papers:
        found_duplicate = False
        for i, existing in enumerate(unique_papers):
            if is_duplicate(paper, existing):
                # Merge the duplicate information into the existing paper
                unique_papers[i] = merge_two_papers(existing, paper)
                duplicates_count += 1
                found_duplicate = True
                break
                
        if not found_duplicate:
            unique_papers.append(paper)
            
    return unique_papers, duplicates_count


# =============================================================================
# 3. RELEVANCE SCORING ENGINE
# =============================================================================

def calculate_paper_relevance(
    paper: Dict[str, Any], 
    topic: str, 
    keywords: str = "", 
    domain: str = ""
) -> float:
    """
    Computes a transparent relevance score from 0.0 to 10.0 based on keyword matching:
    
    Scoring Weights:
    - Topic words in Title: 3.0 points per match
    - Topic words in Abstract: 1.5 points per match
    - User Keywords in Title: 2.0 points per match
    - User Keywords in Abstract: 1.0 points per match
    - Domain words in Title/Abstract: 1.0 point
    - Having a non-empty abstract: +1.0 point bonus
    - Having a PDF link: +0.5 point bonus
    
    The raw score is capped at 10.0 and rounded to 1 decimal place.
    """
    title = paper.get("title", "")
    abstract = paper.get("abstract", "")
    
    title_words = set(normalize_title_for_comparison(title).split())
    abstract_words = set(normalize_title_for_comparison(abstract).split())
    
    topic_terms = extract_search_terms(topic)
    keyword_terms = extract_search_terms(keywords)
    domain_terms = extract_search_terms(domain)
    
    raw_score = 0.0
    
    # 1. Topic matching (highest importance)
    topic_matches_title = len(topic_terms.intersection(title_words))
    topic_matches_abstract = len(topic_terms.intersection(abstract_words))
    raw_score += topic_matches_title * 3.0
    raw_score += topic_matches_abstract * 1.5
    
    # 2. Keywords matching
    if keyword_terms:
        kw_matches_title = len(keyword_terms.intersection(title_words))
        kw_matches_abstract = len(keyword_terms.intersection(abstract_words))
        raw_score += kw_matches_title * 2.0
        raw_score += kw_matches_abstract * 1.0
        
    # 3. Domain matching
    if domain_terms:
        domain_match = bool(domain_terms.intersection(title_words) or domain_terms.intersection(abstract_words))
        if domain_match:
            raw_score += 1.0
            
    # 4. Content bonuses
    if len(abstract) > 50:
        raw_score += 1.0
    if paper.get("pdf_url"):
        raw_score += 0.5
        
    # Scale to 0.0 - 10.0 range
    final_score = min(round(raw_score, 1), 10.0)
    return final_score


# =============================================================================
# 4. PUBLICATION YEAR & DOMAIN FILTERING
# =============================================================================

def filter_by_year(papers: List[Dict[str, Any]], min_year: Optional[int] = None) -> List[Dict[str, Any]]:
    """Filters out papers published prior to min_year."""
    if not min_year:
        return papers
        
    filtered = []
    for paper in papers:
        year_str = extract_year_from_date(paper.get("publication_date", ""))
        if year_str and year_str.isdigit():
            if int(year_str) >= min_year:
                filtered.append(paper)
        else:
            # If publication year is unknown, retain it so we don't accidentally drop valid papers
            filtered.append(paper)
            
    return filtered


# =============================================================================
# 5. UNIFIED FILTERING PIPELINE
# =============================================================================

def filter_and_rank_papers(
    papers: List[Dict[str, Any]],
    topic: str,
    keywords: str = "",
    domain: str = "",
    min_year: Optional[int] = None,
    min_score_threshold: float = 1.0,
    max_papers: int = 30
) -> Dict[str, Any]:
    """
    Orchestrates the complete paper filtering pipeline:
    1. Removes papers with invalid/missing titles
    2. Deduplicates across sources (DOI, title, Jaccard similarity)
    3. Calculates relevance scores for each paper
    4. Applies publication year filtering (if requested)
    5. Flags relevant vs irrelevant papers based on threshold
    6. Sorts by relevance score descending
    7. Limits to max_papers
    
    Returns:
        Dictionary containing:
        - "filtered_papers": list of ranked and scored papers
        - "stats": dictionary of filtering metrics (input_count, duplicates_removed, relevant_count)
    """
    initial_count = len(papers)
    
    # Step 1: Discard invalid items
    valid_papers = [
        p for p in papers 
        if p.get("title") and len(clean_text(p["title"])) >= 5
    ]
    
    # Step 2: Deduplication
    unique_papers, duplicates_removed = remove_duplicate_papers(valid_papers)
    
    # Step 3: Relevance Scoring
    scored_papers = []
    for paper in unique_papers:
        paper_copy = dict(paper)
        score = calculate_paper_relevance(
            paper=paper_copy,
            topic=topic,
            keywords=keywords,
            domain=domain
        )
        paper_copy["relevance_score"] = score
        paper_copy["is_relevant"] = score >= min_score_threshold
        scored_papers.append(paper_copy)
        
    # Step 4: Year filtering (if configured)
    year_filtered = filter_by_year(scored_papers, min_year)
    
    # Step 5: Rank by relevance score descending (highest score first)
    ranked_papers = sorted(
        year_filtered, 
        key=lambda p: (1 if p["is_relevant"] else 0, p["relevance_score"]), 
        reverse=True
    )
    
    # Step 6: Cap at max_papers
    final_papers = ranked_papers[:max_papers]
    relevant_count = sum(1 for p in final_papers if p.get("is_relevant", True))
    
    return {
        "filtered_papers": final_papers,
        "stats": {
            "initial_count": initial_count,
            "duplicates_removed": duplicates_removed,
            "after_dedup_count": len(unique_papers),
            "final_count": len(final_papers),
            "relevant_count": relevant_count,
        }
    }
