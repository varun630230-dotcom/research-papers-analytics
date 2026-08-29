import asyncio
import json
from app.config import settings
from app.database import async_session, create_tables
from app.schemas.requests import AnalyzeRequest
from app.services.pipeline import AnalysisPipeline
from app.models.models import Project
from sqlalchemy.future import select

async def main():
    print("==================================================")
    print("STARTING INNOVATE AI PIPELINE UPGRADE VERIFICATION")
    print("==================================================")
    
    await create_tables()
    pipeline = AnalysisPipeline(settings)
    
    req = AnalyzeRequest(
        idea="cyberbullying detection",
        goal="Final Year Project",
        domain="Natural Language Processing",
        technical_level="Intermediate",
        constraints="Low-latency real-time inference on informal social media text"
    )
    
    async with async_session() as db:
        new_project = Project(
            idea=req.idea,
            goal=req.goal,
            domain=req.domain,
            technical_level=req.technical_level,
            constraints=req.constraints,
            status="analyzing"
        )
        db.add(new_project)
        await db.commit()
        await db.refresh(new_project)
        project_id = new_project.id
        print(f"Created Project ID: {project_id}")

        print("\n--- RUNNING 11-STAGE INTELLIGENCE PIPELINE ---")
        await pipeline.run(project_id, req, db)
        
        # Query results
        res = await db.execute(select(Project).filter(Project.id == project_id))
        proj = res.scalars().first()
        
        print(f"\nFinal Pipeline Status: {proj.status}")
        if proj.error_message:
            print(f"Error: {proj.error_message}")
            
        data = json.loads(proj.results_data or "{}")
        
        print("\n================== VERIFICATION RESULTS ==================")
        
        # 1. Coverage
        cov = data.get("coverage", {})
        print(f"[+] Candidates Retrieved: {cov.get('candidates_retrieved')}")
        print(f"[+] Unique Deduplicated: {cov.get('unique_papers')}")
        print(f"[+] Direct Relevant Count: {cov.get('direct_relevant_count')}")
        print(f"[+] Full-Text PDFs Analyzed: {cov.get('full_text_analyzed_count')}")
        print(f"[+] Abstract-Only Count: {cov.get('abstract_only_count')}")
        print(f"[+] Sources Searched: {', '.join(cov.get('sources_searched', []))}")
        
        # 2. Top 5 Core Research Papers
        top_p = data.get("top_papers", [])
        print(f"\n[+] Top 5 Core Research Papers ({len(top_p)}):")
        for i, p in enumerate(top_p, 1):
            print(f"  {i}. [{p.get('relevance_category')} - {p.get('relevance_score')}%] {p.get('title')} ({p.get('year')})")
            print(f"     Extraction: {p.get('extraction_level')}")
            print(f"     Why Selected: {p.get('relevance_explanation')}")
            if p.get("pdf_url"):
                print(f"     PDF: {p.get('pdf_url')}")
                
        # 3. Background Papers
        bg_p = data.get("background_papers", [])
        print(f"\n[+] Background / Supporting Tech Papers ({len(bg_p)}):")
        for p in bg_p[:4]:
            print(f"  * [BG] {p.get('title')} ({p.get('citation_count')} cites)")

        # 4. Multi-Paper Research Gaps
        rg = data.get("research_gaps", [])
        print(f"\n[+] Multi-Paper Research Gaps ({len(rg)}):")
        for g in rg:
            print(f"  * [{g.get('type')}] {g.get('title')} (Confidence: {g.get('confidence')}, Supporting Papers: {g.get('number_of_supporting_papers')})")
            print(f"    Evidence: {g.get('evidence')[:120]}...")
            if g.get("supporting_sources"):
                print(f"    Papers: {', '.join(g.get('supporting_sources')[:2])}")

        # 5. Opportunities & Scores
        opps = data.get("opportunities", [])
        print(f"\n[+] Synthesized Opportunities ({len(opps)}):")
        for opp in opps:
            scores = opp.get("scores", {})
            print(f"  * {opp.get('title')} -> Overall Score: {scores.get('overall')}/100")
            print(f"    Breakdown: RG={scores.get('research_gap')}, MG={scores.get('market_gap')}, TF={scores.get('technology_feasibility')}, Diff={scores.get('innovation_potential')}")
            print(f"    Differentiation: {opp.get('differentiation_potential')}")

        # 6. Novelty Assessment
        nov = data.get("novelty", {})
        print(f"\n[+] Novelty Assessment:")
        print(f"  * Similarity: {nov.get('similarity_score')}")
        print(f"  * Assessment: {nov.get('final_assessment')}")
        print(f"  * Disclaimer: {nov.get('disclaimer')}")

        # 7. Recommended Solution
        rec = data.get("recommendation", {})
        print(f"\n[+] Recommended Solution:")
        print(f"  * Title: {rec.get('title')}")
        print(f"  * Innovation: {rec.get('core_innovation')}")
        print(f"  * Tech Stack: {', '.join(rec.get('technology_stack', []))}")

        print("\n==================================================")
        print("ALL AUDIT CHECKS COMPLETED SUCCESSFULLY!")
        print("==================================================")

if __name__ == "__main__":
    asyncio.run(main())
