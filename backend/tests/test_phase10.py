"""
Phase 10 - Architecture Recommendations & 8-Phase Roadmap Tests
Tests:
- Technical architecture schema validation & component topology
- Technology justifications, data flow pipelines, and model recommendations
- 8-phase development roadmap generator (phases 1 to 8)
- Tailored task, deliverable, and timeline calculation
- SQLite database persistence in research_results.architecture and roadmap
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.architecture_generator import (
    build_architecture_prompt,
    validate_and_normalize_architecture,
    generate_deterministic_architecture,
    generate_architecture_recommendation
)
from services.roadmap_generator import (
    build_roadmap_prompt,
    validate_and_normalize_roadmap,
    generate_deterministic_roadmap,
    generate_development_roadmap
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
print("  ResearchGap AI - Phase 10 Architecture & Roadmap Tests")
print("=" * 60)

mock_gaps = [
    {
        "title": "Extreme Memory Footprint in Graph Transformers",
        "gap_type": "scalability",
        "description": "Full attention matrix computation scales quadratically O(N^2) with graph node counts.",
        "evidence": "Paper evaluations cite OOM errors when graph exceeds 50,000 nodes."
    }
]

mock_tech_limitations = [
    {
        "title": "Quadratic Memory Scaling in Dense Attention",
        "suggested_alternatives": "Linear graph attention, neighborhood sampling, and FlashAttention."
    }
]

topic = "Scalable Graph Neural Networks for Molecular Chemistry"
domain = "Computational Chemistry & Deep Learning"

# -----------------------------------------------------------------------------
# 1. Architecture Prompt & Validation
# -----------------------------------------------------------------------------
print("\n--- 1. Architecture Generation & Validation ---")
arch_prompt = build_architecture_prompt(topic, domain, mock_gaps, mock_tech_limitations)
test("Includes topic in architecture prompt", topic in arch_prompt)
test("Includes primary gap in architecture prompt", "Memory Footprint" in arch_prompt)

mock_raw_arch = {
    "target_gap_addressed": "Extreme Memory Footprint in Graph Transformers",
    "problem_statement": "Dense attention consumes excessive memory on large molecular graphs.",
    "proposed_solution": "A sparse neighborhood sampling graph transformer with fused GPU kernels.",
    "system_components": [
        {"name": "Graph Ingestion Layer", "role": "Parses SMILES strings and loads molecular adjacency tensors.", "description": "PyG DataLoader"},
        {"name": "Sparse Attention Engine", "role": "Computes linear-time node attention.", "description": "Triton fused kernels"}
    ],
    "recommended_technologies": [
        {"category": "Graph Framework", "name": "PyTorch Geometric (PyG)", "justification": "Native sparse matrix acceleration on CUDA."}
    ],
    "data_flow": [
        "1. Ingest SMILES molecular strings",
        "2. Generate molecular graph adjacency tensors",
        "3. Execute linear neighborhood attention",
        "4. Output molecular property prediction logits"
    ],
    "model_recommendations": [
        {"model_type": "Sparse Graph Transformer", "architecture": "GraphGPS with 8 sparse attention heads", "loss_function": "Mean Squared Error with L2 Weight Decay"}
    ],
    "implementation_considerations": ["Pre-allocate GPU sparse buffers."],
    "expected_challenges": ["Handling disconnected graph components."]
}

val_arch = validate_and_normalize_architecture(mock_raw_arch, topic, "Extreme Memory Footprint")
test("Target gap preserved", val_arch["target_gap_addressed"] == "Extreme Memory Footprint in Graph Transformers")
test("System components list preserved", len(val_arch["system_components"]) == 2)
test("Recommended technologies present", len(val_arch["recommended_technologies"]) == 1)
test("Data flow steps present", len(val_arch["data_flow"]) == 4)
test("Model recommendations present", len(val_arch["model_recommendations"]) == 1)

det_arch = generate_deterministic_architecture(topic, domain, mock_gaps, mock_tech_limitations)
test("Deterministic architecture has system components", len(det_arch["system_components"]) >= 3)
test("Deterministic architecture has recommended technologies", len(det_arch["recommended_technologies"]) >= 3)
test("Deterministic architecture has data flow", len(det_arch["data_flow"]) >= 4)

# -----------------------------------------------------------------------------
# 2. Roadmap Prompt & Validation
# -----------------------------------------------------------------------------
print("\n--- 2. 8-Phase Development Roadmap Tests ---")
road_prompt = build_roadmap_prompt(topic, domain, val_arch)
test("Prompt includes topic", topic in road_prompt)
test("Prompt requests 8 phases", "8-phase" in road_prompt.lower())

mock_raw_roadmap = {
    "phases": [
        {"phase_number": i, "title": f"Phase {i}: Description", "objective": "Obj", "tasks": ["Task A", "Task B"], "deliverable": "Report", "estimated_weeks": 2}
        for i in range(1, 9)
    ]
}

val_roadmap = validate_and_normalize_roadmap(mock_raw_roadmap, topic)
test("Roadmap contains exactly 8 phases", val_roadmap["total_phases"] == 8)
test("Roadmap computes total estimated weeks", val_roadmap["total_estimated_weeks"] == 16)
test("Phase 1 has tasks list", len(val_roadmap["phases"][0]["tasks"]) == 2)

det_roadmap = generate_deterministic_roadmap(topic, domain, val_arch)
test("Deterministic roadmap has exactly 8 phases", det_roadmap["total_phases"] == 8)
test("Phase 1 is Problem Definition", "problem definition" in det_roadmap["phases"][0]["title"].lower())
test("Phase 2 is Literature Review", "literature review" in det_roadmap["phases"][1]["title"].lower())
test("Phase 3 is Dataset Collection", "dataset" in det_roadmap["phases"][2]["title"].lower())
test("Phase 4 is Data Preprocessing", "preprocessing" in det_roadmap["phases"][3]["title"].lower())
test("Phase 5 is Model/System Development", "development" in det_roadmap["phases"][4]["title"].lower())
test("Phase 6 is Evaluation", "evaluation" in det_roadmap["phases"][5]["title"].lower())
test("Phase 7 is Optimization", "optimization" in det_roadmap["phases"][6]["title"].lower())
test("Phase 8 is Deployment", "deployment" in det_roadmap["phases"][7]["title"].lower())
print(f"    Total Roadmap Duration: {det_roadmap['total_estimated_weeks']} weeks across 8 phases.")

# -----------------------------------------------------------------------------
# 3. Database Persistence
# -----------------------------------------------------------------------------
print("\n--- 3. Database Storage & Retrieval ---")
db.initialize_database()

proj_id = db.create_project(topic="Phase 10 Storage Test", domain="AI")
db.save_research_results(proj_id, {
    "architecture": val_arch,
    "roadmap": val_roadmap
})

fetched = db.get_research_results(proj_id)
test("Retrieved results from SQLite", fetched is not None)
test("Architecture parsed as dictionary", isinstance(fetched["architecture"], dict))
test("Roadmap parsed as dictionary with 8 phases", isinstance(fetched["roadmap"], dict) and len(fetched["roadmap"]["phases"]) == 8)

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
    print("  🎉 All Phase 10 Architecture & Roadmap tests passed!")
