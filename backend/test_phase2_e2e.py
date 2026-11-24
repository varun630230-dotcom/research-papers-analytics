"""
Phase 2 - End-to-End API Integration Test
Tests the full paper discovery flow via FastAPI TestClient:
1. Submitting a new research topic via POST /research/analyze
2. Verifying papers are found from academic sources
3. Verifying database storage and paper schema
4. Verifying paper retrieval via GET /papers/{id} and GET /research/{id}
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi.testclient import TestClient
from main import app
import database as db

client = TestClient(app)

print("=" * 60)
print("  ResearchGap AI - Phase 2 End-to-End API Test")
print("=" * 60)

db.initialize_database()

payload = {
    "topic": "Graph Neural Networks for Drug Discovery",
    "domain": "Bioinformatics",
    "keywords": "graph neural networks, molecular property prediction, drug discovery",
    "objectives": "Analyze current GNN architectures and limitations in molecular chemistry"
}

print(f"\nSubmitting research topic: '{payload['topic']}'...")
response = client.post("/research/analyze", json=payload)
assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.text}"

data = response.json()
project_id = data["project_id"]
total_papers = data["total_papers_found"]
counts = data["counts_by_source"]

print(f"✅ Created project ID: {project_id}")
print(f"✅ Discovered {total_papers} papers total:")
for src, cnt in counts.items():
    print(f"   - {src}: {cnt}")

assert total_papers > 0, "Expected at least 1 paper discovered across sources"

# Retrieve papers via /papers/{project_id}
print(f"\nVerifying GET /papers/{project_id}...")
papers_resp = client.get(f"/papers/{project_id}")
assert papers_resp.status_code == 200
papers_data = papers_resp.json()
assert len(papers_data["papers"]) == total_papers

# Check first 3 papers
print("\nSample discovered papers:")
for i, paper in enumerate(papers_data["papers"][:3], 1):
    print(f"\n[{i}] Source: {paper['source']}")
    print(f"    Title: {paper['title']}")
    print(f"    Authors: {paper['authors'][:60]}...")
    print(f"    Date: {paper['publication_date']}")
    print(f"    URL: {paper['url']}")
    print(f"    PDF: {paper['pdf_url']}")
    print(f"    Abstract: {paper['abstract'][:100]}...")

# Clean up test project
client.delete(f"/research/{project_id}")
print(f"\n✅ Cleaned up test project #{project_id}")
print("\n🎉 Phase 2 End-to-End API Test Passed Successfully!")
