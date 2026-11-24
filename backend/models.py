"""
ResearchGap AI - Pydantic Models
==================================
Defines data shapes for API request/response validation.

Pydantic models serve two purposes here:
1. INPUT VALIDATION: Ensures the user sends correct data to our API
2. RESPONSE SHAPING: Defines what our API returns to the frontend

Why Pydantic?
- FastAPI uses it natively for automatic validation
- Provides clear error messages when data is wrong
- Documents the API automatically through OpenAPI/Swagger
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# =============================================================================
# REQUEST MODELS (what the user sends to us)
# =============================================================================

class ResearchRequest(BaseModel):
    """
    The input a user provides to start a research analysis.
    
    Only 'topic' is required. Everything else helps improve results
    but has sensible defaults.
    """
    topic: str = Field(
        ...,  # ... means "required"
        min_length=3,
        max_length=500,
        description="The main research topic or idea to analyze",
        examples=["Federated learning for healthcare data privacy"]
    )
    description: str = Field(
        default="",
        max_length=2000,
        description="Detailed description of the research idea"
    )
    domain: str = Field(
        default="",
        max_length=200,
        description="Research domain (e.g., 'Machine Learning', 'Cybersecurity')"
    )
    keywords: str = Field(
        default="",
        max_length=500,
        description="Comma-separated keywords to refine the search"
    )
    objectives: str = Field(
        default="",
        max_length=2000,
        description="What the researcher wants to achieve"
    )


# =============================================================================
# RESPONSE MODELS (what our API returns)
# =============================================================================

class ProjectSummary(BaseModel):
    """Brief project info for history/listing views."""
    id: int
    topic: str
    domain: str = ""
    status: str = "pending"
    total_papers_found: int = 0
    relevant_papers: int = 0
    created_at: str = ""


class PaperResponse(BaseModel):
    """A single research paper's information."""
    id: int
    title: str
    authors: str = ""
    abstract: str = ""
    publication_date: str = ""
    doi: str = ""
    url: str = ""
    pdf_url: str = ""
    source: str = ""
    relevance_score: float = 0.0
    is_relevant: bool = True


class ResearchGap(BaseModel):
    """A single identified research gap."""
    title: str
    description: str
    gap_type: str = ""  # methodological, dataset, performance, etc.
    evidence: str = ""
    supporting_papers: List[str] = []
    importance: str = ""
    potential_direction: str = ""


class TechLimitation(BaseModel):
    """A technological limitation found across papers."""
    title: str
    description: str
    limitation_type: str = ""
    affected_papers: List[str] = []
    suggested_alternatives: str = ""


class MarketOpportunity(BaseModel):
    """A market opportunity derived from research gaps."""
    title: str
    description: str
    target_users: str = ""
    existing_problem: str = ""
    proposed_solution: str = ""
    feasibility: str = ""
    applications: str = ""
    evidence_basis: str = ""  # research-based vs assumption


class OpportunityScore(BaseModel):
    """Weighted scoring for a research opportunity."""
    opportunity_title: str
    gap_significance: float = 0.0
    technical_feasibility: float = 0.0
    novelty_potential: float = 0.0
    practical_impact: float = 0.0
    evidence_strength: float = 0.0
    weighted_score: float = 0.0
    scoring_explanation: str = ""


class FullResearchResponse(BaseModel):
    """
    Complete research analysis response.
    This is what the dashboard displays.
    """
    project: ProjectSummary
    papers: List[PaperResponse] = []
    synthesis: dict = {}
    research_gaps: List[dict] = []
    tech_limitations: List[dict] = []
    market_opportunities: List[dict] = []
    opportunity_scores: List[dict] = []
    novelty_assessment: dict = {}
    architecture: dict = {}
    roadmap: dict = {}
    ai_review: dict = {}


class HealthResponse(BaseModel):
    """API health check response."""
    status: str
    version: str
    database: str
    gemini_configured: bool
    timestamp: str


class ErrorResponse(BaseModel):
    """Standard error response."""
    error: str
    detail: str = ""
