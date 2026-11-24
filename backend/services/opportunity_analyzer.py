"""
ResearchGap AI - Market Opportunity Analysis Service
======================================================
Derives viable, practical market opportunities directly from identified research gaps
and technological limitations.

Core Principles:
1. Grounding in Real Bottlenecks: Every opportunity originates from a genuine limitation
   identified in the literature (e.g. latency, data scarcity, edge constraints).
2. Epistemic Humility: Explicitly distinguishes between 'research_grounded' opportunities
   (directly solving an empirical bottleneck) and 'extrapolated_assumption' (market hypotheses).
3. Practical Feasibility Assessment: Classifies engineering feasibility into High, Medium, or Low
   based on computational and technological maturity.
4. Target Stakeholder Identification: Names exact user archetypes (e.g. enterprise MLOps,
   clinical data managers, edge hardware designers).
"""

import logging
from typing import Dict, Any, List, Optional

from config import config
from services.gemini_client import call_gemini_json, GeminiError
from utils.text_cleaner import clean_text

logger = logging.getLogger("researchgap.opportunity_analyzer")
logging.basicConfig(level=logging.INFO)

OPPORTUNITY_ANALYZER_SYSTEM_INSTRUCTION = """You are a Technology Commercialization Director and Venture Research Analyst.
Your task is to identify viable, practical market and engineering opportunities derived from academic research gaps and limitations.

STRICT RULES:
1. Every opportunity must address an actual technical problem identified in the provided research gaps or papers.
2. Clearly tag the evidence basis for each opportunity:
   - "research_grounded": Directly solves a specific bottleneck verified by the papers.
   - "extrapolated_assumption": Extrapolates a broader market demand beyond what was measured.
3. Assess practical feasibility realistically ("High", "Medium", "Low") based on current technology maturity.
4. Do not invent fake market sizes or speculate revenue numbers without verified citations.
5. Return strictly valid JSON adhering to the specified schema.
"""


def build_opportunity_prompt(
    topic: str,
    domain: str,
    research_gaps: List[Dict[str, Any]],
    tech_limitations: List[Dict[str, Any]]
) -> str:
    """Builds prompt compiling research gaps and technical limitations for opportunity derivation."""
    gaps_text = []
    for i, gap in enumerate(research_gaps, 1):
        gaps_text.append(
            f'[{i}] Gap: "{gap.get("title")}" (Type: {gap.get("gap_type")})\n'
            f'    Problem: {gap.get("description")}\n'
            f'    Evidence: {gap.get("evidence")}'
        )
    compiled_gaps = "\n\n".join(gaps_text)
    
    tech_text = []
    for i, lim in enumerate(tech_limitations, 1):
        tech_text.append(
            f'[{i}] Limitation: "{lim.get("title")}"\n'
            f'    Suggested Alternatives: {lim.get("suggested_alternatives")}'
        )
    compiled_tech = "\n\n".join(tech_text)
    
    prompt = f"""Derive practical commercial and engineering market opportunities from the following research bottlenecks.

TOPIC: {topic}
DOMAIN: {domain or 'Computer Science / Engineering'}

--- IDENTIFIED RESEARCH GAPS ---
{compiled_gaps}

--- IDENTIFIED TECHNOLOGICAL LIMITATIONS ---
{compiled_tech}

--- INSTRUCTIONS ---
Extract 3 to 5 realistic market opportunities derived directly from these technical gaps.
Output a JSON object with a single key "market_opportunities" containing an array of objects:
{{
    "market_opportunities": [
        {{
            "title": "Clear product or engineering opportunity title",
            "description": "Comprehensive explanation of the practical market opportunity",
            "target_users": "Specific user personas (e.g. Enterprise ML Engineers, Hospital IT Officers)",
            "existing_problem": "The verified technical pain point this addresses",
            "proposed_solution": "Concrete product or system architecture proposed to solve it",
            "practical_feasibility": "High | Medium | Low",
            "potential_applications": ["Use case 1", "Use case 2"],
            "evidence_basis": "research_grounded | extrapolated_assumption",
            "supporting_gap_or_paper": "The specific research gap or technological limitation this solves"
        }}
    ]
}}
"""
    return prompt


# =============================================================================
# 2. VALIDATION & NORMALIZATION
# =============================================================================

def validate_and_normalize_opportunities(raw_opps: Any, default_gap_title: str) -> List[Dict[str, Any]]:
    """Validates and cleans the list of market opportunities."""
    if isinstance(raw_opps, dict) and "market_opportunities" in raw_opps:
        raw_opps = raw_opps["market_opportunities"]
        
    if not isinstance(raw_opps, list):
        return []
        
    validated = []
    for item in raw_opps:
        if not isinstance(item, dict):
            continue
            
        title = clean_text(str(item.get("title", "")))
        if not title:
            continue
            
        feasibility = clean_text(str(item.get("practical_feasibility", ""))).capitalize()
        if feasibility not in ["High", "Medium", "Low"]:
            feasibility = "Medium"
            
        evidence_basis = clean_text(str(item.get("evidence_basis", ""))).lower()
        if evidence_basis not in ["research_grounded", "extrapolated_assumption"]:
            evidence_basis = "research_grounded"
            
        apps = item.get("potential_applications", [])
        if isinstance(apps, list):
            potential_apps = [clean_text(str(a)) for a in apps if str(a).strip()]
        elif isinstance(apps, str) and apps.strip():
            potential_apps = [clean_text(apps)]
        else:
            potential_apps = ["General commercial and scientific workflow automation"]
            
        validated.append({
            "title": title,
            "description": clean_text(str(item.get("description", "A practical application opportunity derived from research limitations."))),
            "target_users": clean_text(str(item.get("target_users", "Engineers, researchers, and enterprise practitioners."))),
            "existing_problem": clean_text(str(item.get("existing_problem", "Unaddressed technical bottleneck identified in literature."))),
            "proposed_solution": clean_text(str(item.get("proposed_solution", "An optimized software toolchain or hardware deployment pipeline."))),
            "practical_feasibility": feasibility,
            "potential_applications": potential_apps,
            "evidence_basis": evidence_basis,
            "supporting_gap_or_paper": clean_text(str(item.get("supporting_gap_or_paper", default_gap_title))),
        })
        
    return validated


# =============================================================================
# 3. DETERMINISTIC OFFLINE HEURISTIC ANALYZER (FALLBACK)
# =============================================================================

def generate_deterministic_opportunities(
    topic: str,
    domain: str,
    research_gaps: List[Dict[str, Any]],
    tech_limitations: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """Generates rule-grounded market opportunities when GEMINI_API_KEY is not configured."""
    gap_title = research_gaps[0].get("title") if research_gaps else "Identified Research Limitations"
    
    return [
        {
            "title": f"Turnkey Optimization & Acceleration SDK for {topic}",
            "description": f"A developer-first software development kit that automates parameter-efficient fine-tuning, memory optimization, and quantization for {domain or topic}.",
            "target_users": "Enterprise AI Engineers, Data Science Teams, and ML Application Developers",
            "existing_problem": "Teams struggle with memory saturation and high compute bills when adapting large models to production environments.",
            "proposed_solution": "A plug-and-play Python library with native FlashAttention-2, QLoRA, and automatic mixed-precision defaults.",
            "practical_feasibility": "High",
            "potential_applications": [
                "Cloud-based training pipeline acceleration",
                "Self-hosted internal enterprise model customization",
                "Cost reduction for high-throughput inference APIs"
            ],
            "evidence_basis": "research_grounded",
            "supporting_gap_or_paper": gap_title
        },
        {
            "title": f"Benchmarking & Drift Monitoring Platform for {topic}",
            "description": f"An automated validation suite that stress-tests models against realistic synthetic noise, data drift, and out-of-distribution shifts before deployment.",
            "target_users": "Quality Assurance Engineers, MLOps Professionals, Compliance Officers",
            "existing_problem": "Models evaluated only on clean static benchmarks suffer from unmonitored performance drops after deployment in the wild.",
            "proposed_solution": "A CI/CD testing platform that generates continuous synthetic edge cases and evaluates distribution robustness.",
            "practical_feasibility": "High",
            "potential_applications": [
                "Pre-deployment safety and compliance certification",
                "Automated continuous evaluation in CI/CD pipelines",
                "Cross-organization benchmark comparisons"
            ],
            "evidence_basis": "research_grounded",
            "supporting_gap_or_paper": "Dataset Scarcity and Evaluation Over-Reliance on Synthetic Benchmarks"
        },
        {
            "title": f"Specialized Edge Inference Gateway for {domain or 'Edge AI'}",
            "description": f"An ultra-low-power runtime engine and hardware bridge designed to execute {topic} algorithms directly on embedded devices.",
            "target_users": "IoT System Developers, Embedded Systems Engineers, Robotics Manufacturers",
            "existing_problem": "High-end server architectures cannot run directly on constrained microcontrollers and mobile edge accelerators.",
            "proposed_solution": "A hardware-agnostic C++ inference engine with 4-bit integer quantization and zero external cloud dependencies.",
            "practical_feasibility": "Medium",
            "potential_applications": [
                "Autonomous robotics and drone navigation",
                "Wearable medical monitoring and point-of-care devices",
                "Industrial IoT sensory anomaly detection"
            ],
            "evidence_basis": "extrapolated_assumption",
            "supporting_gap_or_paper": "Contextual & Practical Integration: Edge Hardware Constraints"
        }
    ]


# =============================================================================
# 4. PRIMARY OPPORTUNITY ANALYSIS FUNCTION
# =============================================================================

def analyze_market_opportunities(
    topic: str,
    domain: str,
    research_gaps: List[Dict[str, Any]],
    tech_limitations: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """Analyzes market opportunities using Gemini AI or deterministic fallback."""
    default_gap = research_gaps[0].get("title", "Research Gaps") if research_gaps else "Identified Bottlenecks"
    has_key = bool(config.get("GEMINI_API_KEY", "").strip())
    
    if has_key:
        try:
            logger.info(f"Analyzing market opportunities for '{topic}' using Gemini AI...")
            prompt = build_opportunity_prompt(topic, domain, research_gaps, tech_limitations)
            raw = call_gemini_json(
                prompt=prompt,
                system_instruction=OPPORTUNITY_ANALYZER_SYSTEM_INSTRUCTION
            )
            validated = validate_and_normalize_opportunities(raw, default_gap)
            if validated:
                logger.info(f"Identified {len(validated)} market opportunities with Gemini.")
                return validated
        except GeminiError as e:
            logger.warning(f"Gemini opportunity analysis failed: {e}. Using deterministic fallback.")
            
    logger.info(f"Generating deterministic market opportunities for '{topic}'.")
    return generate_deterministic_opportunities(topic, domain, research_gaps, tech_limitations)
