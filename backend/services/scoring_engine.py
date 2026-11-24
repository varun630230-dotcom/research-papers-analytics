"""
ResearchGap AI - Weighted Opportunity Scoring Engine
=====================================================
Calculates transparent, mathematical scores for research and market opportunities
using configurable criteria weights.

Criteria & Default Weights:
1. Research Gap Significance (0.25): Importance and severity of the underlying bottleneck
2. Technical Feasibility (0.25): Near-term engineering viability and toolchain readiness
3. Novelty Potential (0.20): Degree of architectural differentiation from existing works
4. Practical Impact (0.15): Breadth of target user personas and application scope
5. Evidence Strength (0.15): Rigor of empirical evidence and supporting paper citations

Formula:
    Final Score = Σ (Criterion_Score * Criterion_Weight)
    All criterion scores: 1.0 to 10.0
    Final Score range: 1.0 to 10.0
"""

import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger("researchgap.scoring_engine")
logging.basicConfig(level=logging.INFO)

DEFAULT_WEIGHTS = {
    "gap_significance": 0.25,
    "technical_feasibility": 0.25,
    "novelty_potential": 0.20,
    "practical_impact": 0.15,
    "evidence_strength": 0.15,
}


def compute_criterion_scores(opportunity: Dict[str, Any], gap_or_paper_context: Optional[Dict[str, Any]] = None) -> Dict[str, float]:
    """
    Computes individual objective sub-scores (1.0 to 10.0) based on verified
    evidence fields in the opportunity and research gap data.
    """
    # 1. Technical Feasibility (1.0 to 10.0)
    feasibility_raw = opportunity.get("practical_feasibility", "Medium").capitalize()
    if feasibility_raw == "High":
        feasibility_score = 9.0
    elif feasibility_raw == "Medium":
        feasibility_score = 7.0
    else:
        feasibility_score = 4.5
        
    # 2. Evidence Strength (1.0 to 10.0)
    basis = opportunity.get("evidence_basis", "research_grounded").lower()
    if basis == "research_grounded":
        # Grounded directly in paper limitations
        evidence_score = 8.5
    else:
        # Extrapolated market assumption
        evidence_score = 5.5
        
    # 3. Practical Impact (1.0 to 10.0)
    apps = opportunity.get("potential_applications", [])
    app_count = len(apps) if isinstance(apps, list) else 1
    users = opportunity.get("target_users", "")
    # Broad impact if multiple applications and clear personas
    impact_score = min(6.0 + (app_count * 0.8) + (1.0 if len(users) > 30 else 0.5), 10.0)
    impact_score = round(impact_score, 1)
    
    # 4. Research Gap Significance (1.0 to 10.0)
    title_lower = (opportunity.get("title", "") + " " + opportunity.get("existing_problem", "")).lower()
    if any(k in title_lower for k in ["scalability", "safety", "privacy", "bottleneck", "saturation", "latency"]):
        gap_score = 8.8
    else:
        gap_score = 7.2
        
    # 5. Novelty Potential (1.0 to 10.0)
    solution = opportunity.get("proposed_solution", "").lower()
    if any(k in solution for k in ["turnkey", "hybrid", "asynchronous", "adaptive", "plug-and-play", "decentralized"]):
        novelty_score = 8.4
    else:
        novelty_score = 7.0
        
    return {
        "gap_significance": gap_score,
        "technical_feasibility": feasibility_score,
        "novelty_potential": novelty_score,
        "practical_impact": impact_score,
        "evidence_strength": evidence_score,
    }


def score_single_opportunity(
    opportunity: Dict[str, Any],
    weights: Optional[Dict[str, float]] = None
) -> Dict[str, Any]:
    """
    Calculates the weighted opportunity score using the transparent formula.
    
    Returns:
        Structured scoring breakdown with individual criterion scores,
        weights used, final score, and written explanation.
    """
    active_weights = dict(DEFAULT_WEIGHTS)
    if weights and isinstance(weights, dict):
        # Normalize custom weights to sum to 1.0
        total_w = sum(weights.values())
        if total_w > 0:
            active_weights = {k: v / total_w for k, v in weights.items() if k in DEFAULT_WEIGHTS}
            
    # Calculate objective sub-scores
    sub_scores = compute_criterion_scores(opportunity)
    
    # Calculate weighted sum: Σ (score * weight)
    weighted_total = sum(
        sub_scores[k] * active_weights.get(k, 0.2)
        for k in sub_scores
    )
    final_score = round(weighted_total, 2)
    
    # Generate human-readable explanation
    explanation = (
        f"Weighted score {final_score}/10.0 computed using 5 criteria: "
        f"Gap Significance ({sub_scores['gap_significance']} × {active_weights['gap_significance']:.2f}), "
        f"Technical Feasibility ({sub_scores['technical_feasibility']} × {active_weights['technical_feasibility']:.2f}), "
        f"Novelty Potential ({sub_scores['novelty_potential']} × {active_weights['novelty_potential']:.2f}), "
        f"Practical Impact ({sub_scores['practical_impact']} × {active_weights['practical_impact']:.2f}), "
        f"Evidence Strength ({sub_scores['evidence_strength']} × {active_weights['evidence_strength']:.2f}). "
        f"Evidence basis: '{opportunity.get('evidence_basis', 'research_grounded')}', "
        f"Feasibility: '{opportunity.get('practical_feasibility', 'Medium')}'."
    )
    
    return {
        "opportunity_title": opportunity.get("title", "Untitled Opportunity"),
        "gap_significance": sub_scores["gap_significance"],
        "technical_feasibility": sub_scores["technical_feasibility"],
        "novelty_potential": sub_scores["novelty_potential"],
        "practical_impact": sub_scores["practical_impact"],
        "evidence_strength": sub_scores["evidence_strength"],
        "weights_applied": active_weights,
        "weighted_score": final_score,
        "scoring_explanation": explanation,
    }


def score_all_opportunities(
    opportunities: List[Dict[str, Any]],
    weights: Optional[Dict[str, float]] = None
) -> List[Dict[str, Any]]:
    """
    Scores a batch of opportunities and returns them sorted by weighted_score descending.
    """
    logger.info(f"Computing weighted opportunity scores for {len(opportunities)} items...")
    scored = [
        score_single_opportunity(opp, weights)
        for opp in opportunities
    ]
    # Sort highest score first
    ranked = sorted(scored, key=lambda x: x["weighted_score"], reverse=True)
    return ranked
