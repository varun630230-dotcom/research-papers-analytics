import urllib.request
import json
import time

def test():
    data = json.dumps({
        'idea': 'AI-based crop disease detection using smartphone images',
        'goal': 'Research Project',
        'domain': 'Agriculture',
        'technical_level': 'Intermediate',
        'constraints': 'Must run on mobile devices'
    }).encode('utf-8')

    req = urllib.request.Request(
        'http://localhost:8000/api/projects/analyze',
        data=data,
        headers={'Content-Type': 'application/json'}
    )
    with urllib.request.urlopen(req) as resp:
        res = json.loads(resp.read().decode())
        project_id = res['project_id']
        print(f"Started analysis for project: {project_id}")

    for i in range(120):
        time.sleep(2)
        try:
            with urllib.request.urlopen(f"http://localhost:8000/api/projects/{project_id}/status") as s_resp:
                status_data = json.loads(s_resp.read().decode())
                status = status_data.get('status')
                stage = status_data.get('progress', {}).get('current_stage', 0)
                print(f"[{i+1}] Status: {status} | Stage: {stage}/11", flush=True)
                if status in ['completed', 'failed', 'partial']:
                    break
        except Exception as e:
            print(f"[{i+1}] Polling status check error: {e}", flush=True)

    with urllib.request.urlopen(f"http://localhost:8000/api/projects/{project_id}") as p_resp:
        project_data = json.loads(p_resp.read().decode())
        print(f"\n===============================")
        print(f"Final Status: {project_data.get('status')}")
        if project_data.get('error_message'):
            print(f"Error Message: {project_data.get('error_message')}")
        papers = project_data.get('papers', [])
        print(f"Papers Analyzed: {len(papers)}")
        if papers:
            print(f"  Sample Paper: {papers[0].get('title')} ({papers[0].get('year')}) - Source: {papers[0].get('source')}")
        methods = project_data.get('methods', [])
        print(f"Methods Compared: {len(methods)}")
        gaps = project_data.get('research_gaps', [])
        print(f"Research Gaps Found: {len(gaps)}")
        if gaps:
            print(f"  Top Research Gap: {gaps[0].get('title')}")
        opps = project_data.get('opportunities', [])
        print(f"Opportunities Identified: {len(opps)}")
        if opps:
            print(f"  Top Opportunity: {opps[0].get('title')}")
            print(f"  Innovation: {opps[0].get('proposed_innovation')}")
        rec = project_data.get('recommendation')
        if rec:
            print(f"Recommendation Title: {rec.get('title')}")
        print(f"===============================\n")

if __name__ == "__main__":
    test()
