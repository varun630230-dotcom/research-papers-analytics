"""
Phase 1 - In-Process API & Integration Tests
Uses FastAPI TestClient to test all endpoints, database logic, models, and static file serving.
"""

import json
import sys
import os

# Add backend directory to sys.path so imports work cleanly
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi.testclient import TestClient
from main import app
import database as db

client = TestClient(app)
passed = 0
failed = 0

def test(name, condition, detail=""):
    global passed, failed
    if condition:
        print(f"  ✅ {name}")
        passed += 1
    else:
        print(f"  ❌ {name} - {detail}")
        failed += 1

print("=" * 60)
print("  ResearchGap AI - Phase 1 Verification Tests")
print("=" * 60)

# Initialize database
db.initialize_database()

# Test 1: Health check
print("\n--- Health Check ---")
r = client.get("/health")
test("Status 200", r.status_code == 200)
data = r.json()
test("Status is healthy", data.get("status") == "healthy")
test("Has gemini_configured field", "gemini_configured" in data)
test("Has timestamp", "timestamp" in data)
print(f"  Response: {json.dumps(data, indent=2)}")

# Test 2: Create project
print("\n--- Create Research Project ---")
payload = {
    "topic": "Federated learning for healthcare data privacy",
    "description": "Investigating FL approaches for sensitive medical data",
    "domain": "Machine Learning",
    "keywords": "federated, privacy, healthcare",
    "objectives": "Find gaps in current FL healthcare research"
}
r = client.post("/research/analyze", json=payload)
test("Status 201", r.status_code == 201)
data = r.json()
test("Has project_id", "project_id" in data)
test("Status is valid", data.get("status") in ["pending", "completed"])
project_id = data.get("project_id")
print(f"  Created project ID: {project_id}")

# Test 3: Get project
print("\n--- Get Project ---")
r = client.get(f"/research/{project_id}")
test("Status 200", r.status_code == 200)
data = r.json()
test("Has project data", "project" in data)
test("Has papers list", "papers" in data)
test("Topic matches", data["project"]["topic"] == payload["topic"])
test("Domain matches", data["project"]["domain"] == payload["domain"])

# Test 4: Research History
print("\n--- Research History ---")
r = client.get("/research/history")
test("Status 200", r.status_code == 200)
data = r.json()
test("Has projects list", "projects" in data)
test("Has total count", data.get("total", 0) >= 1)

# Test 5: Papers list
print("\n--- Papers Endpoint ---")
r = client.get(f"/papers/{project_id}")
test("Status 200", r.status_code == 200)
data = r.json()
test("Has papers list", "papers" in data)
test("Papers returned", isinstance(data.get("papers"), list))

# Test 6: Paper analyses
print("\n--- Paper Analyses ---")
r = client.get(f"/papers/{project_id}/analyses")
test("Status 200", r.status_code == 200)

# Test 7: Export JSON
print("\n--- Export JSON ---")
r = client.get(f"/export/{project_id}/json")
test("Status 200", r.status_code == 200)
test("Content-Type is JSON", "application/json" in r.headers.get("content-type", ""))
export_data = r.json()
test("Has export_info", "export_info" in export_data)
test("Has project data", "project" in export_data)

# Test 8: Export Markdown
print("\n--- Export Markdown ---")
r = client.get(f"/export/{project_id}/markdown")
test("Status 200", r.status_code == 200)
test("Is markdown", "text/markdown" in r.headers.get("content-type", ""))
test("Has title", "Research Intelligence Report" in r.text)

# Test 9: 404 handling
print("\n--- Error Handling ---")
r = client.get("/research/999999")
test("404 for missing project", r.status_code == 404)

# Test 10: Input validation
print("\n--- Input Validation ---")
r = client.post("/research/analyze", json={"topic": "ab"})
test("422 for topic under min_length (3)", r.status_code == 422)

r = client.post("/research/analyze", json={})
test("422 for missing required topic field", r.status_code == 422)

# Test 11: Frontend Serving
print("\n--- Frontend Static Serving ---")
r = client.get("/")
test("Serves index.html at root", r.status_code == 200)
test("Root contains ResearchGap AI", "ResearchGap AI" in r.text)

r_css = client.get("/static/style.css")
test("Serves style.css", r_css.status_code == 200)

r_js = client.get("/static/app.js")
test("Serves app.js", r_js.status_code == 200)

# Test 12: Delete
print("\n--- Delete Project ---")
r = client.delete(f"/research/{project_id}")
test("Status 200", r.status_code == 200)
test("Has success message", "deleted" in r.json().get("message", "").lower())

r = client.get(f"/research/{project_id}")
test("404 after delete", r.status_code == 404)

# Summary
print("\n" + "=" * 60)
print(f"  Results: {passed} passed, {failed} failed, {passed + failed} total")
print("=" * 60)

if failed > 0:
    sys.exit(1)
else:
    print("  🎉 All Phase 1 tests passed successfully!")
