"""
Phase 9 - End-to-End API Integration Test
Tests the full discovery -> filter -> PDF -> analysis -> synthesis -> gaps -> tech -> opportunities -> scoring -> novelty pipeline.
Verifies that GET /research/{id} delivers opportunity scores and novelty assessment.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi.testclient import TestClient
from main import app
import database as db

client = TestClient(app)

print("=" * 60)
print("  ResearchGap AI - Phase 9 End-to-End API Test")
print("=" * 60)

db.initialize_database()

payload = {
    "topic": "Zero-Knowledge Proofs for Private Machine Learning Inference",
    "domain": "Applied Cryptography & Privacy",
    "keywords": "zk-SNARKs, zk-STARKs, verifiable computing, private inference, homomorphic encryption",
    "objectives": "Analyze proof generation latency and circuit complexity barriers in verifiable neural network inference"
}

print(f"\nSubmitting topic: '{payload['topic']}'...")
response = client.post("/research/analyze", json=payload)
assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.text}"

data = response.json()
project_id = data["project_id"]
total_found = data["total_papers_found"]
scores = data.get("opportunity_scores", [])
novelty = data.get("novelty_assessment", {})

print(f"✅ Created project ID: {project_id}")
print(f"✅ Discovered {total_found} papers")
print(f"✅ Computed {len(scores)} opportunity scores")
print(f"✅ Evaluated novelty (Similarity: {novelty.get('similarity_to_literature')})")

# Verify GET /research/{project_id}
proj_resp = client.get(f"/research/{project_id}")
assert proj_resp.status_code == 200
results = proj_resp.json().get("results", {})
stored_scores = results.get("opportunity_scores", [])
stored_novelty = results.get("novelty_assessment", {})

assert len(stored_scores) > 0, "Expected stored opportunity scores"
assert stored_novelty, "Expected stored novelty assessment"

print("\nVerifying Weighted Opportunity Scores:")
for i, s in enumerate(stored_scores[:2], 1):
    print(f"\n[{i}] {s['opportunity_title']}")
    print(f"    Weighted Score: {s['weighted_score']}/10.0")
    print(f"    Gap Significance: {s['gap_significance']} | Feasibility: {s['technical_feasibility']}")
    print(f"    Novelty: {s['novelty_potential']} | Impact: {s['practical_impact']} | Evidence: {s['evidence_strength']}")
    print(f"    Explanation: {s['scoring_explanation'][:90]}...")
    assert 1.0 <= s["weighted_score"] <= 10.0

print("\nVerifying Novelty Assessment:")
print(f"  - Similarity to Literature: {stored_novelty['similarity_to_literature']}")
print(f"  - Similar Approaches Identified: {len(stored_novelty.get('similar_existing_approaches', []))}")
print(f"  - Differentiating Features: {len(stored_novelty.get('differentiating_features', []))}")
print(f"  - Unexplored Combinations: {len(stored_novelty.get('unexplored_combinations', []))}")
print(f"  - Potential Novelty Verdict: {stored_novelty['potential_novelty_assessment'][:120]}...")
print(f"  - Mandatory Caveat: {stored_novelty['verification_notice']}")

assert "potential novelty based on evaluated literature" in stored_novelty["verification_notice"].lower()
assert "empirical baseline verification" in stored_novelty["verification_notice"].lower()

# Clean up
client.delete(f"/research/{project_id}")
print(f"\n✅ Cleaned up test project #{project_id}")
print("\n🎉 Phase 9 End-to-End API Test Passed Successfully!")
