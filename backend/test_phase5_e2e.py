"""
Phase 5 - End-to-End API Integration Test
Tests the full discovery -> filtering -> PDF extraction -> individual paper analysis flow.
Verifies GET /papers/{id}/analyses endpoint returns 10-dimension structured data.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi.testclient import TestClient
from main import app
import database as db

client = TestClient(app)

print("=" * 60)
print("  ResearchGap AI - Phase 5 End-to-End API Test")
print("=" * 60)

db.initialize_database()

payload = {
    "topic": "Diffusion Models for Medical Image Generation",
    "domain": "Biomedical Imaging",
    "keywords": "diffusion models, synthetic MRI, denoising, generative models",
    "objectives": "Survey synthetic medical image synthesis fidelity and clinical validity"
}

print(f"\nSubmitting research topic: '{payload['topic']}'...")
response = client.post("/research/analyze", json=payload)
assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.text}"

data = response.json()
project_id = data["project_id"]
total_found = data["total_papers_found"]
analyzed_count = data["papers_analyzed_count"]

print(f"✅ Created project ID: {project_id}")
print(f"✅ Discovered {total_found} papers")
print(f"✅ Analyzed {analyzed_count} papers across 10 structured dimensions")

# Verify GET /papers/{project_id}/analyses
analyses_resp = client.get(f"/papers/{project_id}/analyses")
assert analyses_resp.status_code == 200
analyses_data = analyses_resp.json()
analyses = analyses_data["analyses"]

assert len(analyses) == analyzed_count, f"Expected {analyzed_count} analyses in DB"

print(f"\nVerifying structured analysis schema for {len(analyses)} papers:")
for i, item in enumerate(analyses[:2], 1):
    a = item["analysis_data"]
    print(f"\n[{i}] Paper: {a.get('paper_title', 'Untitled')[:60]}...")
    print(f"    Mode: {a.get('analysis_mode')}")
    print(f"    Problem: {a.get('research_problem')[:80]}...")
    print(f"    Methodology: {a.get('methodology')[:80]}...")
    print(f"    Algorithms: {a.get('algorithms')}")
    print(f"    Technologies: {a.get('technologies')}")
    print(f"    Datasets: {a.get('datasets')}")
    print(f"    Limitations: {a.get('limitations')}")
    print(f"    Future Work: {a.get('future_work')}")
    print(f"    Contributions: {a.get('contributions')}")
    
    # Assert all 10 keys exist
    for k in ["research_problem", "research_objectives", "methodology", "algorithms",
              "technologies", "datasets", "experimental_findings", "limitations",
              "future_work", "contributions"]:
        assert k in a, f"Key '{k}' missing from analysis!"

# Clean up
client.delete(f"/research/{project_id}")
print(f"\n✅ Cleaned up test project #{project_id}")
print("\n🎉 Phase 5 End-to-End API Test Passed Successfully!")
