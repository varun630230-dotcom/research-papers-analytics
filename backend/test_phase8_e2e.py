"""
Phase 8 - End-to-End API Integration Test
Tests the full discovery -> filter -> PDF -> analysis -> synthesis -> gaps -> tech -> opportunities pipeline.
Verifies that GET /research/{id} delivers both tech limitations and market opportunities.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi.testclient import TestClient
from main import app
from services.technology_analyzer import VALID_LIMITATION_TYPES
import database as db

client = TestClient(app)

print("=" * 60)
print("  ResearchGap AI - Phase 8 End-to-End API Test")
print("=" * 60)

db.initialize_database()

payload = {
    "topic": "Autonomous Drone Swarms for Wildfire Detection",
    "domain": "Robotics & Remote Sensing",
    "keywords": "UAV swarm, thermal vision, edge inference, mesh networking, early fire detection",
    "objectives": "Analyze battery constraints and decentralized communication barriers in drone swarm surveillance"
}

print(f"\nSubmitting topic: '{payload['topic']}'...")
response = client.post("/research/analyze", json=payload)
assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.text}"

data = response.json()
project_id = data["project_id"]
total_found = data["total_papers_found"]
gaps_count = data["gaps_count"]
tech_count = data["tech_limitations_count"]
opps_count = data["opportunities_count"]

print(f"✅ Created project ID: {project_id}")
print(f"✅ Discovered {total_found} papers")
print(f"✅ Identified {gaps_count} research gaps")
print(f"✅ Extracted {tech_count} technological limitations")
print(f"✅ Derived {opps_count} market opportunities")

# Verify GET /research/{project_id}
proj_resp = client.get(f"/research/{project_id}")
assert proj_resp.status_code == 200
results = proj_resp.json().get("results", {})
stored_tech = results.get("tech_limitations", [])
stored_opps = results.get("market_opportunities", [])

assert len(stored_tech) == tech_count
assert len(stored_opps) == opps_count

print("\nVerifying Technological Limitations:")
for i, lim in enumerate(stored_tech[:2], 1):
    print(f"\n[{i}] {lim['title']}")
    print(f"    Type: {lim['limitation_type']}")
    print(f"    Description: {lim['description'][:90]}...")
    print(f"    Alternatives: {lim['suggested_alternatives'][:90]}...")
    assert lim["limitation_type"] in VALID_LIMITATION_TYPES

print("\nVerifying Market Opportunities:")
for i, opp in enumerate(stored_opps[:2], 1):
    print(f"\n[{i}] {opp['title']}")
    print(f"    Target Users: {opp['target_users']}")
    print(f"    Feasibility: {opp['practical_feasibility']} | Basis: {opp['evidence_basis']}")
    print(f"    Proposed Solution: {opp['proposed_solution'][:90]}...")
    assert opp["practical_feasibility"] in ["High", "Medium", "Low"]
    assert opp["evidence_basis"] in ["research_grounded", "extrapolated_assumption"]

# Clean up
client.delete(f"/research/{project_id}")
print(f"\n✅ Cleaned up test project #{project_id}")
print("\n🎉 Phase 8 End-to-End API Test Passed Successfully!")
