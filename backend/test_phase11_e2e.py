"""
Phase 11 - End-to-End API Integration Test: AI Research Reviewer
Tests the entire discovery -> filter -> PDF -> analysis -> synthesis -> gaps -> tech -> opportunities -> scoring -> novelty -> architecture -> roadmap -> AI review pipeline.
Verifies that POST /research/analyze and GET /research/{id} deliver the complete AI peer review audit.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi.testclient import TestClient
from main import app
import database as db

client = TestClient(app)

print("=" * 60)
print("  ResearchGap AI - Phase 11 End-to-End AI Reviewer Test")
print("=" * 60)

db.initialize_database()

payload = {
    "topic": "Privacy-Preserving Federated Graph Learning",
    "domain": "Distributed Privacy & Graph Machine Learning",
    "keywords": "federated graph learning, differential privacy, graph neural networks, non-IID topologies",
    "objectives": "Design an asynchronous differential privacy framework for cross-silo graph neural network training"
}

print(f"\nSubmitting research topic: '{payload['topic']}'...")
response = client.post("/research/analyze", json=payload)
assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.text}"

data = response.json()
project_id = data["project_id"]
total_found = data["total_papers_found"]
review = data.get("ai_review", {})

print(f"✅ Created project ID: {project_id}")
print(f"✅ Discovered {total_found} papers")
print(f"✅ AI Reviewer Overall Score: {review.get('overall_score')}/10.0")
print(f"✅ Review Summary: {review.get('review_summary', '')[:100]}...")

# Verify GET /research/{project_id}
proj_resp = client.get(f"/research/{project_id}")
assert proj_resp.status_code == 200
results = proj_resp.json().get("results", {})
stored_review = results.get("ai_review", {})

assert stored_review, "Expected ai_review in research results"
assert "logical_consistency" in stored_review
assert "evidence_quality" in stored_review
assert "technical_feasibility" in stored_review
assert "missing_research_areas" in stored_review
assert "unsupported_assumptions" in stored_review
assert "weak_recommendations" in stored_review
assert "improvement_suggestions" in stored_review

print("\nVerifying 7 AI Reviewer Audit Dimensions:")
print(f"  1. Logical Consistency:  [{stored_review['logical_consistency']['rating']}] {stored_review['logical_consistency']['critique'][:70]}...")
print(f"  2. Evidence Quality:     [{stored_review['evidence_quality']['rating']}] {stored_review['evidence_quality']['critique'][:70]}...")
print(f"  3. Technical Feasibility:[{stored_review['technical_feasibility']['rating']}] {stored_review['technical_feasibility']['critique'][:70]}...")
print(f"  4. Missing Areas ({len(stored_review.get('missing_research_areas', []))}):")
for item in stored_review.get("missing_research_areas", [])[:2]:
    print(f"      - {item[:70]}...")
print(f"  5. Unsupported Assumptions ({len(stored_review.get('unsupported_assumptions', []))}):")
for item in stored_review.get("unsupported_assumptions", [])[:2]:
    print(f"      - {item[:70]}...")
print(f"  6. Weak Recommendations ({len(stored_review.get('weak_recommendations', []))}):")
for item in stored_review.get("weak_recommendations", [])[:1]:
    print(f"      - {item[:70]}...")
print(f"  7. Actionable Improvements ({len(stored_review.get('improvement_suggestions', []))}):")
for item in stored_review.get("improvement_suggestions", [])[:2]:
    print(f"      - {item[:70]}...")

print("\n" + "=" * 60)
print("  Phase 11 End-to-End Test PASSED successfully!")
print("=" * 60)
