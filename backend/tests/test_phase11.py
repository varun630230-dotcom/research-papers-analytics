"""
Phase 11 - AI Research Reviewer Tests
Tests:
- Comprehensive critique prompt construction across all research modules
- Review normalization, schema validation, and score bounding
- 7 critical review dimensions (Consistency, Evidence, Feasibility, Gaps, Assumptions, Weaknesses, Improvements)
- Deterministic heuristic reviewer fallback when GEMINI_API_KEY is unset
- Gemini API error recovery and graceful fallback
- SQLite database persistence of ai_review in research_results
- Full API response structure verification
"""

import sys
import os
from unittest.mock import patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.ai_reviewer import (
    build_review_prompt,
    validate_and_normalize_review,
    generate_deterministic_review,
    review_research_report
)
from services.gemini_client import GeminiError
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
print("  ResearchGap AI - Phase 11 AI Research Reviewer Tests")
print("=" * 60)

mock_results = {
    "synthesis": {
        "summary": "Cross-paper synthesis reveals asynchronous pipelines reduce synchronization stalls in edge nodes.",
        "dominant_methodologies": ["Decoupled Asynchronous Gradient Descent"],
        "frequently_used_algorithms": [{"name": "FedAvg", "frequency": 4}],
        "three_tier_evidence": {
            "tier_1_direct_claims": [{"claim": "Stragglers cause up to 70% idle GPU time.", "supporting_papers": ["Zhang et al. (2024)"]}],
            "tier_2_derived_insights": [{"insight": "Asynchronous updates preserve overall convergence."}],
            "tier_3_open_hypotheses": [{"hypothesis": "Quantized gradients do not accumulate bias."}]
        }
    },
    "research_gaps": [
        {
            "id": "gap-1",
            "title": "Straggler Sensitivity in Non-IID Edge Nodes",
            "gap_type": "scalability",
            "certainty_tier": "Tier 1 - Directly Supported",
            "supporting_papers": ["Zhang et al. (2024)", "Li et al. (2025)"]
        }
    ],
    "tech_limitations": [
        {
            "title": "Synchronous Barrier Bottleneck",
            "limitation_type": "scalability",
            "recommended_alternative": "Lock-free circular parameter buffers"
        }
    ],
    "market_opportunities": [
        {
            "id": "opp-1",
            "title": "Edge Fleet Optimization Framework",
            "target_persona": "Edge AI Engineers",
            "feasibility": "High",
            "evidence_basis": "research_grounded"
        }
    ],
    "novelty_assessment": {
        "potential_novelty_assessment": "The proposed asynchronous pipeline introduces potential novelty based on evaluated literature.",
        "similar_existing_approaches": ["FedAsync (2020)"],
        "differentiating_features": ["Dynamic staleness penalty"],
        "unexplored_combinations": ["LoRA with Asynchronous Ring-AllReduce"]
    },
    "architecture": {
        "proposed_solution": "Decoupled Asynchronous Federated Architecture",
        "system_components": [
            {"name": "Client Worker", "role": "Local training and 8-bit quantization"},
            {"name": "Aggregation Gateway", "role": "Staleness-aware parameter aggregation"}
        ],
        "technology_stack": {"runtime": "PyTorch 2.x", "acceleration": "FlashAttention-2"}
    },
    "roadmap": {
        "total_phases": 8,
        "total_estimated_weeks": 24,
        "phases": [
            {"phase_number": 1, "phase_name": "Problem Formulation & Baselines", "estimated_weeks": 2}
        ]
    }
}

# -------------------------------------------------------------------------
# Test 1: Prompt Construction
# -------------------------------------------------------------------------
prompt = build_review_prompt(
    topic="Asynchronous Edge Federated Learning",
    domain="Distributed Systems",
    results=mock_results
)

test("Prompt includes topic", "Asynchronous Edge Federated Learning" in prompt)
test("Prompt includes domain", "Distributed Systems" in prompt)
test("Prompt includes synthesis summary", "Cross-paper synthesis reveals" in prompt)
test("Prompt includes research gaps summary", "Straggler Sensitivity" in prompt)
test("Prompt includes tech limitations summary", "Synchronous Barrier Bottleneck" in prompt)
test("Prompt includes market opportunities summary", "Edge Fleet Optimization Framework" in prompt)
test("Prompt includes architecture summary", "Decoupled Asynchronous Federated Architecture" in prompt)
test("Prompt includes roadmap summary", "24 weeks" in prompt)
test("Prompt specifies required JSON structure", '"logical_consistency"' in prompt and '"technical_feasibility"' in prompt)

# -------------------------------------------------------------------------
# Test 2: Normalization & Schema Validation
# -------------------------------------------------------------------------
raw_review = {
    "overall_score": 8.8,
    "review_summary": "Strong engineering blueprint with clear evidence backing.",
    "logical_consistency": {
        "rating": "Strong",
        "critique": "The architecture directly mitigates the identified synchronous barrier gap."
    },
    "evidence_quality": {
        "rating": "Strong",
        "critique": "Every gap references empirical papers directly."
    },
    "technical_feasibility": {
        "rating": "High",
        "critique": "Production-ready open source toolchain."
    },
    "missing_research_areas": [
        "Formal differential privacy loss analysis."
    ],
    "unsupported_assumptions": [
        "Zero packet drop on public cellular networks."
    ],
    "weak_recommendations": [
        "Recommendation for CI/CD should name specific test harnesses."
    ],
    "improvement_suggestions": [
        "Include Rényi differential privacy accounting in Phase 3.",
        "Add hardware stress testing on Raspberry Pi 5 clusters."
    ]
}

normalized = validate_and_normalize_review(raw_review, "Edge FL")
test("Normalization preserves overall score", normalized["overall_score"] == 8.8)
test("Normalization preserves logical consistency rating", normalized["logical_consistency"]["rating"] == "Strong")
test("Normalization preserves technical feasibility rating", normalized["technical_feasibility"]["rating"] == "High")
test("Normalization captures missing research areas", len(normalized["missing_research_areas"]) == 1)
test("Normalization captures unsupported assumptions", len(normalized["unsupported_assumptions"]) == 1)
test("Normalization captures weak recommendations", len(normalized["weak_recommendations"]) == 1)
test("Normalization captures improvement suggestions", len(normalized["improvement_suggestions"]) == 2)

# Test score clamping and invalid input handling
clamped_high = validate_and_normalize_review({"overall_score": 15.0}, "Edge FL")
test("Score clamped to maximum 10.0", clamped_high["overall_score"] == 10.0)

clamped_low = validate_and_normalize_review({"overall_score": -2.0}, "Edge FL")
test("Score clamped to minimum 1.0", clamped_low["overall_score"] == 1.0)

empty_input = validate_and_normalize_review(None, "Edge FL")
test("Handles None input gracefully", 1.0 <= empty_input["overall_score"] <= 10.0)
test("Empty input sets default rating blocks", empty_input["logical_consistency"]["rating"] == "Moderate")
test("Empty input initializes list fields", isinstance(empty_input["missing_research_areas"], list))

# -------------------------------------------------------------------------
# Test 3: Deterministic Heuristic Fallback
# -------------------------------------------------------------------------
det_review = generate_deterministic_review(
    topic="Asynchronous Edge Federated Learning",
    domain="Distributed Systems",
    results=mock_results
)

test("Deterministic review returns valid score", 7.0 <= det_review["overall_score"] <= 10.0)
test("Deterministic review sets is_mock flag", det_review.get("is_mock") is True)
test("Deterministic review includes disclaimer notice", "GEMINI_API_KEY" in det_review.get("notice", ""))
test("Deterministic review has logical consistency critique", len(det_review["logical_consistency"]["critique"]) > 20)
test("Deterministic review references top research gap", "Straggler Sensitivity" in det_review["logical_consistency"]["critique"])
test("Deterministic review has evidence quality block", det_review["evidence_quality"]["rating"] in ["Strong", "Moderate"])
test("Deterministic review has technical feasibility block", det_review["technical_feasibility"]["rating"] in ["High", "Moderate"])
test("Deterministic review has multiple missing research areas", len(det_review["missing_research_areas"]) >= 2)
test("Deterministic review has unsupported assumptions", len(det_review["unsupported_assumptions"]) >= 2)
test("Deterministic review has weak recommendations", len(det_review["weak_recommendations"]) >= 1)
test("Deterministic review has actionable improvement suggestions", len(det_review["improvement_suggestions"]) >= 3)

# -------------------------------------------------------------------------
# Test 4: Primary review_research_report with fallback & mock
# -------------------------------------------------------------------------
# Test fallback when API key is empty
from config import config
orig_key = config.get("GEMINI_API_KEY", "")
config["GEMINI_API_KEY"] = ""

fallback_result = review_research_report(
    topic="Asynchronous Edge Federated Learning",
    domain="Distributed Systems",
    results=mock_results
)
test("review_research_report falls back cleanly when key is missing", fallback_result.get("is_mock") is True)

# Test when Gemini returns valid critique
mock_gemini_output = {
    "overall_score": 9.2,
    "review_summary": "Exemplary research blueprint with empirical grounding.",
    "logical_consistency": {"rating": "Strong", "critique": "Clear traceability from gap to architecture."},
    "evidence_quality": {"rating": "Strong", "critique": "Solid citations across all claims."},
    "technical_feasibility": {"rating": "High", "critique": "Toolchain is mature and readily available."},
    "missing_research_areas": ["Privacy leakage under model inversion"],
    "unsupported_assumptions": ["Assumes uniform client compute latency"],
    "weak_recommendations": ["Clarify learning rate schedule"],
    "improvement_suggestions": ["Perform simulated non-IID Dirichlet distribution stress test."]
}

config["GEMINI_API_KEY"] = "mock_key_for_test"
with patch("services.ai_reviewer.call_gemini_json", return_value=mock_gemini_output):
    gemini_result = review_research_report(
        topic="Asynchronous Edge Federated Learning",
        domain="Distributed Systems",
        results=mock_results
    )
    test("review_research_report parses Gemini JSON output", gemini_result["overall_score"] == 9.2)
    test("review_research_report preserves critique details", gemini_result["logical_consistency"]["rating"] == "Strong")
    test("review_research_report has is_mock False/None", gemini_result.get("is_mock") is not True)

# Test exception recovery from GeminiError
with patch("services.ai_reviewer.call_gemini_json", side_effect=GeminiError("API rate limit exceeded")):
    recovered_result = review_research_report(
        topic="Asynchronous Edge Federated Learning",
        domain="Distributed Systems",
        results=mock_results
    )
    test("review_research_report recovers from GeminiError to deterministic fallback", recovered_result.get("is_mock") is True)
    test("Recovered result contains valid score", recovered_result["overall_score"] > 0)

config["GEMINI_API_KEY"] = orig_key

# -------------------------------------------------------------------------
# Test 5: SQLite Database Persistence
# -------------------------------------------------------------------------
project_id = db.create_project(
    topic="AI Reviewer Test Project",
    description="Evaluating automated peer review persistence",
    domain="Computer Science"
)

save_data = {
    **mock_results,
    "ai_review": {
        "overall_score": 8.5,
        "review_summary": "Database test review summary",
        "logical_consistency": {"rating": "Strong", "critique": "Verified alignment."},
        "evidence_quality": {"rating": "Strong", "critique": "Empirically supported."},
        "technical_feasibility": {"rating": "High", "critique": "Feasible stack."},
        "missing_research_areas": ["Missing Area A", "Missing Area B"],
        "unsupported_assumptions": ["Assumption X"],
        "weak_recommendations": ["Weak recommendation Y"],
        "improvement_suggestions": ["Suggestion 1", "Suggestion 2"]
    }
}

db.save_research_results(project_id, save_data)
retrieved = db.get_research_results(project_id)

test("Retrieved results contains ai_review", "ai_review" in retrieved)
test("ai_review overall score persisted", retrieved["ai_review"]["overall_score"] == 8.5)
test("ai_review logical consistency persisted", retrieved["ai_review"]["logical_consistency"]["rating"] == "Strong")
test("ai_review missing research areas persisted", len(retrieved["ai_review"]["missing_research_areas"]) == 2)
test("ai_review improvement suggestions persisted", len(retrieved["ai_review"]["improvement_suggestions"]) == 2)

# Cleanup test project
db.delete_project(project_id)

print("=" * 60)
print(f"  Phase 11 Reviewer Tests: {passed} passed, {failed} failed")
print("=" * 60)

if failed > 0:
    sys.exit(1)
