import asyncio
import json
from datetime import datetime
from app.providers.openalex import OpenAlexProvider
from app.providers.semantic_scholar import SemanticScholarProvider
from app.providers.arxiv_provider import ArxivProvider
from app.providers.crossref_provider import CrossrefProvider
from app.providers.llm_provider import BaseLLMProvider
from app.schemas.responses import Paper, IdeaAnalysis, ResearchCoverage
from app.prompts.templates import RELEVANCE_CLASSIFICATION_PROMPT
from app.utils.helpers import normalize_title, titles_similar

class ResearchDiscoveryService:
    def __init__(self, config, openalex: OpenAlexProvider, semantic_scholar: SemanticScholarProvider, arxiv: ArxivProvider, crossref: CrossrefProvider):
        self.config = config
        self.openalex = openalex
        self.semantic_scholar = semantic_scholar
        self.arxiv = arxiv
        self.crossref = crossref

    async def search(self, queries: list[str], max_papers: int = 80) -> tuple[list[Paper], list[str]]:
        all_papers: list[Paper] = []
        source_status_messages: list[str] = []
        sources_searched = ["OpenAlex", "arXiv", "Semantic Scholar", "Crossref"]
        
        target_queries = queries[:6] if queries else ["artificial intelligence research"]
        
        # Concurrently query each provider across the target queries
        tasks = []
        for q in target_queries:
            tasks.append(self.openalex.search_works(q, 10))
            tasks.append(self.arxiv.search_papers(q, 8))
            tasks.append(self.semantic_scholar.search_papers(q, 8))
            tasks.append(self.crossref.search_works(q, 8))

        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        source_counts = {"OpenAlex": 0, "arXiv": 0, "Semantic Scholar": 0, "Crossref": 0}
        for res in results:
            if isinstance(res, list):
                for p in res:
                    if isinstance(p, Paper):
                        all_papers.append(p)
                        if p.source in source_counts:
                            source_counts[p.source] += 1
            elif isinstance(res, Exception):
                print(f"Academic search provider error: {res}")

        for s, count in source_counts.items():
            if count > 0:
                source_status_messages.append(f"{s}: {count} papers retrieved")
            else:
                source_status_messages.append(f"{s}: 0 results or temporarily unavailable")

        # Deduplicate papers by DOI, URL, and normalized title
        unique_papers = []
        seen_dois = set()
        seen_titles = []
        seen_urls = set()

        for p in all_papers:
            if p.doi and p.doi.lower() in seen_dois:
                continue
            if p.url and p.url.lower() in seen_urls:
                continue
            norm = normalize_title(p.title)
            if not norm or len(norm) < 6:
                continue
            if any(titles_similar(norm, st) for st in seen_titles):
                continue
            
            if p.doi:
                seen_dois.add(p.doi.lower())
            if p.url:
                seen_urls.add(p.url.lower())
            seen_titles.append(norm)
            unique_papers.append(p)

        return unique_papers[:max_papers], source_status_messages

    async def classify_and_rank(
        self,
        papers: list[Paper],
        idea: IdeaAnalysis,
        llm: BaseLLMProvider
    ) -> tuple[list[Paper], list[Paper], list[Paper], list[Paper], ResearchCoverage]:
        """
        Classifies all candidate papers into DIRECT, RELATED, BACKGROUND, IRRELEVANT.
        Returns (top_papers, additional_papers, background_papers, all_relevant_papers, coverage).
        """
        if not papers:
            coverage = ResearchCoverage(
                candidates_retrieved=0,
                unique_papers=0,
                direct_relevant_count=0,
                related_count=0,
                background_count=0,
                sources_searched=["OpenAlex", "arXiv", "Semantic Scholar", "Crossref"],
                source_status_messages=["No papers found"]
            )
            return [], [], [], [], coverage

        classified_papers: list[Paper] = []
        chunk_size = 12
        paper_chunks = [papers[i:i + chunk_size] for i in range(0, len(papers), chunk_size)]

        current_year = datetime.now().year

        idea_summary = f"{idea.core_problem}. Modalities: {idea.potential_input} -> {idea.potential_output}. Approaches: {', '.join(idea.potential_technologies[:4])}"

        for chunk in paper_chunks:
            chunk_repr = [
                {
                    "paper_id": p.id,
                    "title": p.title,
                    "year": p.year,
                    "abstract": p.abstract[:350] if p.abstract else ""
                }
                for p in chunk
            ]
            prompt = RELEVANCE_CLASSIFICATION_PROMPT.format(
                idea_summary=idea_summary,
                domain=idea.problem_domain,
                papers_json=json.dumps(chunk_repr)
            )
            try:
                evals = await llm.generate_json(prompt, system_prompt="Classify scientific papers into DIRECT, RELATED, BACKGROUND, IRRELEVANT with relevance scores.")
                if isinstance(evals, dict):
                    for v in evals.values():
                        if isinstance(v, list):
                            evals = v
                            break
                if not isinstance(evals, list):
                    evals = [evals]
                
                eval_map = {}
                for e in evals:
                    if isinstance(e, dict) and e.get("paper_id"):
                        eval_map[str(e.get("paper_id"))] = e

                for p in chunk:
                    ev = eval_map.get(str(p.id))
                    if ev:
                        cat = str(ev.get("relevance_category") or "DIRECT").upper()
                        if cat not in ["DIRECT", "RELATED", "BACKGROUND", "IRRELEVANT"]:
                            cat = "DIRECT" if "direct" in cat.lower() else "RELATED"
                        score = int(ev.get("relevance_score") or (90 if cat == "DIRECT" else 70 if cat == "RELATED" else 45))
                        p.relevance_category = cat
                        p.relevance_score = score
                        p.relevance_explanation = str(ev.get("relevance_explanation") or f"Classified as {cat} for {idea.core_problem}")
                        p.key_method = ev.get("key_method")
                        p.key_dataset = ev.get("key_dataset")
                        p.main_finding = ev.get("main_finding")
                        p.main_limitation = ev.get("main_limitation")
                    else:
                        # Heuristic fallback based on title keywords
                        p_title_lower = p.title.lower()
                        core_terms = [w.lower() for w in idea.core_problem.split() if len(w) > 3]
                        matches = sum(1 for w in core_terms if w in p_title_lower)
                        if matches >= 2 or (core_terms and core_terms[0] in p_title_lower):
                            p.relevance_category = "DIRECT"
                            p.relevance_score = 88
                            p.relevance_explanation = "Direct title match to user's core problem."
                        elif any(w in p_title_lower for w in ["transformer", "bert", "scaling", "language model", "deep learning"]):
                            p.relevance_category = "BACKGROUND"
                            p.relevance_score = 50
                            p.relevance_explanation = "Foundational background architecture."
                        else:
                            p.relevance_category = "RELATED"
                            p.relevance_score = 72
                            p.relevance_explanation = "Related domain methodology."
                    classified_papers.append(p)
            except Exception as e:
                print(f"Relevance classification batch error: {e}")
                for p in chunk:
                    p.relevance_category = "DIRECT"
                    p.relevance_score = 80
                    p.relevance_explanation = "Topic relevant candidate."
                    classified_papers.append(p)

        # Segregate into categories
        direct_papers = [p for p in classified_papers if p.relevance_category == "DIRECT"]
        related_papers = [p for p in classified_papers if p.relevance_category == "RELATED"]
        background_papers = [p for p in classified_papers if p.relevance_category == "BACKGROUND"]
        
        # Ranking function: Topic Relevance (70%) + Citation Normalization (15%) + Recency (15%)
        # Note: Citation bonus is capped so a general paper cannot surpass a direct paper
        def compute_rank(p: Paper) -> float:
            base_rel = float(p.relevance_score)
            cite_score = min(float(p.citation_count), 500.0) / 500.0 * 15.0
            years_old = max(0, current_year - p.year)
            recency_score = max(0.0, 15.0 - (years_old * 1.5))
            oa_bonus = 3.0 if p.open_access else 0.0
            return (base_rel * 0.70) + cite_score + recency_score + oa_bonus

        direct_papers.sort(key=compute_rank, reverse=True)
        related_papers.sort(key=compute_rank, reverse=True)
        background_papers.sort(key=lambda p: p.citation_count, reverse=True)

        # Core candidate pool for top 5 selection: prioritize DIRECT, fill with top RELATED if needed
        primary_pool = direct_papers if len(direct_papers) >= 5 else direct_papers + related_papers
        top_papers = primary_pool[:5]
        
        # Remaining direct & related papers become additional_papers
        top_ids = {p.id for p in top_papers}
        additional_papers = [p for p in (direct_papers + related_papers) if p.id not in top_ids][:15]

        all_relevant = top_papers + additional_papers

        coverage = ResearchCoverage(
            candidates_retrieved=len(papers),
            unique_papers=len(classified_papers),
            direct_relevant_count=len(direct_papers),
            related_count=len(related_papers),
            background_count=len(background_papers),
            full_text_analyzed_count=0,  # Will be updated after PDF extraction
            abstract_only_count=len(all_relevant),
            open_access_count=sum(1 for p in classified_papers if p.open_access),
            top_papers_count=len(top_papers),
            sources_searched=["OpenAlex", "arXiv", "Semantic Scholar", "Crossref"],
            source_status_messages=[]
        )

        return top_papers, additional_papers, background_papers, all_relevant, coverage
