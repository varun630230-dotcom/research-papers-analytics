"""
Phase 12 & 13 - Complete Dashboard & Export Integration Tests
Tests:
- Static assets serving (index.html, style.css, app.js)
- HTML UI contains all 11 modular research sections
- Complete JSON dossier export containing all pipeline artifacts
- Comprehensive Academic Markdown report containing all 10 analysis sections
- Scientific literature caveat notice and peer review audit in markdown export
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi.testclient import TestClient
from main import app
import database as db

client = TestClient(app)

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
print("  ResearchGap AI - Phase 12 & 13 Dashboard & Export Tests")
print("=" * 60)

db.initialize_database()

# -------------------------------------------------------------------------
# Test 1: Frontend Static Assets Serving
# -------------------------------------------------------------------------
resp_home = client.get("/")
test("GET / returns 200 OK", resp_home.status_code == 200)
test("GET / serves HTML with ResearchGap AI title", "ResearchGap AI" in resp_home.text)

# Verify all 11 navigation sections exist in HTML
sections = [
    "section-input",
    "section-dashboard",
    "section-papers",
    "section-synthesis",
    "section-gaps",
    "section-technology",
    "section-opportunities",
    "section-novelty",
    "section-architecture",
    "section-review",
    "section-export"
]

for sec in sections:
    test(f"HTML contains '{sec}'", f'id="{sec}"' in resp_home.text)

# Verify static CSS and JS
resp_css = client.get("/static/style.css")
test("GET /static/style.css returns 200 OK", resp_css.status_code == 200)
test("CSS contains design tokens and badge classes", "--primary" in resp_css.text and ".tier-badge" in resp_css.text)

resp_js = client.get("/static/app.js")
test("GET /static/app.js returns 200 OK", resp_js.status_code == 200)
test("JS contains all update functions", (
    "updateSynthesis" in resp_js.text and 
    "updateGapsList" in resp_js.text and
    "updateArchitectureAndRoadmap" in resp_js.text and
    "updateAIReview" in resp_js.text
))

# -------------------------------------------------------------------------
# Test 2: Seed Full Research Project for Export
# -------------------------------------------------------------------------
proj_id = db.create_project(
    topic="Asynchronous Spiking Neural Networks for Edge Robotics",
    description="Ultra-low power event-driven motor control using neuromorphic hardware",
    domain="Neuromorphic Computing & Robotics",
    keywords="spiking neural networks, event-based vision, neuromorphic, edge robotics",
    objectives="Design an asynchronous neuromorphic control loop achieving sub-millisecond response"
)

# Seed papers
mock_papers = [
    {
        "title": "Neuromorphic Vision for High-Speed Robotic Grasping",
        "authors": "Chen et al.",
        "abstract": "We evaluate event cameras for ultra-low latency robotic feedback.",
        "publication_date": "2024-03-15",
        "doi": "10.1145/3600001",
        "url": "https://example.com/paper1",
        "pdf_url": "https://example.com/paper1.pdf",
        "source": "arXiv",
        "relevance_score": 9.4,
        "is_relevant": 1,
        "pdf_text": "Extracted full text of paper 1 evaluating event-based camera pipelines and spike coding."
    },
    {
        "title": "Energy-Efficient Spiking Graph Transformers on Edge FPGA",
        "authors": "Vasquez et al.",
        "abstract": "FPGA deployment of spiking graph transformer layers.",
        "publication_date": "2024-08-20",
        "doi": "10.1109/TNNLS.2024.12345",
        "url": "https://example.com/paper2",
        "pdf_url": "https://example.com/paper2.pdf",
        "source": "OpenAlex",
        "relevance_score": 9.1,
        "is_relevant": 1,
        "pdf_text": "Detailed measurements showing 85% energy reduction compared to standard GPU baselines."
    }
]

db.save_papers(proj_id, mock_papers)

# Seed full results dictionary across all phases
full_results = {
    "synthesis": {
        "summary": "Neuromorphic architectures provide 10x lower latency for robotics but suffer from non-differentiable surrogate gradients.",
        "dominant_methodologies": ["Spike-Timing-Dependent Plasticity", "Surrogate Gradient Learning"],
        "frequently_used_algorithms": [{"name": "LIF Neuron", "frequency": 5}],
        "frequently_used_datasets": [{"name": "DVS-Gesture", "frequency": 4}],
        "three_tier_evidence": {
            "tier_1_direct_claims": [
                {"claim": "Event cameras eliminate motion blur at 10,000 fps.", "supporting_papers": ["Chen et al."]}
            ],
            "tier_2_derived_insights": [
                {"insight": "Surrogate gradient approximations converge reliably for shallow networks."}
            ],
            "tier_3_open_hypotheses": [
                {"hypothesis": "Recurrent SNNs can maintain working memory across multi-second robotic tasks."}
            ]
        }
    },
    "research_gaps": [
        {
            "id": "gap-1",
            "title": "Surrogate Gradient Vanishing in Deep SNNs",
            "gap_type": "methodological",
            "certainty_tier": "Tier 1 - Directly Supported",
            "description": "Surrogate derivatives decay exponentially across timesteps.",
            "evidence": "Observed gradient norms collapse below 1e-6 after 20 timesteps.",
            "importance": "Prevents training deep architectures required for robotic perception.",
            "supporting_papers": ["Chen et al.", "Vasquez et al."],
            "recommended_directions": ["Temporal residual connections", "Direct spike error backpropagation"]
        }
    ],
    "tech_limitations": [
        {
            "title": "Fixed Point Quantization Error on Edge Neuromorphic Chips",
            "limitation_type": "hardware",
            "severity": "Critical",
            "description": "On-chip memory restricts synaptic weights to 4-bit integers.",
            "recommended_alternative": "Quantization-Aware Spike Training (QAST) with stochastic rounding."
        }
    ],
    "market_opportunities": [
        {
            "id": "opp-1",
            "title": "Sub-Watt Neuromorphic Drone Autopilot Controller",
            "target_persona": "Autonomous Drone Manufacturers",
            "existing_problem": "Standard micro-controllers consume too much power for obstacle avoidance.",
            "proposed_solution": "Deploy quantized SNN model onto ultra-low power neuromorphic co-processor.",
            "feasibility": "High",
            "evidence_basis": "research_grounded"
        }
    ],
    "opportunity_scores": [
        {
            "opportunity_id": "opp-1",
            "opportunity_title": "Sub-Watt Neuromorphic Drone Autopilot Controller",
            "weighted_score": 8.7,
            "breakdown": {
                "gap_significance": 9.0,
                "technical_feasibility": 8.5,
                "novelty_potential": 8.8,
                "practical_impact": 8.5,
                "evidence_strength": 8.7
            },
            "explanation": "High practical demand in robotic perception combined with strong empirical citations."
        }
    ],
    "novelty_assessment": {
        "potential_novelty_assessment": "The proposed asynchronous spike framework exhibits potential novelty based on evaluated literature.",
        "notice": "Potential novelty based on evaluated literature — requires further empirical baseline verification.",
        "differentiating_features": [
            "Decoupled event-camera sensor stream",
            "Direct membrane potential residual feedback"
        ],
        "similar_existing_approaches": [
            "Spiking ResNet (2022)",
            "Event-based E2VID (2020)"
        ],
        "unexplored_combinations": [
            "State Space Models (Mamba) coupled with Leaky Integrate-and-Fire neurons"
        ]
    },
    "architecture": {
        "proposed_solution": "Event-Driven Asynchronous Neuromorphic Robot Controller",
        "target_gap_addressed": "Surrogate Gradient Vanishing in Deep SNNs",
        "system_components": [
            {
                "name": "Event Stream Accumulator",
                "layer": "Perception Layer",
                "role": "Converts DVS events into temporal spike tensors",
                "technology_justification": "C++ libcaer with zero-copy ring buffers"
            },
            {
                "name": "Spike Inference Engine",
                "layer": "Compute Layer",
                "role": "Executes quantized LIF layers in sub-millisecond intervals",
                "technology_justification": "ONNX Runtime with TensorRT Neuromorphic plugin"
            }
        ],
        "data_flow_pipeline": [
            {"step_number": 1, "step_name": "Event Ingestion", "description": "Microsecond timestamped polarity events collected."},
            {"step_number": 2, "step_name": "Spike Inference", "description": "Forward pass through Leaky Integrate-and-Fire layers."}
        ]
    },
    "roadmap": {
        "total_phases": 8,
        "total_estimated_weeks": 26,
        "phases": [
            {
                "phase_number": 1,
                "phase_name": "Problem Definition & Baselines",
                "estimated_weeks": 3,
                "tasks": ["Literature benchmark collection", "Baseline simulation in PyTorch"],
                "deliverables": ["Baseline latency benchmark report"]
            },
            {
                "phase_number": 2,
                "phase_name": "Hardware In-the-Loop Testbed",
                "estimated_weeks": 4,
                "tasks": ["FPGA bitstream generation", "Event camera calibration"],
                "deliverables": ["Working physical testbed"]
            }
        ]
    },
    "ai_review": {
        "overall_score": 8.6,
        "review_summary": "Thorough methodology with clear engineering execution and empirical paper grounding.",
        "logical_consistency": {
            "rating": "Strong",
            "critique": "The event accumulator and spike inference engine directly address the sub-millisecond requirement."
        },
        "evidence_quality": {
            "rating": "Strong",
            "critique": "Direct paper citations support the 85% energy reduction and latency metrics."
        },
        "technical_feasibility": {
            "rating": "High",
            "critique": "libcaer and ONNX Runtime are battle-tested and production viable."
        },
        "missing_research_areas": [
            "Thermal throttling under continuous high-frequency event bursts.",
            "Sensor degradation in low-light environments."
        ],
        "unsupported_assumptions": [
            "Assuming robotic motor response latency is negligible compared to perception compute."
        ],
        "weak_recommendations": [
            "Recommendation to 'profile FPGA power' should state exact measurement instrumentation."
        ],
        "improvement_suggestions": [
            "Incorporate a physical optical shutter test to measure worst-case latency under illumination transitions.",
            "Benchmark against an optimized INT8 TensorRT conventional CNN baseline."
        ]
    }
}

db.save_research_results(proj_id, full_results)

# -------------------------------------------------------------------------
# Test 3: Verify JSON Export Endpoint
# -------------------------------------------------------------------------
json_export_resp = client.get(f"/export/{proj_id}/json")
test("GET /export/{id}/json returns 200 OK", json_export_resp.status_code == 200)
test("JSON export has attachment Content-Disposition", "attachment" in json_export_resp.headers.get("Content-Disposition", ""))

export_payload = json_export_resp.json()
test("JSON export contains export_info", export_payload.get("export_info", {}).get("platform") == "ResearchGap AI")
test("JSON export contains project metadata", export_payload.get("project", {}).get("topic") == "Asynchronous Spiking Neural Networks for Edge Robotics")
test("JSON export contains papers array", len(export_payload.get("papers", [])) == 2)
test("JSON export contains synthesis", "synthesis" in export_payload.get("results", {}))
test("JSON export contains research_gaps", len(export_payload["results"]["research_gaps"]) == 1)
test("JSON export contains tech_limitations", len(export_payload["results"]["tech_limitations"]) == 1)
test("JSON export contains market_opportunities", len(export_payload["results"]["market_opportunities"]) == 1)
test("JSON export contains opportunity_scores", len(export_payload["results"]["opportunity_scores"]) == 1)
test("JSON export contains novelty_assessment", "potential_novelty_assessment" in export_payload["results"]["novelty_assessment"])
test("JSON export contains architecture", len(export_payload["results"]["architecture"]["system_components"]) == 2)
test("JSON export contains roadmap", len(export_payload["results"]["roadmap"]["phases"]) == 2)
test("JSON export contains ai_review", export_payload["results"]["ai_review"]["overall_score"] == 8.6)

# -------------------------------------------------------------------------
# Test 4: Verify Markdown Export Endpoint
# -------------------------------------------------------------------------
md_export_resp = client.get(f"/export/{proj_id}/markdown")
test("GET /export/{id}/markdown returns 200 OK", md_export_resp.status_code == 200)
test("Markdown export has text/markdown media type", "text/markdown" in md_export_resp.headers.get("Content-Type", ""))
test("Markdown export has attachment header", "attachment" in md_export_resp.headers.get("Content-Disposition", ""))

md_text = md_export_resp.text
test("Markdown contains Title & Platform", "# Research Intelligence Report: Asynchronous Spiking Neural Networks" in md_text and "ResearchGap AI" in md_text)
test("Markdown contains Section 1: Context & Objectives", "## 1. Research Context & Objectives" in md_text)
test("Markdown contains Section 2: Evidence Synthesis", "## 2. Multi-Paper Evidence Synthesis" in md_text)
test("Markdown contains 3-tier evidence classification", "Tier 1: Directly Supported Empirical Claims" in md_text)
test("Markdown contains Section 3: Discovered Academic Literature", "## 3. Discovered Academic Literature" in md_text)
test("Markdown contains paper details and DOI", "10.1145/3600001" in md_text)
test("Markdown contains Section 4: Research Gaps", "## 4. Identified Research Gaps" in md_text and "Surrogate Gradient Vanishing" in md_text)
test("Markdown contains Section 5: Technological Limitations", "## 5. Technological Limitations" in md_text and "Fixed Point Quantization Error" in md_text)
test("Markdown contains Section 6: Market Opportunities & Scoring", "## 6. Grounded Market Opportunities" in md_text and "8.7/10.0" in md_text)
test("Markdown contains Section 7: Novelty Assessment & Notice", "## 7. Novelty Assessment" in md_text and "Potential novelty based on evaluated literature" in md_text)
test("Markdown contains Section 8: Technical Architecture Recommendations", "## 8. Technical Architecture Recommendations" in md_text and "Event Stream Accumulator" in md_text)
test("Markdown contains Section 9: 8-Phase Development Roadmap", "## 9. 8-Phase Development Roadmap" in md_text and "26 Weeks" in md_text)
test("Markdown contains Section 10: Autonomous AI Research Reviewer & Audit", "## 10. Autonomous AI Research Reviewer & Critical Audit" in md_text and "8.6/10.0" in md_text)
test("Markdown contains AI Review audit dimensions and suggestions", "Logical Consistency" in md_text and "Thermal throttling" in md_text)

# Cleanup
db.delete_project(proj_id)

print("=" * 60)
print(f"  Phase 12 & 13 Tests: {passed} passed, {failed} failed")
print("=" * 60)

if failed > 0:
    sys.exit(1)
