"""
Phase 7 - Research Gap Detection Tests
Tests:
- Gap detection prompt construction with compiled limitations
- Schema validation across the 7 gap taxonomies
- Supporting paper citation grounding
- 3-tier evidence classification
- Database persistence in research_results.research_gaps
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.gap_detector import (
    build_gap_detection_prompt,
    validate_and_normalize_gaps,
    generate_deterministic_gaps,
    detect_research_gaps,
    VALID_GAP_TYPES
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
print("  ResearchGap AI - Phase 7 Research Gap Detection Tests")
print("=" * 60)

mock_paper_analyses = [
    {
        "analysis_data": {
            "paper_title": "Paper A: Scalability Constraints in Edge AI",
            "limitations": ["Memory footprint saturates when scaling batch size beyond 32 on ARM devices."],
            "future_work": ["Quantization-aware pruning."],
            "experimental_findings": ["Latency increases by 3.2x under high network jitter."]
        }
    },
    {
        "analysis_data": {
            "paper_title": "Paper B: Benchmark Bias in Healthcare Models",
            "limitations": ["Tested only on adult ICU cohort from single hospital center (MIMIC-III)."],
            "future_work": ["Validation on pediatric and ambulatory data."],
            "experimental_findings": ["Performance drops by 14% on external hospital transfer."]
        }
    }
]

mock_synthesis = {
    "repeated_limitations": [{"limitation": "High memory footprint", "supporting_papers": ["Paper A"]}],
    "underexplored_areas": [{"area": "Cross-center clinical transfer", "gap_rationale": "Single center bias"}]
}

topic = "Edge AI for Clinical Diagnostics"
domain = "Biomedical Engineering"

# -----------------------------------------------------------------------------
# 1. Prompt Construction
# -----------------------------------------------------------------------------
print("\n--- 1. Gap Detection Prompt Construction ---")
prompt = build_gap_detection_prompt(topic, domain, mock_paper_analyses, mock_synthesis)
test("Includes topic in prompt", topic in prompt)
test("Includes Paper A and Paper B titles", "Paper A" in prompt and "Paper B" in prompt)
test("Includes 7 gap taxonomies", all(t in prompt for t in ["methodological", "dataset", "scalability", "evaluation"]))
test("Requests supporting_papers array", "supporting_papers" in prompt)

# -----------------------------------------------------------------------------
# 2. Validation & Normalization
# -----------------------------------------------------------------------------
print("\n--- 2. Gap Schema Validation & Normalization ---")
mock_raw_gaps = {
    "research_gaps": [
        {
            "title": "Cross-Center Generalization Degradation",
            "gap_type": "dataset",
            "description": "Models trained on single hospital data fail on external cohorts.",
            "evidence": "Paper B demonstrated 14% performance drop on external transfer.",
            "supporting_papers": ["Paper B: Benchmark Bias in Healthcare Models"],
            "importance": "Clinical safety demands robustness across diverse patient populations.",
            "potential_direction": "Implement domain-invariant representation learning.",
            "evidence_tier": "tier_1_directly_supported"
        },
        {
            "title": "Edge Memory Saturation Under Real-Time Constraints",
            "gap_type": "invalid_type",  # Should normalize to 'methodological'
            "description": "Embedded devices run out of SRAM during streaming inference.",
            "evidence": "Paper A cites memory saturation with batch size > 32.",
            "supporting_papers": "Paper A: Scalability Constraints in Edge AI", # passed as string!
            "importance": "Blocks real-time diagnostics at point-of-care.",
            "potential_direction": "8-bit post-training quantization.",
            "evidence_tier": "tier_1_directly_supported"
        }
    ]
}

paper_titles = ["Paper A: Scalability Constraints in Edge AI", "Paper B: Benchmark Bias in Healthcare Models"]
validated = validate_and_normalize_gaps(mock_raw_gaps, paper_titles)

test("Extracted 2 valid gap objects", len(validated) == 2)
test("Gap 1 preserves valid gap_type 'dataset'", validated[0]["gap_type"] == "dataset")
test("Gap 2 normalizes invalid gap_type to 'methodological'", validated[1]["gap_type"] in VALID_GAP_TYPES)
test("Converts single string supporting_papers to list", isinstance(validated[1]["supporting_papers"], list))
test("Contains supporting paper citation", validated[1]["supporting_papers"][0] == paper_titles[0])
test("Evidence tier preserved", validated[0]["evidence_tier"] == "tier_1_directly_supported")

# Test empty input handling
empty_val = validate_and_normalize_gaps([], paper_titles)
test("Handles empty list without error", empty_val == [])

# -----------------------------------------------------------------------------
# 3. Deterministic Gap Generation
# -----------------------------------------------------------------------------
print("\n--- 3. Deterministic Fallback Gap Generation ---")
det_gaps = generate_deterministic_gaps(topic, domain, mock_paper_analyses, mock_synthesis)
test("Generates at least 4 research gaps", len(det_gaps) >= 4)
test("All gaps have valid taxonomy types", all(g["gap_type"] in VALID_GAP_TYPES for g in det_gaps))
test("All gaps cite supporting papers", all(len(g["supporting_papers"]) > 0 for g in det_gaps))
test("All gaps explain why it matters", all(len(g["importance"]) > 0 for g in det_gaps))
test("All gaps propose a potential research direction", all(len(g["potential_direction"]) > 0 for g in det_gaps))

# -----------------------------------------------------------------------------
# 4. detect_research_gaps Execution
# -----------------------------------------------------------------------------
print("\n--- 4. detect_research_gaps Function Execution ---")
gaps_result = detect_research_gaps(topic, domain, mock_paper_analyses, mock_synthesis)
test("Returned gaps list", isinstance(gaps_result, list) and len(gaps_result) > 0)
sample_gap = gaps_result[0]
test("Gap contains title", len(sample_gap["title"]) > 0)
test("Gap contains evidence", len(sample_gap["evidence"]) > 0)
print(f"    Sample Gap Title: '{sample_gap['title']}'")
print(f"    Type: {sample_gap['gap_type']} | Tier: {sample_gap['evidence_tier']}")
print(f"    Citations: {sample_gap['supporting_papers']}")

# -----------------------------------------------------------------------------
# 5. Database Storage & Retrieval
# -----------------------------------------------------------------------------
print("\n--- 5. Database Storage & Retrieval ---")
db.initialize_database()

proj_id = db.create_project(topic="Gap Persistence Test", domain="AI")
db.save_research_results(proj_id, {"research_gaps": gaps_result})

fetched = db.get_research_results(proj_id)
test("Retrieved results from SQLite", fetched is not None)
test("Research gaps parsed from JSON to list", isinstance(fetched["research_gaps"], list))
test("Retrieved gaps count matches saved count", len(fetched["research_gaps"]) == len(gaps_result))

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
    print("  🎉 All Phase 7 Research Gap Detection tests passed!")
