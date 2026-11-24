"""
Phase 3 - End-to-End API Integration Test
Tests the full discovery + deduplication + relevance ranking pipeline via FastAPI TestClient.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi.testclient import TestClient
from main import app
import database as db

client = TestClient(app)

print("=" * 60)
print("  ResearchGap AI - Phase 3 End-to-End API Test")
print("=" * 60)

db.initialize_database()

payload = {
    "topic": "Federated Learning for Healthcare Data Privacy",
    "domain": "Machine Learning",
    "keywords": "differential privacy, healthcare, medical data",
    "objectives": "Identify privacy bottlenecks and data heterogeneity challenges in medical federated learning"
}

print(f"\nSubmitting research topic: '{payload['topic']}'...")
response = client.post("/research/analyze", json=payload)
assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.text}"

data = response.json()
project_id = data["project_id"]
total_found = data["total_papers_found"]
relevant_count = data["relevant_papers"]
duplicates_removed = data["duplicates_removed"]

print(f"✅ Created project ID: {project_id}")
print(f"✅ Total Discovered: {total_found}")
print(f"✅ Duplicates Removed: {duplicates_removed}")
print(f"✅ Relevant Papers: {relevant_count}")
print(f"✅ Source Breakdown: {data['counts_by_source']}")

# Verify via GET /papers/{project_id}
papers_resp = client.get(f"/papers/{project_id}")
assert papers_resp.status_code == 200
papers = papers_resp.json()["papers"]

assert len(papers) > 0, "Expected stored papers in database"

# Verify ranking: papers must be ordered by relevance_score descending
scores = [p["relevance_score"] for p in papers]
is_sorted = all(scores[i] >= scores[i+1] for i in range(len(scores)-1))
print(f"✅ Papers are sorted by relevance score descending: {is_sorted} (Top score: {scores[0]}, Lowest: {scores[-1]})")
assert is_sorted, "Papers must be ordered by relevance score descending"

# Display top 3 ranked papers
print("\nTop 3 Ranked Papers:")
for i, p in enumerate(papers[:3], 1):
    print(f"\n[{i}] Score: {p['relevance_score']}/10.0 | Source: {p['source']}")
    print(f"    Title: {p['title']}")
    print(f"    Authors: {p['authors'][:60]}...")
    print(f"    Date: {p['publication_date']}")
    print(f"    PDF: {'Yes' if p['pdf_url'] else 'No'}")

# Clean up
client.delete(f"/research/{project_id}")
print(f"\n✅ Cleaned up test project #{project_id}")
print("\n🎉 Phase 3 End-to-End API Test Passed Successfully!")
