import json
import traceback
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update
from app.models.models import Project
from app.schemas.requests import AnalyzeRequest
from app.schemas.responses import AnalysisProgress, StageProgress, ResearchCoverage, SourceInfo
from app.providers.llm_provider import get_llm_provider
from app.providers.openalex import OpenAlexProvider
from app.providers.semantic_scholar import SemanticScholarProvider
from app.providers.arxiv_provider import ArxivProvider
from app.providers.crossref_provider import CrossrefProvider

from app.services.idea_analysis import IdeaAnalysisService
from app.services.research_discovery import ResearchDiscoveryService
from app.services.paper_extraction import PaperExtractionService
from app.services.method_analysis import MethodAnalysisService
from app.services.dataset_analysis import DatasetAnalysisService
from app.services.technology_analysis import TechnologyAnalysisService
from app.services.existing_solutions import ExistingSolutionsService
from app.services.gap_detection import GapDetectionService
from app.services.opportunity_analysis import OpportunityAnalysisService
from app.services.novelty_analysis import NoveltyAnalysisService
from app.services.project_recommendation import ProjectRecommendationService
from app.agents.critic_agent import CriticAgent

class AnalysisPipeline:
    def __init__(self, config):
        self.config = config
        self.llm = get_llm_provider(config)
        
        self.openalex = OpenAlexProvider(config.OPENALEX_EMAIL)
        self.semantic = SemanticScholarProvider(config.SEMANTIC_SCHOLAR_API_KEY)
        self.arxiv = ArxivProvider()
        self.crossref = CrossrefProvider()
        
        self.idea_svc = IdeaAnalysisService(self.llm)
        self.research_svc = ResearchDiscoveryService(config, self.openalex, self.semantic, self.arxiv, self.crossref)
        self.extract_svc = PaperExtractionService(self.llm)
        self.method_svc = MethodAnalysisService(self.llm)
        self.dataset_svc = DatasetAnalysisService(self.llm)
        self.tech_svc = TechnologyAnalysisService(self.llm)
        self.exist_svc = ExistingSolutionsService(self.llm)
        self.gap_svc = GapDetectionService(self.llm)
        self.opp_svc = OpportunityAnalysisService(self.llm)
        self.novel_svc = NoveltyAnalysisService(self.llm)
        self.rec_svc = ProjectRecommendationService(self.llm)
        self.critic = CriticAgent(self.llm)

    async def _update_progress(self, db: AsyncSession, project_id: str, stage: int, stages: list[StageProgress]):
        prog = AnalysisProgress(current_stage=stage, total_stages=11, stages=stages)
        await db.execute(
            update(Project)
            .where(Project.id == project_id)
            .values(progress_data=prog.model_dump_json())
        )
        await db.commit()

    async def run(self, project_id: str, request: AnalyzeRequest, db: AsyncSession):
        stage_names = [
            "Understanding your idea",
            "Expanding research queries",
            "Searching academic sources",
            "Identifying existing methods",
            "Analyzing datasets",
            "Exploring technologies",
            "Mapping existing solutions",
            "Extracting limitations",
            "Detecting potential gaps",
            "Evaluating opportunities",
            "Designing recommended solution"
        ]
        stages = [StageProgress(name=name, status="pending") for name in stage_names]
        
        try:
            if not self.config.has_llm_provider:
                raise ValueError("No LLM provider configured. Please set GEMINI_API_KEY, OPENAI_API_KEY, ANTHROPIC_API_KEY, or GROQ_API_KEY in your .env file.")

            results = {}

            # Stage 1: Understanding Idea
            stages[0].status = "in_progress"
            await self._update_progress(db, project_id, 1, stages)
            idea_analysis = await self.idea_svc.analyze(request.idea, request.goal, request.domain, request.technical_level, request.constraints)
            results['idea_analysis'] = idea_analysis.model_dump()
            stages[0].status = "completed"

            # Stage 2: Expanding Research Queries
            stages[1].status = "completed"

            # Stage 3: Searching Academic Sources & Relevance Classification
            stages[2].status = "in_progress"
            await self._update_progress(db, project_id, 3, stages)
            queries = idea_analysis.search_queries
            candidate_papers, source_messages = await self.research_svc.search(queries, max_papers=60)
            
            if not candidate_papers:
                raise ValueError("Connected academic repositories returned no papers. Please verify your query or check network access.")

            top_papers, additional_papers, background_papers, all_relevant, coverage = await self.research_svc.classify_and_rank(
                candidate_papers, idea_analysis, self.llm
            )
            coverage.source_status_messages = source_messages
            
            results['top_papers'] = [p.model_dump() for p in top_papers]
            results['additional_papers'] = [p.model_dump() for p in additional_papers]
            results['background_papers'] = [p.model_dump() for p in background_papers]
            results['papers'] = [p.model_dump() for p in (top_papers + additional_papers)]
            
            # Format comprehensive bibliography
            sources_list = []
            for p in (top_papers + additional_papers + background_papers):
                sources_list.append(SourceInfo(
                    id=str(p.id),
                    title=p.title,
                    authors=p.authors,
                    year=p.year,
                    venue=p.venue,
                    doi=p.doi,
                    url=p.url,
                    open_access=p.open_access,
                    citation_count=p.citation_count,
                    pdf_url=p.pdf_url,
                    relevance_category=p.relevance_category
                ))
            results['sources'] = [s.model_dump() for s in sources_list]
            stages[2].status = "completed"

            # Stage 4: Full-Text Scientific Extraction & Method Comparison
            stages[3].status = "in_progress"
            await self._update_progress(db, project_id, 4, stages)
            
            # Extract from top core papers (full-text PDF or structured abstract)
            extractions = await self.extract_svc.extract_batch(top_papers)
            results['paper_extractions'] = [e.model_dump() for e in extractions]
            
            # Update extraction counts in coverage
            full_text_count = sum(1 for p in top_papers if p.extraction_level == "Full-text PDF analyzed")
            coverage.full_text_analyzed_count = full_text_count
            coverage.abstract_only_count = len(all_relevant) - full_text_count
            results['coverage'] = coverage.model_dump()

            methods = await self.method_svc.analyze(extractions, top_papers)
            results['methods'] = [m.model_dump() for m in methods]
            stages[3].status = "completed"

            # Stage 5: Dataset Intelligence
            stages[4].status = "in_progress"
            await self._update_progress(db, project_id, 5, stages)
            datasets = await self.dataset_svc.analyze(extractions, top_papers + additional_papers)
            results['datasets'] = [d.model_dump() for d in datasets]
            stages[4].status = "completed"

            # Stage 6: Technology Landscape
            stages[5].status = "in_progress"
            await self._update_progress(db, project_id, 6, stages)
            technologies = await self.tech_svc.analyze(idea_analysis, extractions, top_papers)
            results['technologies'] = technologies.model_dump()
            stages[5].status = "completed"

            # Stage 7: Existing Solutions Mapping
            stages[6].status = "in_progress"
            await self._update_progress(db, project_id, 7, stages)
            solutions = await self.exist_svc.analyze(idea_analysis, top_papers, extractions)
            results['existing_solutions'] = [s.model_dump() for s in solutions]
            stages[6].status = "completed"

            # Stage 8 & 9: Multi-Paper Evidence-Clustered Gaps
            stages[7].status = "completed"
            stages[8].status = "in_progress"
            await self._update_progress(db, project_id, 9, stages)
            
            research_gaps = await self.gap_svc.detect_research_gaps(extractions, top_papers, idea_analysis)
            market_gaps = await self.gap_svc.detect_market_gaps(idea_analysis, solutions, research_gaps)
            tech_gaps = await self.gap_svc.detect_technology_gaps(idea_analysis, technologies, extractions)
            
            results['research_gaps'] = [g.model_dump() for g in research_gaps]
            results['market_gaps'] = [g.model_dump() for g in market_gaps]
            results['technology_gaps'] = [g.model_dump() for g in tech_gaps]
            stages[8].status = "completed"

            # Stage 10: Opportunity Synthesis & Objective Novelty Assessment
            stages[9].status = "in_progress"
            await self._update_progress(db, project_id, 10, stages)
            
            opportunities = await self.opp_svc.analyze(research_gaps, market_gaps, tech_gaps, idea_analysis)
            novelty = await self.novel_svc.analyze(idea_analysis, top_papers, extractions, solutions)
            
            results['opportunities'] = [o.model_dump() for o in opportunities]
            results['novelty'] = novelty.model_dump()
            stages[9].status = "completed"

            # Stage 11: Recommended Project, Architecture & Roadmap
            stages[10].status = "in_progress"
            await self._update_progress(db, project_id, 11, stages)
            
            recommendation = await self.rec_svc.recommend(idea_analysis, opportunities, technologies, research_gaps, novelty)
            architecture = await self.rec_svc.generate_architecture(recommendation, idea_analysis)
            roadmap = await self.rec_svc.generate_roadmap(recommendation)
            
            results['recommendation'] = recommendation.model_dump()
            results['architecture'] = architecture.model_dump()
            results['roadmap'] = [r.model_dump() for r in roadmap]
            
            # Critic Review Validation Pass
            try:
                results = await self.critic.review(results)
            except Exception as e:
                print(f"Critic Agent review error: {e}")

            stages[10].status = "completed"
            await self._update_progress(db, project_id, 11, stages)

            # Persist finalized results
            await db.execute(
                update(Project)
                .where(Project.id == project_id)
                .values(
                    status="completed",
                    results_data=json.dumps(results),
                    completed_at=datetime.now(timezone.utc)
                )
            )
            await db.commit()

        except Exception as e:
            traceback.print_exc()
            current_stage = next((i + 1 for i, s in enumerate(stages) if s.status == "in_progress"), 1)
            for s in stages:
                if s.status == "in_progress":
                    s.status = "failed"
            prog = AnalysisProgress(current_stage=current_stage, total_stages=11, stages=stages)
            await db.execute(
                update(Project)
                .where(Project.id == project_id)
                .values(
                    status="failed",
                    error_message=str(e),
                    progress_data=prog.model_dump_json()
                )
            )
            await db.commit()
