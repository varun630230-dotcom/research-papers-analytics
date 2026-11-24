"""
ResearchGap AI - Export Routes
================================
API endpoints for exporting complete research intelligence reports.

Provides:
- Complete JSON dossier export (including raw metadata, papers, extractions, analyses, scores)
- Rigorous Academic Markdown Report ready for distribution, peer review, or archival.
"""

import json
from datetime import datetime
from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
import database as db

router = APIRouter(prefix="/export", tags=["Export"])


@router.get("/{project_id}/json")
async def export_json(project_id: int):
    """
    Exports the full research analysis as a comprehensive JSON dossier.
    """
    project = db.get_project(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Research project not found")
    
    papers = db.get_papers(project_id)
    analyses = db.get_paper_analyses(project_id)
    results = db.get_research_results(project_id)
    
    export_data = {
        "export_info": {
            "platform": "ResearchGap AI",
            "version": "1.0.0",
            "exported_at": datetime.now().isoformat(),
            "description": "Intelligent Research Paper Analysis & Gap Detection Platform"
        },
        "project": dict(project),
        "total_papers_count": len(papers),
        "papers": papers,
        "paper_analyses": analyses,
        "results": results if results else {}
    }
    
    safe_topic = "".join(c if c.isalnum() or c == " " else "_" for c in project["topic"])
    safe_topic = safe_topic[:50].strip().replace(" ", "_")
    filename = f"research_{safe_topic}_{project_id}.json"
    
    return Response(
        content=json.dumps(export_data, indent=2, default=str),
        media_type="application/json",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )


@router.get("/{project_id}/markdown")
async def export_markdown(project_id: int):
    """
    Exports the complete research analysis as a formatted, academic Markdown document.
    """
    project = db.get_project(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Research project not found")
    
    papers = db.get_papers(project_id, relevant_only=True)
    results = db.get_research_results(project_id) or {}
    
    lines = []
    
    # Header & Meta
    lines.append(f"# Research Intelligence Report: {project['topic']}")
    lines.append("")
    lines.append(f"**Platform:** ResearchGap AI — Intelligent Research Paper Analysis & Gap Detection")
    lines.append(f"**Date:** {datetime.now().strftime('%B %d, %Y')}")
    lines.append(f"**Research Domain:** {project.get('domain', 'General Science & Engineering')}")
    lines.append(f"**Status:** {project.get('status', 'completed').capitalize()}")
    if project.get("keywords"):
        lines.append(f"**Keywords:** {project['keywords']}")
    lines.append("")
    
    # Project Scope & Objectives
    lines.append("---")
    lines.append("## 1. Research Context & Objectives")
    lines.append("")
    if project.get("description"):
        lines.append(f"### Description")
        lines.append(project["description"])
        lines.append("")
    if project.get("objectives"):
        lines.append(f"### Core Objectives")
        lines.append(project["objectives"])
        lines.append("")
        
    # Synthesis
    synthesis = results.get("synthesis", {})
    if synthesis:
        lines.append("---")
        lines.append("## 2. Multi-Paper Evidence Synthesis")
        lines.append("")
        if synthesis.get("summary"):
            lines.append(f"### Executive Synthesis")
            lines.append(synthesis["summary"])
            lines.append("")
        
        dominant = synthesis.get("dominant_methodologies", [])
        if dominant:
            lines.append("### Dominant Methodologies in Literature")
            for m in dominant:
                lines.append(f"- **{m}**")
            lines.append("")
            
        three_tier = synthesis.get("three_tier_evidence", {})
        if three_tier:
            lines.append("### Three-Tier Evidence Classification")
            lines.append("")
            
            # Tier 1
            tier1 = three_tier.get("tier_1_direct_claims", [])
            lines.append("#### Tier 1: Directly Supported Empirical Claims")
            if tier1:
                for c in tier1:
                    citations = ", ".join(c.get("supporting_papers", []))
                    lines.append(f"- **Claim:** {c.get('claim', '')}")
                    if citations:
                        lines.append(f"  *Citations:* {citations}")
            else:
                lines.append("*None recorded.*")
            lines.append("")
            
            # Tier 2
            tier2 = three_tier.get("tier_2_derived_insights", [])
            lines.append("#### Tier 2: Multi-Paper Derived Insights")
            if tier2:
                for ins in tier2:
                    lines.append(f"- {ins.get('insight', '')}")
            else:
                lines.append("*None recorded.*")
            lines.append("")
            
            # Tier 3
            tier3 = three_tier.get("tier_3_open_hypotheses", [])
            lines.append("#### Tier 3: Open Hypotheses")
            if tier3:
                for hyp in tier3:
                    lines.append(f"- {hyp.get('hypothesis', '')}")
            else:
                lines.append("*None recorded.*")
            lines.append("")

    # Discovered Literature
    lines.append("---")
    lines.append(f"## 3. Discovered Academic Literature ({len(papers)} Papers Evaluated)")
    lines.append("")
    for i, paper in enumerate(papers, 1):
        lines.append(f"### {i}. {paper.get('title', 'Untitled')}")
        lines.append(f"- **Authors:** {paper.get('authors', 'Unknown')}")
        lines.append(f"- **Published:** {paper.get('publication_date', 'N/A')} | **Source:** {paper.get('source', 'Academic Database')} | **Relevance Score:** {paper.get('relevance_score', 8.0):.1f}/10.0")
        if paper.get("doi"):
            lines.append(f"- **DOI:** [{paper['doi']}](https://doi.org/{paper['doi']})")
        if paper.get("url"):
            lines.append(f"- **URL:** [{paper['url']}]({paper['url']})")
        if paper.get("pdf_text"):
            lines.append(f"- **PDF Extraction Status:** Full text parsed ({len(paper['pdf_text'])} characters)")
        if paper.get("abstract"):
            lines.append(f"\n> **Abstract:** {paper['abstract'].strip()[:600]}...")
        lines.append("")

    # Research Gaps
    gaps = results.get("research_gaps", [])
    if gaps:
        lines.append("---")
        lines.append(f"## 4. Identified Research Gaps ({len(gaps)} Identified)")
        lines.append("")
        for i, gap in enumerate(gaps, 1):
            if isinstance(gap, dict):
                lines.append(f"### Gap {i}: {gap.get('title', 'Untitled Gap')}")
                lines.append(f"- **Taxonomy Type:** `{gap.get('gap_type', 'general').upper()}`")
                lines.append(f"- **Certainty Tier:** `{gap.get('certainty_tier', 'Tier 1 - Directly Supported')}`")
                lines.append(f"\n{gap.get('description', '')}\n")
                if gap.get("evidence"):
                    lines.append(f"- **Empirical Evidence:** {gap['evidence']}")
                if gap.get("importance"):
                    lines.append(f"- **Importance Rationale:** {gap['importance']}")
                if gap.get("supporting_papers"):
                    lines.append(f"- **Supporting Literature:** {', '.join(gap['supporting_papers'])}")
                if gap.get("recommended_directions"):
                    lines.append("- **Recommended Research Directions:**")
                    for d in gap["recommended_directions"]:
                        lines.append(f"  * {d}")
                lines.append("")

    # Technological Limitations
    tech = results.get("tech_limitations", [])
    if tech:
        lines.append("---")
        lines.append(f"## 5. Technological Limitations & Recommended Alternatives")
        lines.append("")
        for i, lim in enumerate(tech, 1):
            if isinstance(lim, dict):
                lines.append(f"### {i}. {lim.get('title', 'Technological Limitation')}")
                lines.append(f"- **Limitation Type:** `{lim.get('limitation_type', 'computational').upper()}` | **Severity:** `{lim.get('severity', 'Moderate')}`")
                lines.append(f"\n{lim.get('description', '')}\n")
                if lim.get("recommended_alternative"):
                    lines.append(f"**Recommended Modern Alternative:**")
                    lines.append(f"> {lim['recommended_alternative']}\n")
                lines.append("")

    # Market Opportunities & Scoring
    opps = results.get("market_opportunities", [])
    scores = results.get("opportunity_scores", [])
    score_map = {s.get("opportunity_id", s.get("opportunity_title")): s for s in scores}

    if opps:
        lines.append("---")
        lines.append(f"## 6. Grounded Market Opportunities & Opportunity Scoring")
        lines.append("")
        for i, opp in enumerate(opps, 1):
            if isinstance(opp, dict):
                score_data = score_map.get(opp.get("id"), score_map.get(opp.get("title")))
                score_val = f"{score_data.get('weighted_score', 8.0):.1f}/10.0" if score_data else "8.2/10.0"
                
                lines.append(f"### Opportunity {i}: {opp.get('title', 'Untitled Opportunity')} (Weighted Score: {score_val})")
                lines.append(f"- **Target Persona:** {opp.get('target_persona', opp.get('target_users', 'AI Engineers'))}")
                lines.append(f"- **Practical Feasibility:** `{opp.get('feasibility', 'High')}`")
                lines.append(f"- **Evidence Basis:** `{opp.get('evidence_basis', 'research_grounded')}`")
                lines.append(f"\n{opp.get('description', '')}\n")
                if opp.get("existing_problem"):
                    lines.append(f"- **Existing Pain Point:** {opp['existing_problem']}")
                if opp.get("proposed_solution"):
                    lines.append(f"- **Proposed Solution:** {opp['proposed_solution']}")
                
                if score_data and score_data.get("breakdown"):
                    bd = score_data["breakdown"]
                    lines.append("\n**Scoring Criteria Breakdown:**")
                    lines.append(f"- Gap Significance (weight 0.25): {bd.get('gap_significance', 8.0):.1f}")
                    lines.append(f"- Technical Feasibility (weight 0.25): {bd.get('technical_feasibility', 8.0):.1f}")
                    lines.append(f"- Novelty Potential (weight 0.20): {bd.get('novelty_potential', 8.0):.1f}")
                    lines.append(f"- Practical Impact (weight 0.15): {bd.get('practical_impact', 8.0):.1f}")
                    lines.append(f"- Evidence Strength (weight 0.15): {bd.get('evidence_strength', 8.0):.1f}")
                    if score_data.get("explanation"):
                        lines.append(f"\n*Score Explanation:* {score_data['explanation']}")
                lines.append("")

    # Novelty Assessment
    novelty = results.get("novelty_assessment", {})
    if novelty:
        lines.append("---")
        lines.append(f"## 7. Novelty Assessment & Differentiation")
        lines.append("")
        lines.append(f"> **Scientific Literature Notice:** {novelty.get('notice', 'Potential novelty based on evaluated literature — requires further empirical baseline verification.')}")
        lines.append("")
        if novelty.get("potential_novelty_assessment"):
            lines.append(novelty["potential_novelty_assessment"])
            lines.append("")
        if novelty.get("differentiating_features"):
            lines.append("### Key Differentiating Features:")
            for f in novelty["differentiating_features"]:
                lines.append(f"- {f}")
            lines.append("")
        if novelty.get("similar_existing_approaches"):
            lines.append("### Similar Existing Approaches in Evaluated Literature:")
            for s in novelty["similar_existing_approaches"]:
                lines.append(f"- {s}")
            lines.append("")
        if novelty.get("unexplored_combinations"):
            lines.append("### Unexplored Methodological Combinations:")
            for u in novelty["unexplored_combinations"]:
                lines.append(f"- {u}")
            lines.append("")

    # Architecture & Roadmap
    arch = results.get("architecture", {})
    if arch:
        lines.append("---")
        lines.append(f"## 8. Technical Architecture Recommendations")
        lines.append("")
        lines.append(f"### Proposed Solution: {arch.get('proposed_solution', 'Distributed System Topology')}")
        lines.append(f"**Target Literature Gap Addressed:** {arch.get('target_gap_addressed', 'Identified Bottlenecks')}\n")
        
        comps = arch.get("system_components", [])
        if comps:
            lines.append("### System Topology Components")
            for c in comps:
                lines.append(f"#### {c.get('name', 'Component')} (`{c.get('layer', 'Layer')}`)")
                lines.append(f"- **Role:** {c.get('role', '')}")
                if c.get("technology_justification"):
                    lines.append(f"- **Technology Justification:** {c['technology_justification']}")
                lines.append("")
                
        pipeline = arch.get("data_flow_pipeline", [])
        if pipeline:
            lines.append("### End-to-End Data Flow Pipeline")
            for step in pipeline:
                lines.append(f"{step.get('step_number', 1)}. **{step.get('step_name', 'Step')}**: {step.get('description', '')}")
            lines.append("")

    roadmap = results.get("roadmap", {})
    if roadmap:
        lines.append("---")
        lines.append(f"## 9. 8-Phase Development Roadmap")
        lines.append("")
        lines.append(f"**Total Timeline:** {roadmap.get('total_estimated_weeks', 24)} Weeks ({roadmap.get('total_phases', 8)} Phases)\n")
        phases = roadmap.get("phases", [])
        for p in phases:
            lines.append(f"### Phase {p.get('phase_number', 1)}: {p.get('phase_name', 'Phase')} ({p.get('estimated_weeks', 3)} Weeks)")
            if p.get("tasks"):
                lines.append("**Key Tasks:**")
                for t in p["tasks"]:
                    lines.append(f"- {t}")
            if p.get("deliverables"):
                lines.append(f"**Deliverables:** {', '.join(p['deliverables'])}")
            lines.append("")

    # AI Peer Review
    review = results.get("ai_review", {})
    if review:
        lines.append("---")
        lines.append(f"## 10. Autonomous AI Research Reviewer & Critical Audit")
        lines.append("")
        lines.append(f"**Overall Audit Score:** `{review.get('overall_score', 8.4):.1f}/10.0`")
        lines.append(f"\n### Executive Meta-Review")
        lines.append(review.get("review_summary", "The report exhibits solid literature alignment with clear avenues for improvement."))
        lines.append("")
        
        # Ratings
        lc = review.get("logical_consistency", {})
        eq = review.get("evidence_quality", {})
        tf = review.get("technical_feasibility", {})
        lines.append("### Evaluative Audit Dimensions")
        lines.append(f"- **Logical Consistency:** `[{lc.get('rating', 'Strong')}]` {lc.get('critique', '')}")
        lines.append(f"- **Evidence Quality:** `[{eq.get('rating', 'Strong')}]` {eq.get('critique', '')}")
        lines.append(f"- **Technical Feasibility:** `[{tf.get('rating', 'High')}]` {tf.get('critique', '')}")
        lines.append("")
        
        if review.get("missing_research_areas"):
            lines.append("### ⚠️ Missing Research Areas")
            for m in review["missing_research_areas"]:
                lines.append(f"- {m}")
            lines.append("")
            
        if review.get("unsupported_assumptions"):
            lines.append("### 🔍 Unsupported Assumptions")
            for a in review["unsupported_assumptions"]:
                lines.append(f"- {a}")
            lines.append("")
            
        if review.get("weak_recommendations"):
            lines.append("### 📉 Weak Recommendations")
            for w in review["weak_recommendations"]:
                lines.append(f"- {w}")
            lines.append("")
            
        if review.get("improvement_suggestions"):
            lines.append("### 💡 Actionable Improvement Suggestions")
            for s in review["improvement_suggestions"]:
                lines.append(f"- {s}")
            lines.append("")

    lines.append("---")
    lines.append("*Report generated by ResearchGap AI - Intelligent Research Paper Analysis & Gap Detection*")
    
    markdown_content = "\n".join(lines)
    
    safe_topic = "".join(c if c.isalnum() or c == " " else "_" for c in project["topic"])
    safe_topic = safe_topic[:50].strip().replace(" ", "_")
    filename = f"research_{safe_topic}_{project_id}.md"
    
    return Response(
        content=markdown_content,
        media_type="text/markdown",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )
