"""
Phase 6 - Multi-Paper Evidence Synthesis Tests
Tests:
- Synthesis prompt generation with compiled paper analyses
- Structured validation & normalization of multi-paper synthesis
- 3-tier claim classification (Directly Supported, Cross-Paper Derived, Open Hypotheses)
- Algorithm & dataset frequency aggregation
- Database persistence in research_results table
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.evidence_synthesizer import (
    build_synthesis_prompt,
    validate_synthesis_output,
    generate_deterministic_synthesis,
    synthesize_multi_paper_evidence
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
print("  ResearchGap AI - Phase 6 Evidence Synthesis Tests")
print("=" * 60)

mock_paper_analyses = [
    {
        "analysis_data": {
            "paper_title": "Paper 1: FedAvg under Non-IID Medical Scenarios",
            "research_problem": "Communication bottleneck and high weight divergence in federated optimization.",
            "methodology": "Simulated non-IID client partitions on distributed cluster.",
            "algorithms": ["FedAvg", "SGD"],
            "technologies": ["PyTorch", "CUDA"],
            "datasets": ["MIMIC-III", "MNIST"],
            "experimental_findings": ["Weight divergence increases by 45% when Dirichlet alpha < 0.1."],
            "limitations": ["Significant bandwidth requirement for parameter synchronization."],
            "future_work": ["Gradient compression techniques."],
            "contributions": ["Demonstrated divergence behavior on medical records."]
        }
    },
    {
        "analysis_data": {
            "paper_title": "Paper 2: FedProx for Heterogeneous Edge Clients",
            "research_problem": "System dropouts and client stragglers in heterogeneous networks.",
            "methodology": "Proximal regularization added to client objectives.",
            "algorithms": ["FedProx", "FedAvg", "AdamW"],
            "technologies": ["PyTorch", "Docker"],
            "datasets": ["MIMIC-III", "Shakespeare"],
            "experimental_findings": ["Proximal term stabilizes accuracy by 18% on stragglers."],
            "limitations": ["Proximal term mu requires manual tuning and degrades convergence speed."],
            "future_work": ["Adaptive mu estimation."],
            "contributions": ["Introduced FedProx algorithm with convergence bounds."]
        }
    },
    {
        "analysis_data": {
            "paper_title": "Paper 3: Differential Privacy in Cross-Silo Healthcare",
            "research_problem": "Privacy leakage through model inversion and gradient reconstruction attacks.",
            "methodology": "Gaussian noise perturbation added to gradient aggregation.",
            "algorithms": ["DP-SGD", "FedAvg"],
            "technologies": ["PyTorch", "Opacus"],
            "datasets": ["eICU", "MIMIC-III"],
            "experimental_findings": ["Epsilon=2.0 guarantees privacy but drops AUC by 4.2%."],
            "limitations": ["Severe privacy-utility trade-off on minority patient cohorts."],
            "future_work": ["Client-adaptive clipping thresholds."],
            "contributions": ["Rigorous privacy accounting on multi-hospital cohorts."]
        }
    }
]

topic = "Federated Learning for Healthcare Privacy & Heterogeneity"
domain = "Machine Learning"

# -----------------------------------------------------------------------------
# 1. Prompt Construction
# -----------------------------------------------------------------------------
print("\n--- 1. Synthesis Prompt Construction ---")
prompt = build_synthesis_prompt(topic, domain, mock_paper_analyses)
test("Includes topic in prompt", topic in prompt)
test("Includes all 3 paper titles", all(p["analysis_data"]["paper_title"] in prompt for p in mock_paper_analyses))
test("Requests evidence_tiers", "evidence_tiers" in prompt)
test("Requests repeated_limitations", "repeated_limitations" in prompt)
test("Requests conflicting_findings", "conflicting_findings" in prompt)

# -----------------------------------------------------------------------------
# 2. Validation & Normalization
# -----------------------------------------------------------------------------
print("\n--- 2. Synthesis Output Validation ---")
mock_raw_synthesis = {
    "summary": "Summary of 3 papers.",
    "common_approaches": ["Distributed optimization", "Noise perturbation"],
    "frequently_used_algorithms": [{"name": "FedAvg", "papers": ["Paper 1", "Paper 2", "Paper 3"]}],
    "frequently_used_technologies": [{"name": "PyTorch", "papers": ["Paper 1", "Paper 2", "Paper 3"]}],
    "common_datasets": [{"name": "MIMIC-III", "papers": ["Paper 1", "Paper 2", "Paper 3"]}],
    "repeated_limitations": [{"limitation": "High communication overhead", "supporting_papers": ["Paper 1", "Paper 2"]}],
    "conflicting_findings": [],
    "underexplored_areas": [{"area": "Adaptive privacy budgets under non-IID data"}],
    "technological_trends": ["Transition toward parameter-efficient federated tuning"],
    "evidence_tiers": {
        "tier_1_directly_supported": [{"claim": "Epsilon=2 drops AUC by 4.2%", "supporting_papers": ["Paper 3"]}],
        "tier_2_cross_paper_derived": [{"insight": "Both FedAvg and FedProx struggle with communication costs", "synthesized_from": ["Paper 1", "Paper 2"]}],
        "tier_3_open_hypotheses": [{"hypothesis": "Dynamic compression will resolve communication bottlenecks", "grounding": "Paper 1"}]
    }
}
validated = validate_synthesis_output(mock_raw_synthesis, topic)
test("Summary is preserved", validated["summary"] == mock_raw_synthesis["summary"])
test("Contains common_approaches list", len(validated["common_approaches"]) == 2)
test("Contains evidence_tiers dict", isinstance(validated["evidence_tiers"], dict))
test("Tier 1 present", len(validated["evidence_tiers"]["tier_1_directly_supported"]) == 1)
test("Tier 2 present", len(validated["evidence_tiers"]["tier_2_cross_paper_derived"]) == 1)
test("Tier 3 present", len(validated["evidence_tiers"]["tier_3_open_hypotheses"]) == 1)

# Test with empty/null input
empty_val = validate_synthesis_output({}, topic)
test("Handles empty dictionary without error", isinstance(empty_val, dict))
test("Populates default summary", topic in empty_val["summary"])
test("Empty tiers initialized as lists", isinstance(empty_val["evidence_tiers"]["tier_1_directly_supported"], list))

# -----------------------------------------------------------------------------
# 3. Deterministic Heuristic Synthesis
# -----------------------------------------------------------------------------
print("\n--- 3. Deterministic Heuristic Synthesis ---")
det_synthesis = generate_deterministic_synthesis(topic, domain, mock_paper_analyses)

test("FedAvg correctly identified as top frequent algorithm (count=3)", det_synthesis["frequently_used_algorithms"][0]["name"] == "FedAvg" and det_synthesis["frequently_used_algorithms"][0]["frequency"] == 3)
test("PyTorch correctly identified as top frequent technology (count=3)", det_synthesis["frequently_used_technologies"][0]["name"] == "PyTorch")
test("MIMIC-III correctly identified as top frequent dataset (count=3)", det_synthesis["common_datasets"][0]["name"] == "MIMIC-III")
test("Repeated limitations generated with citations", len(det_synthesis["repeated_limitations"]) > 0)
test("Tier 1 contains directly supported claims", len(det_synthesis["evidence_tiers"]["tier_1_directly_supported"]) > 0)
test("Tier 2 contains cross-paper derived insights", len(det_synthesis["evidence_tiers"]["tier_2_cross_paper_derived"]) > 0)
test("Tier 3 contains grounded open hypotheses", len(det_synthesis["evidence_tiers"]["tier_3_open_hypotheses"]) > 0)

# -----------------------------------------------------------------------------
# 4. synthesize_multi_paper_evidence Function
# -----------------------------------------------------------------------------
print("\n--- 4. Primary Synthesis Function Execution ---")
syn_result = synthesize_multi_paper_evidence(topic, domain, mock_paper_analyses)
test("Returned synthesis dictionary", isinstance(syn_result, dict))
test("Contains synthesis_mode tag", "synthesis_mode" in syn_result)
test("Contains underexplored_areas", len(syn_result["underexplored_areas"]) > 0)
test("Contains technological_trends", len(syn_result["technological_trends"]) > 0)
print(f"    Mode: {syn_result['synthesis_mode']}")
print(f"    Summary: {syn_result['summary'][:90]}...")
print(f"    Top Algorithm: {syn_result['frequently_used_algorithms'][0]['name']}")
print(f"    Top Dataset: {syn_result['common_datasets'][0]['name']}")

# -----------------------------------------------------------------------------
# 5. Database Persistence
# -----------------------------------------------------------------------------
print("\n--- 5. Database Storage & Retrieval ---")
db.initialize_database()

proj_id = db.create_project(topic="Synthesis Storage Test", domain="ML")
db.save_research_results(proj_id, {"synthesis": syn_result})

fetched_results = db.get_research_results(proj_id)
test("Retrieved results from SQLite", fetched_results is not None)
test("Synthesis parsed from JSON to dictionary", isinstance(fetched_results["synthesis"], dict))
test("Evidence tiers accessible in retrieved synthesis", "evidence_tiers" in fetched_results["synthesis"])

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
    print("  🎉 All Phase 6 Evidence Synthesis tests passed!")
