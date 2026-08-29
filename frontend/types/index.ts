export interface AnalyzeRequest {
  idea: string;
  goal: string;
  domain: string;
  technical_level: string;
  constraints: string;
}

export interface AnalyzeResponse {
  project_id: string;
}

export interface StageProgress {
  name: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  message: string;
}

export interface AnalysisProgress {
  current_stage: number;
  total_stages: number;
  stages: StageProgress[];
}

export interface IdeaAnalysis {
  problem_domain: string;
  core_problem: string;
  target_users: string;
  potential_input: string;
  potential_output: string;
  potential_technologies: string[];
  key_constraints: string[];
  search_queries: string[];
}

export interface Paper {
  id: string;
  title: string;
  authors: string[];
  abstract: string;
  year: number;
  venue: string;
  doi: string | null;
  url: string;
  citation_count: number;
  open_access: boolean;
  pdf_url: string | null;
  source: string;
  relevance_score: number;
  relevance_category: 'DIRECT' | 'RELATED' | 'BACKGROUND' | 'IRRELEVANT';
  relevance_explanation: string;
  extraction_level: 'Full-text PDF analyzed' | 'Abstract-only analysis' | 'Partial-full-text';
  key_method?: string | null;
  key_dataset?: string | null;
  main_finding?: string | null;
  main_limitation?: string | null;
}

export interface ResearchCoverage {
  candidates_retrieved: number;
  unique_papers: number;
  direct_relevant_count: number;
  related_count: number;
  background_count: number;
  full_text_analyzed_count: number;
  abstract_only_count: number;
  open_access_count: number;
  top_papers_count: number;
  sources_searched: string[];
  source_status_messages: string[];
}

export interface PaperExtraction {
  paper_id: string;
  title: string;
  problem: string;
  objective: string;
  methodology: string;
  algorithms: string[];
  models: string[];
  datasets_used: string[];
  dataset_size?: string[];
  features?: string[];
  metrics: string[];
  results: string[];
  strengths: string[];
  limitations: string[];
  future_work: string[];
  key_findings?: string[];
  research_contribution?: string;
  extraction_level: string;
  evidence_type: 'FACT' | 'INFERENCE';
}

export interface MethodComparison {
  paper_title?: string;
  method: string;
  dataset: string;
  performance: string;
  advantages: string;
  limitations: string;
  source_paper_id: string;
  evidence_type: 'FACT' | 'INFERENCE';
  extraction_level?: string;
  comparability_warning: string | null;
}

export interface DatasetInfo {
  name: string;
  domain: string;
  size: string;
  data_type: string;
  classes: string;
  availability: string;
  license: string;
  common_usage: string;
  strengths: string;
  limitations: string;
  potential_gaps: string;
  papers_using?: string[];
  dataset_category?: string;
  evidence_type: 'FACT' | 'INFERENCE';
}

export interface TechnologyInfo {
  name: string;
  category: 'Established' | 'Emerging' | 'Experimental' | 'Potentially Relevant';
  description: string;
  use_cases: string[];
  relevant_papers?: string[];
  advantages?: string;
  limitations?: string;
  maturity_level?: string;
  evidence_type: 'FACT' | 'INFERENCE' | 'HYPOTHESIS' | 'RECOMMENDATION';
}

export interface TechnologyLandscape {
  established: TechnologyInfo[];
  emerging: TechnologyInfo[];
  experimental: TechnologyInfo[];
  potentially_relevant: TechnologyInfo[];
}

export interface ExistingSolution {
  name: string;
  type: 'Academic Model' | 'Open-Source Implementation' | 'Commercial Product' | 'API / Platform' | 'General-Purpose Technology' | 'Academic' | 'Open-source' | 'Commercial' | 'Prototype';
  target_users: string;
  purpose?: string;
  main_features: string[];
  technology: string;
  strengths: string[];
  weaknesses: string[];
  missing_features: string[];
  source: string;
  evidence_type: 'FACT' | 'INFERENCE';
}

export interface Gap {
  title: string;
  type: 'Knowledge' | 'Methodological' | 'Dataset / Data' | 'Evaluation' | 'Technology' | 'Application' | 'Integration' | 'Generalization' | 'Explainability' | 'Deployment';
  description: string;
  evidence: string;
  supporting_sources: string[];
  supporting_evidence_passages?: string[];
  number_of_supporting_papers?: number;
  confidence: 'Low' | 'Medium' | 'Medium-High' | 'High';
  potential_impact: string;
  validation_status: 'Evidence-backed' | 'Strong inference' | 'Possible opportunity' | 'Hypothesis requiring validation';
  reasoning_summary?: string;
}

export interface MarketGap {
  problem: string;
  type: 'Feature' | 'Accessibility' | 'Cost' | 'UX' | 'Geographic' | 'Integration' | 'Automation' | 'Deployment';
  affected_users: string;
  current_solutions: string;
  current_features?: string;
  current_limitations: string;
  missing_capability?: string;
  potential_opportunity: string;
  evidence: string;
  confidence: 'Low' | 'Medium' | 'Medium-High' | 'High';
  validation_required: string;
  evidence_type: 'INFERENCE' | 'HYPOTHESIS';
}

export interface TechnologyGap {
  technology_problem: string;
  current_technology: string;
  limitation: string;
  emerging_technology: string;
  potential_combination: string;
  opportunity: string;
  implementation_difficulty: 'Easy' | 'Medium' | 'Hard' | 'Advanced';
  evidence_type: 'FACT' | 'INFERENCE' | 'HYPOTHESIS';
}

export interface OpportunityScores {
  research_gap: number;
  market_gap: number;
  technology_feasibility: number;
  implementation_difficulty: number;
  data_availability: number;
  innovation_potential: number;
  market_potential: number;
  evidence_confidence: number;
  overall: number;
  weighting_explanation?: string;
}

export interface Opportunity {
  title: string;
  problem: string;
  existing_situation: string;
  identified_gap: string;
  proposed_innovation: string;
  target_users: string;
  required_technologies: string[];
  data_requirements?: string;
  potential_impact: string;
  technical_difficulty: string;
  research_potential: string;
  market_potential: string;
  differentiation_potential?: string;
  novelty_assessment: string;
  evidence_level: 'Evidence-backed' | 'Strong inference' | 'Possible opportunity' | 'Hypothesis requiring validation';
  validation_steps: string[];
  scores: OpportunityScores;
}

export interface ComponentNovelty {
  component: string;
  novelty_level: 'Low' | 'Moderate' | 'High';
  explanation: string;
}

export interface NoveltyAssessment {
  similarity_score: string;
  common_approaches: string[];
  unique_aspects: string[];
  potential_differentiators: string[];
  overcrowded_areas: string[];
  innovation_directions: string[];
  novelty_confidence: string;
  component_assessments: ComponentNovelty[];
  final_assessment: string;
  disclaimer: string;
}

export interface ProjectRecommendation {
  title: string;
  problem_statement: string;
  existing_system: string;
  limitations_of_existing: string[];
  identified_opportunity: string;
  proposed_solution: string;
  core_innovation: string;
  target_users: string;
  key_features: string[];
  technology_stack: string[];
  ai_models: string[];
  datasets: string[];
  apis: string[];
  database: string;
  deployment_strategy: string;
  evaluation_metrics: string[];
  risks: string[];
  development_difficulty: 'Easy' | 'Medium' | 'Hard' | 'Advanced';
  expected_outcome: string;
  future_improvements: string[];
}

export interface ArchitectureComponent {
  name: string;
  description: string;
  technology: string;
  connections: string[];
}

export interface Architecture {
  components: ArchitectureComponent[];
  diagram_description: string;
  data_flow: string[];
}

export interface RoadmapPhase {
  phase_number: number;
  title: string;
  tasks: string[];
  complexity: 'Easy' | 'Medium' | 'Hard' | 'Advanced';
  estimated_duration: string;
}

export interface SourceInfo {
  id: string;
  title: string;
  authors: string[];
  year: number;
  venue: string;
  doi: string | null;
  url: string;
  open_access: boolean;
  citation_count: number;
  pdf_url: string | null;
  relevance_category?: string;
}

export interface ProjectResult {
  id: string;
  idea: string;
  goal: string;
  domain: string;
  technical_level: string;
  constraints: string;
  status: 'pending' | 'analyzing' | 'completed' | 'failed' | 'partial';
  progress: AnalysisProgress;
  idea_analysis: IdeaAnalysis | null;
  top_papers?: Paper[];
  additional_papers?: Paper[];
  background_papers?: Paper[];
  papers: Paper[];
  coverage?: ResearchCoverage | null;
  paper_extractions: PaperExtraction[];
  methods: MethodComparison[];
  datasets: DatasetInfo[];
  technologies: TechnologyLandscape | null;
  existing_solutions: ExistingSolution[];
  research_gaps: Gap[];
  market_gaps: MarketGap[];
  technology_gaps: TechnologyGap[];
  opportunities: Opportunity[];
  novelty: NoveltyAssessment | null;
  recommendation: ProjectRecommendation | null;
  architecture: Architecture | null;
  roadmap: RoadmapPhase[];
  sources: SourceInfo[];
  created_at: string;
  completed_at: string | null;
  error_message: string | null;
}
