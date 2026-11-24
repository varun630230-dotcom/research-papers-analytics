"""
Phase 3 - Paper Filtering, Deduplication & Relevance Scoring Tests
Tests:
- Title normalization & Jaccard similarity
- Exact DOI duplicate detection
- Title-based duplicate detection & paper merging
- Transparent keyword-based relevance scoring
- Year & completeness filtering
- End-to-end pipeline integration
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.paper_filter import (
    normalize_title_for_comparison,
    calculate_jaccard_similarity,
    is_duplicate,
    merge_two_papers,
    remove_duplicate_papers,
    calculate_paper_relevance,
    filter_by_year,
    filter_and_rank_papers
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
print("  ResearchGap AI - Phase 3 Filtering & Deduplication Tests")
print("=" * 60)

# -----------------------------------------------------------------------------
# 1. Title Normalization & Jaccard Similarity
# -----------------------------------------------------------------------------
print("\n--- 1. Title Normalization & Jaccard Similarity ---")
raw_title = "  Federated Learning: A Survey on Privacy-Preserving ML!!  "
normalized = normalize_title_for_comparison(raw_title)
expected = "federated learning a survey on privacy preserving ml"
test("Normalizes punctuation and whitespace", normalized == expected, f"Got '{normalized}'")

sim_identical = calculate_jaccard_similarity("Federated Learning Survey", "federated learning survey")
test("Identical titles have similarity 1.0", sim_identical == 1.0)

sim_similar = calculate_jaccard_similarity(
    "Federated Learning in Healthcare: A Comprehensive Survey",
    "A Comprehensive Survey of Federated Learning in Healthcare"
)
test("Reordered titles have high similarity (>0.85)", sim_similar >= 0.85, f"Similarity: {sim_similar}")

sim_different = calculate_jaccard_similarity("Quantum Computing Principles", "Federated Learning Survey")
test("Completely different titles have similarity 0.0", sim_different == 0.0)

# -----------------------------------------------------------------------------
# 2. Duplicate Detection
# -----------------------------------------------------------------------------
print("\n--- 2. Duplicate Detection ---")
# Case A: Same DOI, different titles
p_doi1 = {"title": "Paper One", "doi": "10.1000/182"}
p_doi2 = {"title": "Paper One (Revised)", "doi": "https://doi.org/10.1000/182"}
test("Detects duplicate via normalized DOI", is_duplicate(p_doi1, p_doi2))

# Case B: No DOI, identical normalized titles
p_title1 = {"title": "Deep Learning for Healthcare Systems.", "doi": ""}
p_title2 = {"title": "deep learning for healthcare systems", "doi": ""}
test("Detects duplicate via normalized title", is_duplicate(p_title1, p_title2))

# Case C: Distinct papers
p_distinct = {"title": "Reinforcement Learning in Robotics", "doi": "10.1000/999"}
test("Does not flag distinct papers as duplicate", not is_duplicate(p_title1, p_distinct))

# -----------------------------------------------------------------------------
# 3. Paper Merging
# -----------------------------------------------------------------------------
print("\n--- 3. Paper Merging ---")
p_short_abstract = {
    "title": "Federated Learning Survey",
    "abstract": "Short abstract.",
    "source": "arXiv",
    "pdf_url": "https://arxiv.org/pdf/123.pdf",
    "doi": ""
}
p_long_abstract = {
    "title": "Federated Learning Survey",
    "abstract": "This is a much longer and more detailed abstract that describes the full paper findings.",
    "source": "Crossref",
    "pdf_url": "",
    "doi": "10.1016/j.survey.2024"
}
merged = merge_two_papers(p_short_abstract, p_long_abstract)
test("Retains the longer abstract", merged["abstract"] == p_long_abstract["abstract"])
test("Retains PDF link from the one that had it", merged["pdf_url"] == p_short_abstract["pdf_url"])
test("Retains DOI from the one that had it", merged["doi"] == p_long_abstract["doi"])
test("Combines sources (arXiv, Crossref)", "arXiv" in merged["source"] and "Crossref" in merged["source"])

# -----------------------------------------------------------------------------
# 4. Deduplication of Paper List
# -----------------------------------------------------------------------------
print("\n--- 4. Deduplicate Paper List ---")
sample_papers = [
    {"title": "Paper A", "doi": "10.1/a", "abstract": "A", "source": "arXiv"},
    {"title": "Paper B", "doi": "10.1/b", "abstract": "B", "source": "OpenAlex"},
    {"title": "Paper A (Duplicate)", "doi": "10.1/a", "abstract": "Longer A", "source": "Crossref"}, # Duplicate of 0
    {"title": "Paper C", "doi": "", "abstract": "C", "source": "arXiv"},
    {"title": "Paper C.", "doi": "", "abstract": "C2", "source": "Semantic Scholar"}, # Duplicate of 3
]
unique, dup_count = remove_duplicate_papers(sample_papers)
test("Detected 2 duplicates in list of 5", dup_count == 2, f"Got {dup_count}")
test("Unique count is 3", len(unique) == 3, f"Got {len(unique)}")

# -----------------------------------------------------------------------------
# 5. Relevance Scoring
# -----------------------------------------------------------------------------
print("\n--- 5. Keyword Relevance Scoring ---")
topic = "Federated learning for healthcare data privacy"
keywords = "differential privacy, electronic health records"
domain = "Machine Learning"

relevant_paper = {
    "title": "Federated Learning with Differential Privacy for Healthcare Records",
    "abstract": "We evaluate federated learning on distributed electronic health records with privacy guarantees.",
    "pdf_url": "https://arxiv.org/pdf/1.pdf"
}
irrelevant_paper = {
    "title": "Quantum chromodynamics at finite temperature",
    "abstract": "We study phase transitions in strongly coupled quark-gluon plasma.",
    "pdf_url": ""
}

score_rel = calculate_paper_relevance(relevant_paper, topic, keywords, domain)
score_irrel = calculate_paper_relevance(irrelevant_paper, topic, keywords, domain)

test("Relevant paper receives high score (>5.0)", score_rel >= 5.0, f"Score: {score_rel}")
test("Irrelevant paper receives low score (<2.0)", score_irrel < 2.0, f"Score: {score_irrel}")
test("Relevant paper score significantly exceeds irrelevant", score_rel > score_irrel + 3.0)

# -----------------------------------------------------------------------------
# 6. Year Filtering
# -----------------------------------------------------------------------------
print("\n--- 6. Year Filtering ---")
papers_with_dates = [
    {"title": "Recent Paper 2024", "publication_date": "2024-05-10"},
    {"title": "Old Paper 2015", "publication_date": "2015-01-01"},
    {"title": "Undated Paper", "publication_date": ""}
]
filtered_years = filter_by_year(papers_with_dates, min_year=2020)
test("Retains 2024 paper", any(p["title"] == "Recent Paper 2024" for p in filtered_years))
test("Removes 2015 paper", not any(p["title"] == "Old Paper 2015" for p in filtered_years))
test("Retains undated paper (conservative fallback)", any(p["title"] == "Undated Paper" for p in filtered_years))

# -----------------------------------------------------------------------------
# 7. Complete Pipeline Integration
# -----------------------------------------------------------------------------
print("\n--- 7. Complete Filter & Rank Pipeline ---")
raw_batch = [
    relevant_paper,
    irrelevant_paper,
    # Duplicate of relevant paper
    {"title": "Federated Learning with Differential Privacy for Healthcare Records.", "abstract": "Short", "pdf_url": ""},
    {"title": "Valid Machine Learning Medical Study", "abstract": "Healthcare privacy using machine learning models.", "pdf_url": ""}
]

pipeline_output = filter_and_rank_papers(
    papers=raw_batch,
    topic=topic,
    keywords=keywords,
    domain=domain,
    max_papers=10
)

filtered = pipeline_output["filtered_papers"]
stats = pipeline_output["stats"]

test("Pipeline removed duplicate", stats["duplicates_removed"] == 1)
test("Top ranked paper is the most relevant", filtered[0]["title"] == relevant_paper["title"])
test("Papers are ordered by relevance score descending", filtered[0]["relevance_score"] >= filtered[-1]["relevance_score"])

# Summary
print("\n" + "=" * 60)
print(f"  Results: {passed} passed, {failed} failed, {passed + failed} total")
print("=" * 60)

if failed > 0:
    sys.exit(1)
else:
    print("  🎉 All Phase 3 Filtering & Deduplication tests passed!")
