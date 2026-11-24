"""
Phase 6 - End-to-End API Integration Test
Tests the full pipeline from discovery through multi-paper evidence synthesis:
1. POST /research/analyze
2. Verifies SQLite research_results contains 'synthesis'
3. Verifies 3-tier claim structure and cross-paper insights
4. Verifies GET /research/{id} delivers the synthesis to frontend
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi.testclient import TestClient
from main import app
import database as db

client = TestClient(app)

print("=" * 60)
print("  ResearchGap AI - Phase 6 End-to-End API Test")
print("=" * 60)

db.initialize_database()

payload = {
    "topic": "Quantum Machine Learning for Optimization",
    "domain": "Quantum Computing",
    "keywords": "quantum annealing, QAOA, variational quantum eigensolver, quantum circuits",
    "objectives": "Synthesize current QML optimization capabilities on noisy intermediate-scale quantum devices"
}

print(f"\nSubmitting research topic: '{payload['topic']}'...")
response = client.post("/research/analyze", json=payload)
assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.text}"

data = response.json()
project_id = data["project_id"]
total_found = data["total_papers_found"]
analyzed_count = data["papers_analyzed_count"]
synthesis = data.get("synthesis", {})

print(f"✅ Created project ID: {project_id}")
print(f"✅ Discovered {total_found} papers")
print(f"✅ Analyzed {analyzed_count} papers")
print(f"✅ Synthesis Summary: {synthesis.get('summary', '')[:120]}...")

# Verify GET /research/{project_id}
proj_resp = client.get(f"/research/{project_id}")
assert proj_resp.status_code == 200
proj_data = proj_resp.json()
stored_results = proj_data.get("results", {})
stored_synthesis = stored_results.get("synthesis", {})

assert stored_synthesis, "Expected synthesis object in research results"

print("\nVerifying Multi-Paper Synthesis Structure:")
print(f"  - Common Approaches: {len(stored_synthesis.get('common_approaches', []))} found")
for app_item in stored_synthesis.get("common_approaches", [])[:2]:
    print(f"      * {app_item}")

print(f"  - Frequently Used Algorithms: {len(stored_synthesis.get('frequently_used_algorithms', []))} found")
for algo in stored_synthesis.get("frequently_used_algorithms", [])[:2]:
    print(f"      * {algo.get('name')}")

print(f"  - Repeated Limitations: {len(stored_synthesis.get('repeated_limitations', []))} found")
for lim in stored_synthesis.get("repeated_limitations", [])[:2]:
    print(f"      * {lim.get('limitation')[:80]}...")

print(f"  - Underexplored Areas: {len(stored_synthesis.get('underexplored_areas', []))} found")
for area in stored_synthesis.get("underexplored_areas", [])[:2]:
    print(f"      * {area.get('area')}")

# Verify 3-Tier Claim Classification
tiers = stored_synthesis.get("evidence_tiers", {})
assert "tier_1_directly_supported" in tiers
assert "tier_2_cross_paper_derived" in tiers
assert "tier_3_open_hypotheses" in tiers

print("\nThree-Tier Claim Classification:")
print(f"  - Tier 1 (Directly Supported Claims): {len(tiers['tier_1_directly_supported'])}")
if tiers['tier_1_directly_supported']:
    print(f"      Sample: {tiers['tier_1_directly_supported'][0].get('claim')[:80]}...")

print(f"  - Tier 2 (Cross-Paper Insights): {len(tiers['tier_2_cross_paper_derived'])}")
if tiers['tier_2_cross_paper_derived']:
    print(f"      Sample: {tiers['tier_2_cross_paper_derived'][0].get('insight')[:80]}...")

print(f"  - Tier 3 (Open Hypotheses): {len(tiers['tier_3_open_hypotheses'])}")
if tiers['tier_3_open_hypotheses']:
    print(f"      Sample: {tiers['tier_3_open_hypotheses'][0].get('hypothesis')[:80]}...")

# Clean up
client.delete(f"/research/{project_id}")
print(f"\n✅ Cleaned up test project #{project_id}")
print("\n🎉 Phase 6 End-to-End API Test Passed Successfully!")
