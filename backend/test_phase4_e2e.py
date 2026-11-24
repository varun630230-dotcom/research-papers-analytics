"""
Phase 4 - End-to-End API Integration Test
Tests the combined pipeline:
Discovery -> Filtering & Deduplication -> PDF Extraction -> SQLite Storage
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi.testclient import TestClient
from main import app
import database as db

client = TestClient(app)

print("=" * 60)
print("  ResearchGap AI - Phase 4 End-to-End API Test")
print("=" * 60)

db.initialize_database()

payload = {
    "topic": "Reinforcement Learning with Human Feedback in Large Language Models",
    "domain": "Artificial Intelligence",
    "keywords": "RLHF, reward model, direct preference optimization, alignment",
    "objectives": "Survey key limitations and reward hacking in RLHF algorithms"
}

print(f"\nSubmitting topic: '{payload['topic']}'...")
response = client.post("/research/analyze", json=payload)
assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.text}"

data = response.json()
project_id = data["project_id"]
total_found = data["total_papers_found"]
relevant = data["relevant_papers"]
pdf_count = data["pdf_extracted_count"]

print(f"✅ Created project ID: {project_id}")
print(f"✅ Total Discovered: {total_found}")
print(f"✅ Relevant Papers: {relevant}")
print(f"✅ Full PDFs Extracted: {pdf_count}")

# Fetch papers from DB and inspect pdf_text
papers_resp = client.get(f"/papers/{project_id}")
assert papers_resp.status_code == 200
papers = papers_resp.json()["papers"]

papers_with_full_text = [p for p in papers if p.get("pdf_text") and len(p["pdf_text"]) > 100]
print(f"✅ Papers in DB with full extracted PDF text: {len(papers_with_full_text)}")

if papers_with_full_text:
    sample = papers_with_full_text[0]
    print(f"\nSample Paper with PDF text:")
    print(f"  Title: {sample['title']}")
    print(f"  Source: {sample['source']}")
    print(f"  PDF URL: {sample['pdf_url']}")
    print(f"  Extracted text length: {len(sample['pdf_text'])} characters")
    print(f"  Text preview: {sample['pdf_text'][:250].replace('\n', ' ')}...")

# Clean up
client.delete(f"/research/{project_id}")
print(f"\n✅ Cleaned up test project #{project_id}")
print("\n🎉 Phase 4 End-to-End API Test Passed Successfully!")
