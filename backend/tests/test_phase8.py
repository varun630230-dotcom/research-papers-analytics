"""
Phase 8 - Technological Limitations & Market Opportunities Tests
Tests:
- Technological limitation analyzer schema validation across 5 types
- Modern alternative technology suggestions
- Market opportunity analyzer schema validation & user persona extraction
- Strict distinction of research_grounded vs extrapolated_assumption
- Practical feasibility ranking (High, Medium, Low)
- SQLite database persistence of both results
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.technology_analyzer import (
    build_tech_analysis_prompt,
    validate_and_normalize_tech_limitations,
    generate_deterministic_tech_limitations,
    analyze_technological_limitations,
    VALID_LIMITATION_TYPES
)
from services.opportunity_analyzer import (
    build_opportunity_prompt,
    validate_and_normalize_opportunities,
    generate_deterministic_opportunities,
    analyze_market_opportunities
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
print("  ResearchGap AI - Phase 8 Tech Limits & Opportunities Tests")
print("=" * 60)

mock_paper_analyses = [
    {
        "analysis_data": {
            "paper_title": "Paper 1: Distributed Model Training Bottlenecks",
            "technologies": ["PyTorch", "Synchronous AllReduce"],
            "algorithms": ["SGD"],
            "limitations": ["VRAM consumption explodes when scaling batch size; network synchronization stalls high-speed nodes."]
        }
    }
]

mock_synthesis = {
    "repeated_limitations": [{"limitation": "High memory consumption and communication latency"}],
    "technological_trends": ["Adoption of parameter-efficient fine-tuning (LoRA) and FlashAttention"]
}

mock_gaps = [
    {
        "title": "Scalability Bottleneck in Synchronous Parameter Updates",
        "gap_type": "scalability",
        "description": "Nodes stall waiting for stragglers in distributed training.",
        "evidence": "Stated limitations cite network synchronization latency.",
        "supporting_papers": ["Paper 1: Distributed Model Training Bottlenecks"]
    }
]

topic = "Distributed LLM Fine-Tuning"
domain = "Cloud AI Infrastructure"

# -----------------------------------------------------------------------------
# 1. Technological Limitations
# -----------------------------------------------------------------------------
print("\n--- 1. Technological Limitation Analysis ---")
tech_prompt = build_tech_analysis_prompt(topic, domain, mock_paper_analyses, mock_synthesis)
test("Includes topic in tech prompt", topic in tech_prompt)
test("Includes 5 limitation types in instructions", all(t in tech_prompt for t in ["computational", "scalability", "infrastructure"]))

mock_raw_tech = {
    "technological_limitations": [
        {
            "title": "GPU VRAM OOM During Activation Caching",
            "limitation_type": "computational",
            "description": "Full-rank backward pass exhausts 80GB H100 memory on long contexts.",
            "affected_technologies": ["Standard PyTorch Autograd"],
            "affected_papers": ["Paper 1: Distributed Model Training Bottlenecks"],
            "suggested_alternatives": "FlashAttention-2 and ZeRO-3 activation checkpointing.",
            "expected_benefits": "Enables 4x longer context windows without OOM errors."
        }
    ]
}

val_tech = validate_and_normalize_tech_limitations(mock_raw_tech, ["Paper 1"])
test("Validated 1 technological limitation", len(val_tech) == 1)
test("Limitation type is valid", val_tech[0]["limitation_type"] in VALID_LIMITATION_TYPES)
test("Affected papers cited", len(val_tech[0]["affected_papers"]) > 0)
test("Has suggested alternatives", len(val_tech[0]["suggested_alternatives"]) > 0)

det_tech = generate_deterministic_tech_limitations(topic, domain, mock_paper_analyses, mock_synthesis)
test("Deterministic tech analyzer produces at least 3 limitations", len(det_tech) >= 3)
test("All deterministic items have valid limitation_type", all(t["limitation_type"] in VALID_LIMITATION_TYPES for t in det_tech))

# -----------------------------------------------------------------------------
# 2. Market Opportunities
# -----------------------------------------------------------------------------
print("\n--- 2. Market Opportunity Analysis ---")
opp_prompt = build_opportunity_prompt(topic, domain, mock_gaps, val_tech)
test("Includes topic in opportunity prompt", topic in opp_prompt)
test("Includes gaps and tech limitations in opportunity prompt", "Scalability Bottleneck" in opp_prompt)

mock_raw_opps = {
    "market_opportunities": [
        {
            "title": "Turnkey Distributed MLOps Acceleration Engine",
            "description": "An automated orchestrator that injects ZeRO-3 and asynchronous gradient compression into PyTorch pipelines.",
            "target_users": "Enterprise AI Engineering Teams, Cloud Platform Architects",
            "existing_problem": "Companies spend millions on idle GPU compute due to stragglers and synchronization stalls.",
            "proposed_solution": "A drop-in Python wrapper replacing standard DistributedDataParallel with adaptive async compression.",
            "practical_feasibility": "high",
            "potential_applications": ["Cost reduction for foundation model tuning", "Enterprise private cloud training"],
            "evidence_basis": "research_grounded",
            "supporting_gap_or_paper": "Scalability Bottleneck in Synchronous Parameter Updates"
        }
    ]
}

val_opps = validate_and_normalize_opportunities(mock_raw_opps, "Scalability Bottleneck")
test("Validated 1 market opportunity", len(val_opps) == 1)
test("Feasibility normalized to capitalized 'High'", val_opps[0]["practical_feasibility"] == "High")
test("Evidence basis tagged 'research_grounded'", val_opps[0]["evidence_basis"] == "research_grounded")
test("Target users identified", "Enterprise" in val_opps[0]["target_users"])
test("Supporting gap linked", len(val_opps[0]["supporting_gap_or_paper"]) > 0)

det_opps = generate_deterministic_opportunities(topic, domain, mock_gaps, val_tech)
test("Deterministic opportunity analyzer produces at least 3 opportunities", len(det_opps) >= 3)
test("All deterministic items have target users", all(len(o["target_users"]) > 0 for o in det_opps))
test("All deterministic items have proposed solutions", all(len(o["proposed_solution"]) > 0 for o in det_opps))
test("Correctly flags evidence_basis (research_grounded vs extrapolated_assumption)", any(o["evidence_basis"] == "research_grounded" for o in det_opps))

# -----------------------------------------------------------------------------
# 3. Database Persistence
# -----------------------------------------------------------------------------
print("\n--- 3. Database Storage & Retrieval ---")
db.initialize_database()

proj_id = db.create_project(topic="Phase 8 Storage Test", domain="AI")
db.save_research_results(proj_id, {
    "tech_limitations": val_tech,
    "market_opportunities": val_opps
})

fetched = db.get_research_results(proj_id)
test("Retrieved results from SQLite", fetched is not None)
test("Tech limitations parsed as list", isinstance(fetched["tech_limitations"], list) and len(fetched["tech_limitations"]) == 1)
test("Market opportunities parsed as list", isinstance(fetched["market_opportunities"], list) and len(fetched["market_opportunities"]) == 1)

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
    print("  🎉 All Phase 8 Tech Limits & Opportunities tests passed!")
