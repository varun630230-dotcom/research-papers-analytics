"""
Phase 2 - Paper Discovery Service Tests
Verifies search across OpenAlex, arXiv, Semantic Scholar, and Crossref.
Tests abstract reconstruction, XML stripping, schema normalization, and multi-source orchestration.
"""

import sys
import os

# Add backend directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.paper_search import (
    reconstruct_openalex_abstract,
    strip_html_tags,
    search_openalex,
    search_arxiv,
    search_semantic_scholar,
    search_crossref,
    search_all_sources
)

passed = 0
failed = 0

def test(name, condition, detail=""):
    global passed, failed
    if condition:
        print(f"  ✅ {name}")
        passed += 1
    else:
        print(f"  ❌ {name} - {detail}")
        failed += 1

print("=" * 60)
print("  ResearchGap AI - Phase 2 Paper Discovery Tests")
print("=" * 60)

# -----------------------------------------------------------------------------
# Unit Test 1: OpenAlex Inverted Index Reconstruction
# -----------------------------------------------------------------------------
print("\n--- Unit Test: OpenAlex Abstract Inverted Index Reconstructor ---")
mock_inverted_index = {
    "Federated": [0],
    "learning": [1, 5],
    "enables": [2],
    "collaborative": [3],
    "machine": [4],
    "without": [6],
    "sharing": [7],
    "raw": [8],
    "data.": [9]
}
reconstructed = reconstruct_openalex_abstract(mock_inverted_index)
expected = "Federated learning enables collaborative machine learning without sharing raw data."
test("Reconstructs word positions accurately", reconstructed == expected, f"Got: '{reconstructed}'")
test("Handles empty or null inverted index gracefully", reconstruct_openalex_abstract(None) == "")
test("Handles invalid dictionary structures gracefully", reconstruct_openalex_abstract({}) == "")

# -----------------------------------------------------------------------------
# Unit Test 2: Crossref JATS Tag / HTML Tag Stripping
# -----------------------------------------------------------------------------
print("\n--- Unit Test: HTML / JATS Tag Stripping ---")
raw_jats = "<jats:title>Abstract</jats:title><jats:p>This study investigates &amp; analyzes <jats:italic>differential privacy</jats:italic> in healthcare.</jats:p>"
cleaned = strip_html_tags(raw_jats)
test("Strips tags cleanly", "<jats" not in cleaned and "</jats" not in cleaned)
test("Unescapes HTML entities (&amp; -> &)", "&" in cleaned and "&amp;" not in cleaned)
test("Handles empty string", strip_html_tags("") == "")

# -----------------------------------------------------------------------------
# Integration Test: OpenAlex API
# -----------------------------------------------------------------------------
print("\n--- Integration: OpenAlex API Search ---")
openalex_results = search_openalex("federated learning healthcare", limit=3)
test("OpenAlex returned papers", len(openalex_results) > 0, f"Found {len(openalex_results)}")
if openalex_results:
    p = openalex_results[0]
    test("Has valid title", len(p["title"]) > 0)
    test("Source is OpenAlex", p["source"] == "OpenAlex")
    test("Has standardized schema keys", all(k in p for k in ["title", "authors", "abstract", "doi", "url", "pdf_url", "publication_date"]))
    print(f"    Sample OpenAlex: '{p['title'][:60]}...' ({p['publication_date']})")

# -----------------------------------------------------------------------------
# Integration Test: arXiv API
# -----------------------------------------------------------------------------
print("\n--- Integration: arXiv API Search ---")
arxiv_results = search_arxiv("federated learning healthcare", limit=3)
test("arXiv returned papers", len(arxiv_results) > 0, f"Found {len(arxiv_results)}")
if arxiv_results:
    p = arxiv_results[0]
    test("Has valid title", len(p["title"]) > 0)
    test("Source is arXiv", p["source"] == "arXiv")
    test("Has PDF URL", "pdf" in p["pdf_url"].lower())
    test("Has standardized schema keys", all(k in p for k in ["title", "authors", "abstract", "doi", "url", "pdf_url", "publication_date"]))
    print(f"    Sample arXiv: '{p['title'][:60]}...' ({p['publication_date']})")

# -----------------------------------------------------------------------------
# Integration Test: Semantic Scholar API (Resilience Test)
# -----------------------------------------------------------------------------
print("\n--- Integration: Semantic Scholar API Search ---")
ss_results = search_semantic_scholar("federated learning healthcare", limit=2)
# Notice: Semantic Scholar might return 429 if unauthenticated, but it MUST NOT crash
test("Semantic Scholar returned a list (even if empty due to rate limit)", isinstance(ss_results, list))
if ss_results:
    test("Source is Semantic Scholar", ss_results[0]["source"] == "Semantic Scholar")
    print(f"    Sample Semantic Scholar: '{ss_results[0]['title'][:60]}...'")
else:
    print("    Semantic Scholar: Handled gracefully (rate limit / unauthenticated quota)")

# -----------------------------------------------------------------------------
# Integration Test: Crossref API
# -----------------------------------------------------------------------------
print("\n--- Integration: Crossref API Search ---")
crossref_results = search_crossref("federated learning healthcare", limit=3)
test("Crossref returned papers", len(crossref_results) > 0, f"Found {len(crossref_results)}")
if crossref_results:
    p = crossref_results[0]
    test("Has valid title", len(p["title"]) > 0)
    test("Source is Crossref", p["source"] == "Crossref")
    test("Has DOI", len(p["doi"]) > 0)
    test("Has standardized schema keys", all(k in p for k in ["title", "authors", "abstract", "doi", "url", "pdf_url", "publication_date"]))
    print(f"    Sample Crossref: '{p['title'][:60]}...' (DOI: {p['doi']})")

# -----------------------------------------------------------------------------
# Integration Test: Multi-Source Concurrent Orchestrator
# -----------------------------------------------------------------------------
print("\n--- Integration: Multi-Source Concurrent Search Orchestrator ---")
search_summary = search_all_sources("federated learning healthcare privacy", limit_per_source=3)
test("Orchestrator returned results dict", isinstance(search_summary, dict))
test("Contains 'papers' list", "papers" in search_summary and len(search_summary["papers"]) > 0)
test("Contains 'counts_by_source'", "counts_by_source" in search_summary)
print(f"    Total papers discovered: {search_summary['total_found']}")
for src, count in search_summary["counts_by_source"].items():
    print(f"    - {src}: {count} papers")

# Summary
print("\n" + "=" * 60)
print(f"  Results: {passed} passed, {failed} failed, {passed + failed} total")
print("=" * 60)

if failed > 0:
    sys.exit(1)
else:
    print("  🎉 All Phase 2 Paper Discovery tests passed!")
