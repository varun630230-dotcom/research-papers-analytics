"""
Phase 7 - End-to-End API Integration Test
Tests the full discovery -> filtering -> PDF -> analysis -> synthesis -> gap detection flow.
Verifies that GET /research/{id} delivers evidence-supported research gaps to frontend.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi.testclient import TestClient
from main import app
from services.gap_detector import VALID_GAP_TYPES
import database as db

client = TestClient(app)

print("=" * 60)
print("  ResearchGap AI - Phase 7 End-to-End API Test")
print("=" * 60)

db.initialize_database()

payload = {
    "topic": "Neuromorphic Computing for Energy-Efficient AI",
    "domain": "Computer Architecture & Hardware",
    "keywords": "spiking neural networks, memristors, event-based cameras, neuromorphic hardware",
    "objectives": "Identify technological barriers to scaling spiking neural networks on memristive hardware"
}

print(f"\nSubmitting topic: '{payload['topic']}'...")
response = client.post("/research/analyze", json=payload)
assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.text}"

data = response.json()
project_id = data["project_id"]
total_found = data["total_papers_found"]
gaps_count = data["gaps_count"]

print(f"✅ Created project ID: {project_id}")
print(f"✅ Discovered {total_found} papers")
print(f"✅ Identified {gaps_count} research gaps")

# Verify GET /research/{project_id}
proj_resp = client.get(f"/research/{project_id}")
assert proj_resp.status_code == 200
results = proj_resp.json().get("results", {})
stored_gaps = results.get("research_gaps", [])

assert len(stored_gaps) == gaps_count, f"Expected {gaps_count} gaps in DB"

print("\nVerifying Identified Research Gaps:")
for i, gap in enumerate(stored_gaps, 1):
    print(f"\n[{i}] {gap['title']}")
    print(f"    Type: {gap['gap_type']} | Tier: {gap['evidence_tier']}")
    print(f"    Description: {gap['description'][:100]}...")
    print(f"    Evidence: {gap['evidence'][:100]}...")
    print(f"    Citing: {gap['supporting_papers']}")
    print(f"    Direction: {gap['potential_direction'][:80]}...")
    
    assert gap["gap_type"] in VALID_GAP_TYPES, f"Invalid gap type: {gap['gap_type']}"
    assert len(gap["supporting_papers"]) > 0, "Gap must cite supporting papers"
    assert len(gap["potential_direction"]) > 0, "Gap must propose a research direction"

# Clean up
client.delete(f"/research/{project_id}")
print(f"\n✅ Cleaned up test project #{project_id}")
print("\n🎉 Phase 7 End-to-End API Test Passed Successfully!")
