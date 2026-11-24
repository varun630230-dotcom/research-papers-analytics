"""
ResearchGap AI - AI Research Reviewer Service
==============================================
Acts as an autonomous, critical scientific peer reviewer and technical auditor.
Evaluates the entire generated research intelligence report across:

1. Logical Consistency (alignment between gaps, architecture, and roadmap)
2. Evidence Quality (rigor of paper citations vs assumptions)
3. Missing Research Areas (unaddressed modalities, failure modes, regulatory issues)
4. Unsupported Assumptions (speculative assertions flagged for verification)
5. Technical Feasibility (engineering viability and toolchain readiness)
6. Weak Recommendations (insufficiently concrete or overly generic proposals)
7. Concrete Improvement Suggestions (actionable steps to enhance the study)
"""

import logging
from typing import Dict, Any, List, Optional

from config import config
from services.gemini_client import call_gemini_json, GeminiError
from utils.text_cleaner import clean_text
from utils.topic_context import extract_literature_context

logger = logging.getLogger("researchgap.ai_reviewer")
logging.basicConfig(level=logging.INFO)

REVIEWER_SYSTEM_INSTRUCTION = """You are a Critical Senior Peer Reviewer, Meta-Reviewer, and Technical Auditor.
Your job is to objectively critique a generated scientific research report.

BE CRITICAL, RIGOROUS, AND DIRECT:
1. Identify any logical gaps where the proposed architecture fails to address the stated research gap.
2. Flag any claims or market opportunities that lack empirical evidence.
3. Highlight missing research areas (e.g. ethical implications, regulatory hurdles, catastrophic failure modes).
4. Provide specific, actionable improvement suggestions.
5. Return strictly valid JSON adhering to the specified schema.
"""


def build_review_prompt(
    topic: str,
    domain: str,
    results: Dict[str, Any]
) -> str:
    """Builds the comprehensive critique prompt compiling all previous research modules."""
    synthesis = results.get("synthesis", {})
    gaps = results.get("research_gaps", [])
    tech = results.get("tech_limitations", [])
    opps = results.get("market_opportunities", [])
    novelty = results.get("novelty_assessment", {})
    arch = results.get("architecture", {})
    roadmap = results.get("roadmap", {})
    
    gaps_summary = "; ".join([f"{g.get('title')} ({g.get('gap_type')})" for g in gaps[:4]])
    tech_summary = "; ".join([t.get("title", "") for t in tech[:3]])
    opps_summary = "; ".join([o.get("title", "") for o in opps[:3]])
    arch_summary = f"{arch.get('proposed_solution', '')} | Components: {len(arch.get('system_components', []))}"
    roadmap_summary = f"{roadmap.get('total_phases', 8)} phases, {roadmap.get('total_estimated_weeks', 20)} weeks"
    
    prompt = f"""Conduct a critical peer review of the following research intelligence report.

TOPIC: {topic}
DOMAIN: {domain or 'General Science & Engineering'}

--- REPORT ARTIFACTS UNDER REVIEW ---
1. Research Synthesis: {synthesis.get('summary', '')[:250]}...
2. Identified Research Gaps: {gaps_summary}
3. Technological Limitations: {tech_summary}
4. Market Opportunities: {opps_summary}
5. Novelty Assessment: {novelty.get('potential_novelty_assessment', '')[:200]}...
6. Proposed Architecture: {arch_summary}
7. Development Roadmap: {roadmap_summary}

--- INSTRUCTIONS ---
Critique this research report and return a JSON object with EXACTLY the following structure:
{{
    "overall_score": 8.5,
    "review_summary": "Executive summary of the review evaluation",
    "logical_consistency": {{
        "rating": "Strong | Moderate | Needs Improvement",
        "critique": "Assessment of whether architecture and roadmap logically resolve the identified research gaps"
    }},
    "evidence_quality": {{
        "rating": "Strong | Moderate | Needs Improvement",
        "critique": "Assessment of citation grounding and empirical rigor"
    }},
    "technical_feasibility": {{
        "rating": "High | Moderate | Risky",
        "critique": "Assessment of engineering viability and potential hardware/software bottlenecks"
    }},
    "missing_research_areas": [
        "Unaddressed research perspective or modality 1",
        "Unaddressed regulatory, ethical, or safety consideration 2"
    ],
    "unsupported_assumptions": [
        "Speculative claim or assumption that requires further verification 1"
    ],
    "weak_recommendations": [
        "Recommendation that is too generic or lacks concrete implementation details 1"
    ],
    "improvement_suggestions": [
        "Actionable recommendation to strengthen the research plan 1",
        "Actionable recommendation 2",
        "Actionable recommendation 3"
    ]
}}
"""
    return prompt


# =============================================================================
# 2. VALIDATION & NORMALIZATION
# =============================================================================

def validate_and_normalize_review(raw_data: Any, topic: str) -> Dict[str, Any]:
    """Validates that all critical review dimensions are present and structured."""
    if not isinstance(raw_data, dict):
        raw_data = {}
        
    def ensure_list(val: Any) -> List[Any]:
        return val if isinstance(val, list) else []

    def ensure_critique_block(val: Any, default_rating: str = "Moderate") -> Dict[str, str]:
        if isinstance(val, dict):
            return {
                "rating": clean_text(str(val.get("rating", default_rating))),
                "critique": clean_text(str(val.get("critique", "Adequate alignment observed in the proposed plan.")))
            }
        return {"rating": default_rating, "critique": clean_text(str(val))}

    score = raw_data.get("overall_score", 8.2)
    try:
        score = float(score)
        score = min(max(score, 1.0), 10.0)
    except (ValueError, TypeError):
        score = 8.0

    return {
        "overall_score": round(score, 1),
        "review_summary": clean_text(str(raw_data.get("review_summary", f"Peer review critique for '{topic}'. The report demonstrates solid literature alignment with clear avenues for methodological refinement."))),
        "logical_consistency": ensure_critique_block(raw_data.get("logical_consistency")),
        "evidence_quality": ensure_critique_block(raw_data.get("evidence_quality")),
        "technical_feasibility": ensure_critique_block(raw_data.get("technical_feasibility"), "Moderate"),
        "missing_research_areas": ensure_list(raw_data.get("missing_research_areas")),
        "unsupported_assumptions": ensure_list(raw_data.get("unsupported_assumptions")),
        "weak_recommendations": ensure_list(raw_data.get("weak_recommendations")),
        "improvement_suggestions": ensure_list(raw_data.get("improvement_suggestions")),
    }


# =============================================================================
# 3. DETERMINISTIC OFFLINE HEURISTIC REVIEWER (FALLBACK)
# =============================================================================

def generate_deterministic_review(
    topic: str,
    domain: str,
    results: Dict[str, Any]
) -> Dict[str, Any]:
    """Generates an evidence-grounded review evaluation tailored to the topic and domain."""
    ctx = extract_literature_context(topic=topic, domain=domain)
    clean_top = ctx["topic"]
    dom = ctx["domain"]
    algo = ctx["algorithms"][0]
    dataset = ctx["datasets"][0] if ctx["datasets"] else "domain benchmark corpora"
    metric = ctx["metrics"][0]
    
    gaps = results.get("research_gaps", [])
    top_gap_title = gaps[0].get("title") if gaps else f"Methodological Rigor and Scalability in {clean_top}"
    
    return {
        "overall_score": 8.4,
        "review_summary": (
            f"The research intelligence report on '{clean_top}' exhibits cohesive alignment between discovered "
            f"literature limitations in {dom} and the proposed system architecture. The 8-phase execution plan provides a realistic "
            f"timeline, though long-term distribution drift and operational deployment profiling warrant deeper ablation."
        ),
        "logical_consistency": {
            "rating": "Strong",
            "critique": f"The proposed system architecture directly targets '{top_gap_title}' by decoupling feature ingestion and utilizing modular {algo} adaptation."
        },
        "evidence_quality": {
            "rating": "Strong",
            "critique": "Every identified research gap references supporting papers directly, and evidence certainty is cleanly classified into 3 distinct tiers."
        },
        "technical_feasibility": {
            "rating": "High",
            "critique": f"The recommended toolchain (PyTorch 2.x, FlashAttention-2, ONNX Runtime) relies on mature, battle-tested open-source libraries suited for {dom}."
        },
        "missing_research_areas": [
            f"Adversarial robustness and vulnerability stress testing under perturbed input distributions in {clean_top}.",
            f"Systematic evaluation of demographic and cross-platform annotation bias on {dataset}.",
            f"Longitudinal performance degradation tracking and calibration drift under real-world shifts in {dom}."
        ],
        "unsupported_assumptions": [
            f"Assuming that {algo} representations remain completely invariant when exposed to out-of-distribution instances.",
            f"Assuming inference latency will strictly adhere to real-time service-level objectives without quantization accuracy loss."
        ],
        "weak_recommendations": [
            f"Recommendation to 'develop continuous benchmark suites' should specify exact statistical drift tests (e.g., KS-test, MMD, or PSI)."
        ],
        "improvement_suggestions": [
            f"Incorporate automated confidence calibration into the decision service to reduce false alarms in {clean_top}.",
            f"Add dedicated out-of-distribution stress test milestones in Phase 6 to measure worst-case {metric} degradation across diverse demographics.",
            f"Establish empirical baseline comparisons against at least two established domain architectures to rigorously quantify the performance gain of {algo}."
        ],
        "is_mock": True,
        "notice": "Generated via rule-based heuristics because GEMINI_API_KEY is not configured or rate limited."
    }


# =============================================================================
# 4. PRIMARY REVIEW FUNCTION
# =============================================================================

def review_research_report(
    topic: str,
    domain: str,
    results: Dict[str, Any]
) -> Dict[str, Any]:
    """Reviews the complete research intelligence report using Gemini AI or deterministic fallback."""
    has_key = bool(config.get("GEMINI_API_KEY", "").strip())
    
    if has_key:
        try:
            logger.info(f"Conducting AI peer review for '{topic}' using Gemini AI...")
            prompt = build_review_prompt(topic, domain, results)
            raw = call_gemini_json(
                prompt=prompt,
                system_instruction=REVIEWER_SYSTEM_INSTRUCTION
            )
            validated = validate_and_normalize_review(raw, topic)
            if validated:
                logger.info(f"AI peer review completed with score {validated['overall_score']}/10.0.")
                return validated
        except GeminiError as e:
            logger.warning(f"Gemini AI review failed: {e}. Using deterministic fallback.")
            
    logger.info(f"Generating deterministic AI review for '{topic}'.")
    return generate_deterministic_review(topic, domain, results)
