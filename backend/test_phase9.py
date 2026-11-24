"""
Phase 9 - Opportunity Scoring & Novelty Assessment Tests
Tests:
- Transparent weighted opportunity scoring formula
- Configurable criteria weights (gap, feasibility, novelty, impact, evidence)
- Sorting opportunities by weighted score
- Novelty assessment schema & required scientific phrasing
- SQLite database persistence of opportunity_scores & novelty_assessment
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.scoring_engine import (
    compute_criterion_scores,
    score_single_opportunity,
    score_all_opportunities,
    DEFAULT_WEIGHTS
)
from services.novelty_assessor import (
    build_novelty_prompt,
    validate_and_normalize_novelty,
    generate_deterministic_novelty,
    assess_research_novelty
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
print("  ResearchGap AI - Phase 9 Scoring & Novelty Tests")
print("=" * 60)

mock_opportunity_1 = {
    "title": "Turnkey Acceleration SDK for LLM Tuning",
    "description": "SDK automating parameter-efficient fine-tuning and asynchronous aggregation.",
    "target_users": "Enterprise AI Engineers and ML Teams",
    "existing_problem": "High memory consumption and synchronization stalls.",
    "proposed_solution": "Plug-and-play Python library with native FlashAttention-2.",
    "practical_feasibility": "High",
    "potential_applications": ["Cloud training acceleration", "Cost reduction for inference"],
    "evidence_basis": "research_grounded"
}

mock_opportunity_2 = {
    "title": "Speculative Edge Neuromorphic Gateway",
    "description": "Custom hardware bridge for neuromorphic microcontrollers.",
    "target_users": "IoT developers",
    "existing_problem": "Hardware constraints.",
    "proposed_solution": "Proprietary ASICs.",
    "practical_feasibility": "Low",
    "potential_applications": ["Robotics"],
    "evidence_basis": "extrapolated_assumption"
}

# -----------------------------------------------------------------------------
# 1. Opportunity Criterion Scoring
# -----------------------------------------------------------------------------
print("\n--- 1. Criterion Scoring Calculation ---")
sub1 = compute_criterion_scores(mock_opportunity_1)
sub2 = compute_criterion_scores(mock_opportunity_2)

test("High feasibility receives higher feasibility score than Low", sub1["technical_feasibility"] > sub2["technical_feasibility"])
test("Research grounded receives higher evidence score than extrapolated assumption", sub1["evidence_strength"] > sub2["evidence_strength"])
test("All sub-scores between 1.0 and 10.0", all(1.0 <= v <= 10.0 for v in sub1.values()))

# -----------------------------------------------------------------------------
# 2. Weighted Opportunity Scoring Formula
# -----------------------------------------------------------------------------
print("\n--- 2. Weighted Formula Scoring ---")
scored1 = score_single_opportunity(mock_opportunity_1)
scored2 = score_single_opportunity(mock_opportunity_2)

test("Has weighted_score field", "weighted_score" in scored1)
test("Score 1 is higher than Score 2 (due to High feasibility and research grounding)", scored1["weighted_score"] > scored2["weighted_score"])
test("Weighted score is between 1.0 and 10.0", 1.0 <= scored1["weighted_score"] <= 10.0)
test("Includes human-readable scoring explanation", len(scored1["scoring_explanation"]) > 50)
print(f"    Opp 1 Score: {scored1['weighted_score']}/10.0")
print(f"    Opp 2 Score: {scored2['weighted_score']}/10.0")
print(f"    Explanation: {scored1['scoring_explanation'][:100]}...")

# Test custom weights
custom_weights = {"gap_significance": 0.5, "technical_feasibility": 0.5, "novelty_potential": 0.0, "practical_impact": 0.0, "evidence_strength": 0.0}
scored_custom = score_single_opportunity(mock_opportunity_1, weights=custom_weights)
expected_custom = round(sub1["gap_significance"] * 0.5 + sub1["technical_feasibility"] * 0.5, 2)
test("Custom weights calculated correctly", scored_custom["weighted_score"] == expected_custom)

# Test batch scoring & sorting
ranked = score_all_opportunities([mock_opportunity_2, mock_opportunity_1])
test("Batch scores are sorted descending", ranked[0]["weighted_score"] >= ranked[1]["weighted_score"])

# -----------------------------------------------------------------------------
# 3. Novelty Assessment Prompt & Validation
# -----------------------------------------------------------------------------
print("\n--- 3. Novelty Assessment Schema & Terminology ---")
topic = "Decentralized Federated Learning for Medical IoT"
papers = [{"title": "Paper X", "abstract": "Summary X", "source": "arXiv"}]

novelty_prompt = build_novelty_prompt(topic, "Description", "AI", "Objectives", papers, [])
test("Prompt includes topic", topic in novelty_prompt)
test("Prompt requires scientific terminology", "potential novelty" in novelty_prompt.lower())

mock_raw_novelty = {
    "similarity_to_literature": "Moderate Similarity",
    "similarity_rationale": "Shares distributed architecture with Paper X but focuses on IoT edge nodes.",
    "similar_existing_approaches": [{"approach": "Baseline FedAvg", "cited_paper": "Paper X", "overlap_description": "Client aggregation"}],
    "differentiating_features": ["Ultra-low-power quantization", "Asynchronous gossip protocol"],
    "unexplored_combinations": ["Pairing 4-bit quantization with differential privacy on ARM cortex"],
    "existing_limitations_faced": ["Network disconnects during rounds"],
    "potential_novelty_assessment": "The proposed work demonstrates potential novelty based on evaluated literature."
}

val_novelty = validate_and_normalize_novelty(mock_raw_novelty, topic, len(papers))
test("Novelty contains similarity_to_literature", val_novelty["similarity_to_literature"] == "Moderate Similarity")
test("Contains differentiating features list", len(val_novelty["differentiating_features"]) == 2)
test("Enforces mandatory scientific notice", "potential novelty based on evaluated literature" in val_novelty["verification_notice"].lower())
test("Enforces empirical verification caveat", "empirical baseline verification" in val_novelty["verification_notice"].lower())

# -----------------------------------------------------------------------------
# 4. Deterministic Novelty Assessor Execution
# -----------------------------------------------------------------------------
print("\n--- 4. Deterministic Novelty Assessor ---")
det_novelty = generate_deterministic_novelty(topic, "AI", papers, [])
test("Contains similar_existing_approaches", len(det_novelty["similar_existing_approaches"]) > 0)
test("Contains unexplored_combinations", len(det_novelty["unexplored_combinations"]) > 0)
test("Assessment uses required scientific phrasing", "potential novelty based on evaluated literature" in det_novelty["potential_novelty_assessment"].lower())

# -----------------------------------------------------------------------------
# 5. Database Persistence
# -----------------------------------------------------------------------------
print("\n--- 5. Database Storage & Retrieval ---")
db.initialize_database()

proj_id = db.create_project(topic="Phase 9 Storage Test", domain="AI")
db.save_research_results(proj_id, {
    "opportunity_scores": ranked,
    "novelty_assessment": val_novelty
})

fetched = db.get_research_results(proj_id)
test("Retrieved results from SQLite", fetched is not None)
test("Opportunity scores parsed as list", isinstance(fetched["opportunity_scores"], list) and len(fetched["opportunity_scores"]) == 2)
test("Novelty assessment parsed as dictionary", isinstance(fetched["novelty_assessment"], dict))
test("Novelty notice preserved in DB", "empirical baseline verification" in fetched["novelty_assessment"]["verification_notice"])

# Clean up
db.delete_project(proj_id)
test("Cleaned up test project", db.get_project(proj_id) is None)

# Summary
print("\n" + "=" * 60)
print(f"  Results: {passed} passed, {failed} failed, {passed + failed} total")
print("=" * 60)

if failed > 0:
    sys.exit(1)
else:
    print("  🎉 All Phase 9 Scoring & Novelty tests passed!")
