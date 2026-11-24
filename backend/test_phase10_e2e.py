"""
Phase 10 - End-to-End API Integration Test
Tests the full discovery -> filter -> PDF -> analysis -> synthesis -> gaps -> tech -> opportunities -> scoring -> novelty -> architecture -> roadmap pipeline.
Verifies that GET /research/{id} delivers technical architecture and 8-phase roadmap.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi.testclient import TestClient
from main import app
import database as db

client = TestClient(app)

print("=" * 60)
print("  ResearchGap AI - Phase 10 End-to-End API Test")
print("=" * 60)

db.initialize_database()

payload = {
    "topic": "Spiking Neural Networks for Edge Robotics",
    "domain": "Neuromorphic AI & Robotics",
    "keywords": "spiking neural networks, event-based vision, neuromorphic hardware, edge robotics, ultra-low power",
    "objectives": "Propose an asynchronous spiking neural network architecture for ultra-low latency robotic motor control"
}

print(f"\nSubmitting topic: '{payload['topic']}'...")
response = client.post("/research/analyze", json=payload)
assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.text}"

data = response.json()
project_id = data["project_id"]
total_found = data["total_papers_found"]
arch = data.get("architecture", {})
roadmap = data.get("roadmap", {})

print(f"✅ Created project ID: {project_id}")
print(f"✅ Discovered {total_found} papers")
print(f"✅ Architecture Designed: {arch.get('proposed_solution', '')[:90]}...")
print(f"✅ Roadmap Generated: {roadmap.get('total_phases')} phases ({roadmap.get('total_estimated_weeks')} weeks total)")

# Verify GET /research/{project_id}
proj_resp = client.get(f"/research/{project_id}")
assert proj_resp.status_code == 200
results = proj_resp.json().get("results", {})
stored_arch = results.get("architecture", {})
stored_roadmap = results.get("roadmap", {})

assert stored_arch, "Expected architecture in research results"
assert stored_roadmap, "Expected roadmap in research results"

print("\nVerifying Technical Architecture Recommendations:")
print(f"  - Target Gap Addressed: {stored_arch['target_gap_addressed']}")
print(f"  - System Components: {len(stored_arch.get('system_components', []))} layers")
for comp in stored_arch.get("system_components", [])[:2]:
    print(f"      * {comp.get('name')}: {comp.get('role')[:60]}...")

print(f"  - Recommended Technologies: {len(stored_arch.get('recommended_technologies', []))} tools")
for tech in stored_arch.get("recommended_technologies", [])[:2]:
    print(f"      * {tech.get('name')}: {tech.get('justification')[:60]}...")

print(f"  - Data Flow Pipeline: {len(stored_arch.get('data_flow', []))} steps")
print(f"  - Model Recommendations: {len(stored_arch.get('model_recommendations', []))} models")

print("\nVerifying 8-Phase Development Roadmap:")
phases = stored_roadmap.get("phases", [])
assert len(phases) == 8, f"Expected 8 phases, got {len(phases)}"

for p in phases:
    print(f"  [{p['phase_number']}] {p['title']} ({p['estimated_weeks']} wks) -> Deliverable: {p['deliverable'][:60]}...")
    assert len(p["tasks"]) > 0, "Phase must contain specific tasks"
    assert len(p["deliverable"]) > 0, "Phase must specify concrete deliverable"

# Clean up
client.delete(f"/research/{project_id}")
print(f"\n✅ Cleaned up test project #{project_id}")
print("\n🎉 Phase 10 End-to-End API Test Passed Successfully!")
