from pydantic import BaseModel, ConfigDict
from typing import List, Optional

class BaseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

class AnalyzeResponse(BaseResponse):
    project_id: str

class StageProgress(BaseResponse):
    name: str
    status: str
    message: str = ""

class AnalysisProgress(BaseResponse):
    current_stage: int
    total_stages: int
    stages: List[StageProgress]

class StatusResponse(BaseResponse):
    status: str
    progress: AnalysisProgress

class IdeaAnalysis(BaseResponse):
    problem_domain: str
    core_problem: str
    target_users: str
    potential_input: str
    potential_output: str
    potential_technologies: List[str]
    key_constraints: List[str]
    search_queries: List[str]

class Paper(BaseResponse):
    id: str
    title: str
    authors: List[str]
    abstract: str
    year: int
    venue: str
    doi: Optional[str] = None
    url: str
    citation_count: int = 0
    open_access: bool
    pdf_url: Optional[str] = None
    source: str
    relevance_score: int = 85
    relevance_category: str = "DIRECT"  # DIRECT, RELATED, BACKGROUND, IRRELEVANT
    relevance_explanation: str = ""
    extraction_level: str = "Abstract-only analysis"  # Full-text PDF analyzed, Abstract-only analysis, Partial-full-text
    key_method: Optional[str] = None
    key_dataset: Optional[str] = None
    main_finding: Optional[str] = None
    main_limitation: Optional[str] = None

class ResearchCoverage(BaseResponse):
    candidates_retrieved: int = 0
    unique_papers: int = 0
    direct_relevant_count: int = 0
    related_count: int = 0
    background_count: int = 0
    full_text_analyzed_count: int = 0
    abstract_only_count: int = 0
    open_access_count: int = 0
    top_papers_count: int = 0
    sources_searched: List[str] = []
    source_status_messages: List[str] = []

class PaperExtraction(BaseResponse):
    paper_id: str
    title: str
    problem: str
    objective: str
    methodology: str
    algorithms: List[str]
    models: List[str]
    datasets_used: List[str]
    dataset_size: List[str] = []
    features: List[str] = []
    metrics: List[str]
    results: List[str]
    strengths: List[str]
    limitations: List[str]
    future_work: List[str]
    key_findings: List[str] = []
    research_contribution: str = ""
    extraction_level: str = "Abstract-only analysis"
    evidence_type: str = "FACT"

class MethodComparison(BaseResponse):
    paper_title: str = ""
    method: str
    dataset: str
    performance: str
    advantages: str
    limitations: str
    source_paper_id: str
    evidence_type: str
    extraction_level: str = "Abstract-only"
    comparability_warning: Optional[str] = None

class DatasetInfo(BaseResponse):
    name: str
    domain: str
    size: str
    data_type: str
    classes: str
    availability: str
    license: str = "Unknown"
    common_usage: str
    strengths: str
    limitations: str
    potential_gaps: str
    papers_using: List[str] = []
    dataset_category: str = "Core Dataset"  # Core Dataset, Benchmark Dataset, Background Pretraining Corpus
    evidence_type: str

class TechnologyInfo(BaseResponse):
    name: str
    category: str
    description: str
    use_cases: List[str]
    relevant_papers: List[str] = []
    advantages: str = ""
    limitations: str = ""
    maturity_level: str = "Established"
    evidence_type: str

class TechnologyLandscape(BaseResponse):
    established: List[TechnologyInfo]
    emerging: List[TechnologyInfo]
    experimental: List[TechnologyInfo]
    potentially_relevant: List[TechnologyInfo]

class ExistingSolution(BaseResponse):
    name: str
    type: str  # Academic Model, Open-Source Implementation, Commercial Product, API / Platform, General-Purpose Technology
    target_users: str
    purpose: str = ""
    main_features: List[str]
    technology: str
    strengths: List[str]
    weaknesses: List[str]
    missing_features: List[str]
    source: str
    evidence_type: str

class Gap(BaseResponse):
    title: str
    type: str  # Knowledge, Methodological, Dataset / Data, Evaluation, Technology, Application, Integration, Generalization, Explainability, Deployment
    description: str
    evidence: str
    supporting_sources: List[str] = []
    supporting_evidence_passages: List[str] = []
    number_of_supporting_papers: int = 1
    confidence: str  # Low, Medium, Medium-High, High
    potential_impact: str
    validation_status: str  # Evidence-backed, Strong inference, Possible opportunity, Hypothesis requiring validation
    reasoning_summary: str = ""

class MarketGap(BaseResponse):
    problem: str
    type: str  # Feature, Accessibility, Cost, UX, Geographic, Integration, Automation, Deployment
    affected_users: str
    current_solutions: str
    current_features: str = ""
    current_limitations: str
    missing_capability: str = ""
    potential_opportunity: str
    evidence: str
    confidence: str
    validation_required: str
    evidence_type: str = "INFERENCE"

class TechnologyGap(BaseResponse):
    technology_problem: str
    current_technology: str
    limitation: str
    emerging_technology: str
    potential_combination: str
    opportunity: str
    implementation_difficulty: str
    evidence_type: str

class OpportunityScores(BaseResponse):
    research_gap: int
    market_gap: int
    technology_feasibility: int
    implementation_difficulty: int
    data_availability: int
    innovation_potential: int
    market_potential: int
    evidence_confidence: int
    overall: int
    weighting_explanation: str = "Research Gap: 30% | Market Evidence: 20% | Tech Feasibility: 20% | Data Availability: 10% | Differentiation: 10% | Evidence Confidence: 10%"

class Opportunity(BaseResponse):
    title: str
    problem: str
    existing_situation: str
    identified_gap: str
    proposed_innovation: str
    target_users: str
    required_technologies: List[str]
    data_requirements: str = "Domain-specific labeled validation dataset"
    potential_impact: str
    technical_difficulty: str
    research_potential: str
    market_potential: str
    differentiation_potential: str = "Moderate to High differentiation"
    novelty_assessment: str
    evidence_level: str
    validation_steps: List[str]
    scores: OpportunityScores

class ComponentNovelty(BaseResponse):
    component: str
    novelty_level: str
    explanation: str

class NoveltyAssessment(BaseResponse):
    similarity_score: str  # Low similarity detected, Moderate similarity detected, High similarity detected
    common_approaches: List[str]
    unique_aspects: List[str]
    potential_differentiators: List[str]
    overcrowded_areas: List[str]
    innovation_directions: List[str]
    novelty_confidence: str
    component_assessments: List[ComponentNovelty]
    final_assessment: str
    disclaimer: str

class ProjectRecommendation(BaseResponse):
    title: str
    problem_statement: str
    existing_system: str
    limitations_of_existing: List[str]
    identified_opportunity: str
    proposed_solution: str
    core_innovation: str
    target_users: str
    key_features: List[str]
    technology_stack: List[str]
    ai_models: List[str]
    datasets: List[str]
    apis: List[str]
    database: str
    deployment_strategy: str
    evaluation_metrics: List[str]
    risks: List[str]
    development_difficulty: str
    expected_outcome: str
    future_improvements: List[str]

class ArchitectureComponent(BaseResponse):
    name: str
    description: str
    technology: str
    connections: List[str]

class Architecture(BaseResponse):
    components: List[ArchitectureComponent]
    diagram_description: str
    data_flow: List[str]

class RoadmapPhase(BaseResponse):
    phase_number: int
    title: str
    tasks: List[str]
    complexity: str
    estimated_duration: str

class SourceInfo(BaseResponse):
    id: str
    title: str
    authors: List[str]
    year: int
    venue: str
    doi: Optional[str] = None
    url: str
    open_access: bool
    citation_count: int = 0
    pdf_url: Optional[str] = None
    relevance_category: str = "DIRECT"

class ExportResponse(BaseResponse):
    content: str
    filename: str

class ProjectResult(BaseResponse):
    id: str
    idea: str
    goal: str
    domain: str
    technical_level: str
    constraints: str
    status: str
    progress: AnalysisProgress
    idea_analysis: Optional[IdeaAnalysis] = None
    top_papers: List[Paper] = []
    additional_papers: List[Paper] = []
    background_papers: List[Paper] = []
    papers: List[Paper] = []
    coverage: Optional[ResearchCoverage] = None
    paper_extractions: List[PaperExtraction] = []
    methods: List[MethodComparison] = []
    datasets: List[DatasetInfo] = []
    technologies: Optional[TechnologyLandscape] = None
    existing_solutions: List[ExistingSolution] = []
    research_gaps: List[Gap] = []
    market_gaps: List[MarketGap] = []
    technology_gaps: List[TechnologyGap] = []
    opportunities: List[Opportunity] = []
    novelty: Optional[NoveltyAssessment] = None
    recommendation: Optional[ProjectRecommendation] = None
    architecture: Optional[Architecture] = None
    roadmap: List[RoadmapPhase] = []
    sources: List[SourceInfo] = []
    created_at: str
    completed_at: Optional[str] = None
    error_message: Optional[str] = None
