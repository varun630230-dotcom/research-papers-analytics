from app.schemas.responses import ProjectResult

class ReportGenerationService:
    def generate_markdown(self, project: ProjectResult) -> str:
        md = f"# INNOVATE AI — Research & Innovation Dossier\n\n"
        md += f"**Target Idea:** {project.idea}\n\n"
        md += f"**Domain:** {project.domain} | **Goal:** {project.goal} | **Technical Level:** {project.technical_level}\n\n"
        
        if project.coverage:
            cov = project.coverage
            md += f"### Research Coverage Summary\n"
            md += f"- **Candidate Papers Retrieved:** {cov.candidates_retrieved}\n"
            md += f"- **Unique Papers Evaluated:** {cov.unique_papers}\n"
            md += f"- **Directly Relevant Core Papers:** {cov.direct_relevant_count}\n"
            md += f"- **Full-Text PDFs Analyzed:** {cov.full_text_analyzed_count}\n"
            md += f"- **Abstract-Only Analyses:** {cov.abstract_only_count}\n"
            md += f"- **Connected Academic Sources:** {', '.join(cov.sources_searched)}\n\n"

        if project.recommendation:
            rec = project.recommendation
            md += f"## 1. Recommended Project & Innovation Direction\n"
            md += f"### **{rec.title}**\n\n"
            md += f"**Core Innovation:** {rec.core_innovation}\n\n"
            md += f"**Problem Statement:** {rec.problem_statement}\n\n"
            md += f"**Proposed Solution:** {rec.proposed_solution}\n\n"
            md += f"**Target Users:** {rec.target_users}\n\n"
            md += f"**Key Features:**\n"
            for feat in rec.key_features:
                md += f"- {feat}\n"
            md += f"\n**Technology Stack:** {', '.join(rec.technology_stack)}\n\n"
            md += f"**AI Models:** {', '.join(rec.ai_models)}\n\n"
            md += f"**Evaluation Metrics:** {', '.join(rec.evaluation_metrics)}\n\n"

        top_papers = project.top_papers if project.top_papers else project.papers[:5]
        if top_papers:
            md += f"## 2. Top 5 Verified Core Research Papers\n\n"
            for i, p in enumerate(top_papers, 1):
                md += f"### {i}. {p.title} ({p.year})\n"
                md += f"- **Authors:** {', '.join(p.authors[:4])}\n"
                md += f"- **Relevance Score:** {p.relevance_score}% ({p.relevance_category})\n"
                md += f"- **Extraction Level:** {p.extraction_level}\n"
                md += f"- **Why Selected:** {p.relevance_explanation}\n"
                if p.key_method:
                    md += f"- **Key Method:** {p.key_method}\n"
                if p.main_finding:
                    md += f"- **Main Finding:** {p.main_finding}\n"
                if p.main_limitation:
                    md += f"- **Limitation:** {p.main_limitation}\n"
                if p.url:
                    md += f"- **Source Link:** [{p.source}]({p.url})\n"
                if p.pdf_url:
                    md += f"- **Open-Access PDF:** [View Legal PDF]({p.pdf_url})\n"
                md += "\n"

        if project.research_gaps:
            md += f"## 3. Evidence-Backed Research Gaps\n\n"
            for g in project.research_gaps:
                md += f"### {g.title} `[{g.type} Gap - {g.confidence} Confidence]`\n"
                md += f"{g.description}\n\n"
                md += f"**Synthesized Evidence:** {g.evidence}\n\n"
                md += f"**Supporting Papers ({g.number_of_supporting_papers}):** {', '.join(g.supporting_sources)}\n\n"
                if g.supporting_evidence_passages:
                    md += "**Extracted Passages:**\n"
                    for passg in g.supporting_evidence_passages:
                        md += f"> {passg}\n\n"

        if project.opportunities:
            md += f"## 4. Ranked Opportunities & Feasibility Scores\n\n"
            for opp in project.opportunities:
                md += f"### {opp.title} `[Overall Score: {opp.scores.overall}/100]`\n"
                md += f"**Problem:** {opp.problem}\n\n"
                md += f"**Proposed Innovation:** {opp.proposed_innovation}\n\n"
                md += f"**Score Breakdown:** Research Gap: {opp.scores.research_gap} | Market Evidence: {opp.scores.market_gap} | Tech Feasibility: {opp.scores.technology_feasibility} | Data Availability: {opp.scores.data_availability} | Innovation: {opp.scores.innovation_potential}\n\n"
                md += f"**Validation Roadmap:**\n"
                for step in opp.validation_steps:
                    md += f"- {step}\n"
                md += "\n"

        if project.novelty:
            md += f"## 5. Objective Novelty & Differentiation Assessment\n\n"
            md += f"**Similarity Level:** {project.novelty.similarity_score}\n\n"
            md += f"{project.novelty.final_assessment}\n\n"
            md += f"*{project.novelty.disclaimer}*\n\n"

        if project.roadmap:
            md += f"## 6. 7-Phase Execution Roadmap\n\n"
            for ph in project.roadmap:
                md += f"### Phase {ph.phase_number}: {ph.title} `[{ph.estimated_duration} - {ph.complexity}]`\n"
                for t in ph.tasks:
                    md += f"- {t}\n"
                md += "\n"

        return md

    def generate_json(self, project: ProjectResult) -> str:
        return project.model_dump_json(indent=2)
