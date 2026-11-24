"""
Phase 5 - Individual Paper Analysis Service Tests
Tests:
- Prompt generation with strict schema instructions
- Validation and sanitization across all 10 research dimensions
- Deterministic heuristic analysis when GEMINI_API_KEY is not configured
- Live or mocked Gemini response parsing
- Database persistence of paper analyses linked to project and paper records
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.paper_analyzer import (
    build_analysis_prompt,
    validate_and_normalize_analysis,
    generate_deterministic_analysis,
    analyze_paper,
    analyze_project_papers
)
import database as db

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
print("  ResearchGap AI - Phase 5 Paper Analysis Tests")
print("=" * 60)

# Sample test paper
sample_paper = {
    "id": 101,
    "title": "FedProx: Federated Optimization in Heterogeneous Networks",
    "authors": "Tian Li, Anit Kumar Sahu, Manzil Zaheer, Sanjiv Kumar",
    "publication_date": "2020-05-15",
    "source": "arXiv",
    "abstract": (
        "Federated learning faces challenges of systems and statistical heterogeneity. "
        "We introduce FedProx, a generalization of FedAvg that adds a proximal term to local subproblems. "
        "We evaluate FedProx on synthetic data and real-world benchmark datasets including MNIST and Shakespeare, "
        "implemented using PyTorch and CUDA. We observe improved convergence stability under high device heterogeneity."
    ),
    "pdf_text": "",
    "doi": "10.48550/arXiv.1812.06127"
}

# -----------------------------------------------------------------------------
# 1. Prompt Construction
# -----------------------------------------------------------------------------
print("\n--- 1. Prompt Construction ---")
prompt = build_analysis_prompt(sample_paper)
test("Includes paper title", sample_paper["title"] in prompt)
test("Includes abstract content", "FedProx" in prompt)
test("Requests all 10 JSON output keys", all(
    k in prompt for k in [
        "research_problem", "research_objectives", "methodology", "algorithms",
        "technologies", "datasets", "experimental_findings", "limitations",
        "future_work", "contributions"
    ]
))

# -----------------------------------------------------------------------------
# 2. Validation & Normalization
# -----------------------------------------------------------------------------
print("\n--- 2. Output Validation & Sanitization ---")
mock_raw_ai_output = {
    "research_problem": "Addressing system and data heterogeneity in distributed FL.",
    "research_objectives": "Improve stability across non-IID clients", # passed as string instead of list!
    "methodology": "Added proximal regularization term to local client loss functions.",
    "algorithms": ["FedProx", "FedAvg", "SGD"],
    "technologies": ["PyTorch", "CUDA"],
    "datasets": ["MNIST", "Shakespeare"],
    "experimental_findings": ["Achieved 22% better convergence stability."],
    "limitations": ["Requires tuning proximal hyperparameter mu."],
    "future_work": ["Adaptive proximal term tuning."],
    "contributions": ["Proposed FedProx framework.", "Theoretical convergence guarantees."]
}

normalized = validate_and_normalize_analysis(mock_raw_ai_output, sample_paper)
test("Contains paper title", normalized["paper_title"] == sample_paper["title"])
test("Converts single string objective to list", isinstance(normalized["research_objectives"], list))
test("Contains algorithms list", len(normalized["algorithms"]) == 3)
test("Contains datasets list", len(normalized["datasets"]) == 2)
test("Contains limitations list", len(normalized["limitations"]) == 1)
test("Contains contributions list", len(normalized["contributions"]) == 2)

# Test with empty/null input
empty_normalized = validate_and_normalize_analysis({}, sample_paper)
test("Handles empty dictionary without crashing", isinstance(empty_normalized, dict))
test("Populates default fallback problem", "Not explicitly stated" in empty_normalized["research_problem"])
test("Ensures empty lists for omitted dimensions", empty_normalized["algorithms"] == [])

# -----------------------------------------------------------------------------
# 3. Deterministic Extraction (Offline Fallback)
# -----------------------------------------------------------------------------
print("\n--- 3. Deterministic Offline Heuristic Analysis ---")
det_analysis = generate_deterministic_analysis(sample_paper)
test("Detects algorithms mentioned in text (FedAvg, PyTorch/etc)", any("fedavg" in a.lower() for a in det_analysis["algorithms"]))
test("Detects technologies mentioned in text (PyTorch, CUDA)", any("pytorch" in t.lower() or "cuda" in t.lower() for t in det_analysis["technologies"]))
test("Detects datasets mentioned in text (MNIST)", any("mnist" in d.lower() for d in det_analysis["datasets"]))
test("Has 10 structured dimensions", all(
    k in det_analysis for k in [
        "research_problem", "research_objectives", "methodology", "algorithms",
        "technologies", "datasets", "experimental_findings", "limitations",
        "future_work", "contributions"
    ]
))

# -----------------------------------------------------------------------------
# 4. Single Paper Analysis Function
# -----------------------------------------------------------------------------
print("\n--- 4. analyze_paper Function Execution ---")
analysis_result = analyze_paper(sample_paper)
test("Returned analysis dictionary", isinstance(analysis_result, dict))
test("Analysis contains analysis_mode tag", "analysis_mode" in analysis_result)
test("Analysis has problem description", len(analysis_result["research_problem"]) > 0)
test("Analysis has limitations", len(analysis_result["limitations"]) > 0)
print(f"    Mode: {analysis_result['analysis_mode']}")
print(f"    Problem: {analysis_result['research_problem'][:70]}...")
print(f"    Algorithms: {analysis_result['algorithms']}")
print(f"    Limitations: {analysis_result['limitations']}")

# -----------------------------------------------------------------------------
# 5. Database Persistence
# -----------------------------------------------------------------------------
print("\n--- 5. Database Storage & Retrieval ---")
db.initialize_database()

# Create dummy project and paper
proj_id = db.create_project(topic="FedProx Testing", domain="ML")
paper_id_list = db.save_papers(proj_id, [sample_paper])
db_papers = db.get_papers(proj_id)
saved_paper_id = db_papers[0]["id"]

# Save analysis to DB
db.save_paper_analysis(
    paper_id=saved_paper_id,
    project_id=proj_id,
    analysis_data=analysis_result
)

# Retrieve from DB
stored_analyses = db.get_paper_analyses(proj_id)
test("Retrieved 1 analysis from SQLite", len(stored_analyses) == 1)
if stored_analyses:
    stored = stored_analyses[0]
    test("Analysis data matches paper title", stored["analysis_data"]["paper_title"] == sample_paper["title"])
    test("Analysis data parsed from JSON into dict", isinstance(stored["analysis_data"], dict))
    test("Algorithms present in retrieved analysis", len(stored["analysis_data"]["algorithms"]) > 0)

# Clean up
db.delete_project(proj_id)
test("Deleted test project and cascading analyses", db.get_project(proj_id) is None)

# Summary
print("\n" + "=" * 60)
print(f"  Results: {passed} passed, {failed} failed, {passed + failed} total")
print("=" * 60)

if failed > 0:
    sys.exit(1)
else:
    print("  🎉 All Phase 5 Paper Analysis tests passed!")
