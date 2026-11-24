"""
ResearchGap AI - Research Routes
==================================
API endpoints for creating and retrieving research analyses.

Handles:
- Starting a research analysis (discovery -> filter -> PDF -> analysis -> synthesis -> gaps -> tech -> opportunities -> scoring -> novelty -> architecture -> roadmap)
- Retrieving analysis results & papers
- Getting research history
- Deleting projects
"""

import logging
from fastapi import APIRouter, HTTPException
from models import ResearchRequest
import database as db
from services.paper_search import search_all_sources
from services.paper_filter import filter_and_rank_papers
from services.pdf_extractor import batch_extract_papers
from services.paper_analyzer import analyze_project_papers
from services.evidence_synthesizer import synthesize_multi_paper_evidence
from services.gap_detector import detect_research_gaps
from services.technology_analyzer import analyze_technological_limitations
from services.opportunity_analyzer import analyze_market_opportunities
from services.scoring_engine import score_all_opportunities
from services.novelty_assessor import assess_research_novelty
from services.architecture_generator import generate_architecture_recommendation
from services.roadmap_generator import generate_development_roadmap
from services.ai_reviewer import review_research_report
from utils.helpers import build_search_queries
from config import config

logger = logging.getLogger("researchgap.routes.research")
router = APIRouter(prefix="/research", tags=["Research"])


def run_paper_pipeline(project_id: int, topic: str, description: str = "", keywords: str = "", domain: str = "", objectives: str = ""):
    """
    Executes the complete research intelligence pipeline:
    1. Phase 2: Multi-source academic paper discovery (OpenAlex, arXiv, Semantic Scholar, Crossref)
    2. Phase 3: Deduplication and transparent keyword relevance ranking
    3. Phase 4: Full PDF text download and extraction (PyPDF)
    4. Phase 5: Structured 10-dimension individual paper analysis (Gemini AI / Heuristic)
    5. Phase 6: Multi-Paper Evidence Synthesis & 3-Tier Claim Classification
    6. Phase 7: Research Gap Detection across 7 taxonomies with citation grounding
    7. Phase 8: Technological Limitations & Grounded Market Opportunity Analysis
    8. Phase 9: Weighted Opportunity Scoring & Rigorous Novelty Assessment
    9. Phase 10: Technical Architecture Recommendations & 8-Phase Development Roadmap
    10. Saves all results and relations to SQLite
    """
    try:
        # Phase 2: Paper Discovery
        db.update_project_status(project_id, "searching")
        queries = build_search_queries(topic, keywords, domain)
        primary_query = queries[0] if queries else topic
        
        search_result = search_all_sources(
            query=primary_query, 
            limit_per_source=config.get("PAPERS_PER_SOURCE", 15)
        )
        raw_papers = search_result.get("papers", [])
        total_discovered = len(raw_papers)
        
        # Phase 3: Filtering & Deduplication
        db.update_project_status(project_id, "filtering")
        filter_result = filter_and_rank_papers(
            papers=raw_papers,
            topic=topic,
            keywords=keywords,
            domain=domain,
            max_papers=config.get("MAX_PAPERS_TOTAL", 40)
        )
        filtered_papers = filter_result["filtered_papers"]
        stats = filter_result["stats"]
        
        # Phase 4: PDF Extraction for top ranked papers
        db.update_project_status(project_id, "extracting_pdfs")
        enriched_papers = batch_extract_papers(
            papers=filtered_papers,
            max_to_extract=5,
            max_workers=3
        )
        
        # Save enriched papers to SQLite
        saved_count = db.save_papers(project_id, enriched_papers)
        db_papers = db.get_papers(project_id)
        
        # Sync pdf_text in database for saved papers
        for p_db, p_enriched in zip(db_papers, enriched_papers):
            if p_enriched.get("pdf_text"):
                db.update_paper_pdf_text(p_db["id"], p_enriched["pdf_text"])
                
        # Phase 5: Individual Paper Analysis
        db.update_project_status(project_id, "analyzing_papers")
        top_db_papers = db.get_papers(project_id, relevant_only=True)[:5]
        
        paper_analyses = analyze_project_papers(
            papers=top_db_papers,
            project_id=project_id,
            max_to_analyze=5
        )
        
        # Save each structured analysis to SQLite
        for p_row, analysis in zip(top_db_papers, paper_analyses):
            db.save_paper_analysis(
                paper_id=p_row["id"],
                project_id=project_id,
                analysis_data=analysis
            )
            
        # Phase 6: Multi-Paper Evidence Synthesis
        db.update_project_status(project_id, "synthesizing_evidence")
        synthesis = synthesize_multi_paper_evidence(
            topic=topic,
            domain=domain,
            paper_analyses=paper_analyses
        )
        
        # Phase 7: Research Gap Detection
        db.update_project_status(project_id, "detecting_gaps")
        research_gaps = detect_research_gaps(
            topic=topic,
            domain=domain,
            paper_analyses=paper_analyses,
            synthesis=synthesis
        )
        
        # Phase 8: Technological Limitations Analysis
        db.update_project_status(project_id, "analyzing_technology")
        tech_limitations = analyze_technological_limitations(
            topic=topic,
            domain=domain,
            paper_analyses=paper_analyses,
            synthesis=synthesis
        )
        
        # Phase 8: Market Opportunity Analysis
        db.update_project_status(project_id, "analyzing_opportunities")
        market_opportunities = analyze_market_opportunities(
            topic=topic,
            domain=domain,
            research_gaps=research_gaps,
            tech_limitations=tech_limitations
        )
        
        # Phase 9: Weighted Opportunity Scoring
        db.update_project_status(project_id, "scoring_opportunities")
        opportunity_scores = score_all_opportunities(market_opportunities)
        
        # Phase 9: Novelty Assessment
        db.update_project_status(project_id, "assessing_novelty")
        novelty_assessment = assess_research_novelty(
            topic=topic,
            description=description,
            domain=domain,
            objectives=objectives,
            papers=filtered_papers,
            paper_analyses=paper_analyses
        )
        
        # Phase 10: Technical Architecture Recommendations
        db.update_project_status(project_id, "generating_architecture")
        architecture = generate_architecture_recommendation(
            topic=topic,
            domain=domain,
            research_gaps=research_gaps,
            tech_limitations=tech_limitations
        )
        
        # Phase 10: 8-Phase Development Roadmap
        db.update_project_status(project_id, "generating_roadmap")
        roadmap = generate_development_roadmap(
            topic=topic,
            domain=domain,
            architecture=architecture
        )
        
        # Phase 11: AI Research Reviewer Critique & Audit
        db.update_project_status(project_id, "reviewing_report")
        ai_review = review_research_report(
            topic=topic,
            domain=domain,
            results={
                "synthesis": synthesis,
                "research_gaps": research_gaps,
                "tech_limitations": tech_limitations,
                "market_opportunities": market_opportunities,
                "opportunity_scores": opportunity_scores,
                "novelty_assessment": novelty_assessment,
                "architecture": architecture,
                "roadmap": roadmap
            }
        )
        
        # Save all results to SQLite research_results
        existing_results = db.get_research_results(project_id) or {}
        existing_results["synthesis"] = synthesis
        existing_results["research_gaps"] = research_gaps
        existing_results["tech_limitations"] = tech_limitations
        existing_results["market_opportunities"] = market_opportunities
        existing_results["opportunity_scores"] = opportunity_scores
        existing_results["novelty_assessment"] = novelty_assessment
        existing_results["architecture"] = architecture
        existing_results["roadmap"] = roadmap
        existing_results["ai_review"] = ai_review
        db.save_research_results(project_id, existing_results)
        
        # Update project status
        db.update_project_status(
            project_id=project_id,
            status="completed",
            total_papers=total_discovered,
            relevant_papers=stats["relevant_count"],
        )
        
        pdf_extracted_count = sum(1 for p in enriched_papers if p.get("pdf_text"))
        logger.info(
            f"Project #{project_id}: Pipeline complete. Discovered {total_discovered}, "
            f"Architecture designed. 8-phase roadmap generated."
        )
        return {
            **stats,
            "pdf_extracted_count": pdf_extracted_count,
            "analyzed_count": len(paper_analyses),
            "gaps_count": len(research_gaps),
            "tech_limitations_count": len(tech_limitations),
            "opportunities_count": len(market_opportunities),
            "scores_count": len(opportunity_scores),
        }
    except Exception as e:
        logger.error(f"Error in research pipeline for project #{project_id}: {e}")
        db.update_project_status(project_id, "failed")
        raise e


@router.post("/analyze", status_code=201)
async def start_analysis(request: ResearchRequest):
    """Start a new research analysis."""
    project_id = db.create_project(
        topic=request.topic,
        description=request.description,
        domain=request.domain,
        keywords=request.keywords,
        objectives=request.objectives,
    )
    
    pipeline_stats = run_paper_pipeline(
        project_id=project_id,
        topic=request.topic,
        description=request.description,
        keywords=request.keywords,
        domain=request.domain,
        objectives=request.objectives,
    )
    
    project = db.get_project(project_id)
    papers = db.get_papers(project_id)
    analyses = db.get_paper_analyses(project_id)
    results = db.get_research_results(project_id)
    
    counts_by_source = {}
    for p in papers:
        for s in p.get("source", "").split(","):
            s_clean = s.strip()
            if s_clean:
                counts_by_source[s_clean] = counts_by_source.get(s_clean, 0) + 1
                
    return {
        "project_id": project_id,
        "topic": request.topic,
        "status": project["status"],
        "total_papers_found": project["total_papers_found"],
        "relevant_papers": project["relevant_papers"],
        "duplicates_removed": pipeline_stats.get("duplicates_removed", 0) if pipeline_stats else 0,
        "pdf_extracted_count": pipeline_stats.get("pdf_extracted_count", 0) if pipeline_stats else 0,
        "papers_analyzed_count": len(analyses),
        "gaps_count": len(results.get("research_gaps", [])) if results else 0,
        "tech_limitations_count": len(results.get("tech_limitations", [])) if results else 0,
        "opportunities_count": len(results.get("market_opportunities", [])) if results else 0,
        "counts_by_source": counts_by_source,
        "synthesis": results.get("synthesis", {}) if results else {},
        "research_gaps": results.get("research_gaps", []) if results else [],
        "tech_limitations": results.get("tech_limitations", []) if results else [],
        "market_opportunities": results.get("market_opportunities", []) if results else [],
        "opportunity_scores": results.get("opportunity_scores", []) if results else [],
        "novelty_assessment": results.get("novelty_assessment", {}) if results else {},
        "architecture": results.get("architecture", {}) if results else {},
        "roadmap": results.get("roadmap", {}) if results else {},
        "ai_review": results.get("ai_review", {}) if results else {},
        "message": (
            f"Analysis complete for '{request.topic}'. "
            f"Discovered {project['total_papers_found']} papers. "
            f"Architecture recommendations, 8-phase roadmap, and AI peer review generated."
        ),
    }


@router.get("/history")
async def get_research_history():
    """Returns all past research projects."""
    projects = db.get_all_projects()
    return {
        "projects": [
            {
                "id": p["id"],
                "topic": p["topic"],
                "domain": p["domain"],
                "status": p["status"],
                "total_papers_found": p["total_papers_found"],
                "relevant_papers": p["relevant_papers"],
                "created_at": p["created_at"],
            }
            for p in projects
        ],
        "total": len(projects),
    }


@router.get("/{project_id}")
async def get_research_project(project_id: int):
    """Returns full project details, papers, analyses, and results."""
    project = db.get_project(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Research project not found")
    
    papers = db.get_papers(project_id)
    analyses = db.get_paper_analyses(project_id)
    results = db.get_research_results(project_id)
    
    return {
        "project": dict(project),
        "papers": papers,
        "analyses": analyses,
        "results": results if results else {},
    }


@router.delete("/{project_id}")
async def delete_research_project(project_id: int):
    """Deletes a research project and all associated records."""
    project = db.get_project(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Research project not found")
    
    db.delete_project(project_id)
    return {"message": f"Project '{project['topic']}' deleted successfully"}
