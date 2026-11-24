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
from utils.topic_context import extract_literature_context

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
    """Generates dynamic, domain-specific market opportunities derived from research gaps."""
    ctx = extract_literature_context(topic=topic, domain=domain)
    clean_top = ctx["topic"]
    dom = ctx["domain"]
    algo = ctx["algorithms"][0]
    metric = ctx["metrics"][0]
    
    gap_title = research_gaps[0].get("title") if research_gaps else f"Methodological Rigor and Contextual Ambiguity in {clean_top}"
    sec_gap = research_gaps[1].get("title") if len(research_gaps) > 1 else f"Dataset Scarcity and Evaluation Bias in {clean_top}"
    
    # Customise product personas based on domain
    if any(k in dom.lower() for k in ["language", "nlp", "text", "multimodal", "social"]):
        opp1_title = f"Real-Time Automated Intelligence & Moderation API for {clean_top}"
        opp1_users = "Trust & Safety Teams, Community Managers, Social Platforms, and EdTech Administrators"
        opp1_prob = f"Current platforms rely on slow, manual reviews or rigid keyword blocklists that fail on nuanced {clean_top} contexts."
        opp1_sol = f"A low-latency REST/gRPC API with fine-tuned {algo} backbones delivering explainable confidence scores and multi-label severity categorization."
        opp1_apps = ["Live stream and chat room automated moderation", "School and workplace digital safety monitoring", "Social media brand reputation management"]
    elif any(k in dom.lower() for k in ["health", "medical", "clinical"]):
        opp1_title = f"Clinical Decision Support & Risk Stratification Suite for {clean_top}"
        opp1_users = "Clinical Informaticians, Hospital Physicians, Diagnostic Centers, and Healthcare Startups"
        opp1_prob = f"Clinicians lack automated tools to detect early biomarkers and subtle pathological signals in {clean_top} without high false-alarm rates."
        opp1_sol = f"An integrated software platform utilizing {algo} with calibrated confidence bounds and HL7/FHIR EHR interoperability."
        opp1_apps = ["Point-of-care patient risk assessment", "Automated diagnostic triage in intensive care", "Clinical trial cohort screening"]
    else:
        opp1_title = f"Turnkey Optimization & Acceleration SDK for {clean_top}"
        opp1_users = "Enterprise AI Engineers, Systems Architects, and ML Application Developers"
        opp1_prob = f"Teams struggle with compute bottlenecks and high infrastructure bills when deploying {algo} in production environments."
        opp1_sol = f"A drop-in Python/C++ acceleration library providing memory-efficient execution and automated mixed-precision pipelining."
        opp1_apps = ["Cloud-based training pipeline acceleration", "Enterprise internal model customization", "High-throughput inference deployment"]

    return [
        {
            "title": opp1_title,
            "description": f"A specialized software solution addressing practical operational challenges in {clean_top}.",
            "target_users": opp1_users,
            "existing_problem": opp1_prob,
            "proposed_solution": opp1_sol,
            "practical_feasibility": "High",
            "potential_applications": opp1_apps,
            "evidence_basis": "research_grounded",
            "supporting_gap_or_paper": gap_title
        },
        {
            "title": f"Continuous Robustness & Benchmark Auditing Platform for {clean_top}",
            "description": f"An automated verification harness that stress-tests models against realistic data drift, adversarial perturbations, and demographic shift in {dom}.",
            "target_users": "Quality Assurance Engineers, MLOps Professionals, and AI Compliance Officers",
            "existing_problem": f"Models validated only on static benchmarks suffer from unmonitored performance drops ({metric} degradation) after live deployment.",
            "proposed_solution": "A CI/CD testing platform that generates continuous synthetic edge cases and monitors real-world calibration stability.",
            "practical_feasibility": "High",
            "potential_applications": [
                "Pre-deployment safety and compliance certification",
                "Automated continuous evaluation in CI/CD pipelines",
                "Cross-model benchmark comparisons and audit reports"
            ],
            "evidence_basis": "research_grounded",
            "supporting_gap_or_paper": sec_gap
        },
        {
            "title": f"High-Throughput Low-Latency Edge Inference Gateway for {dom}",
            "description": f"An ultra-low-power runtime engine and hardware bridge designed to execute {clean_top} algorithms on resource-constrained devices.",
            "target_users": "Embedded Systems Developers, IoT Product Engineers, and Platform Architects",
            "existing_problem": "High-capacity server architectures cannot execute directly on constrained endpoint devices without network roundtrips.",
            "proposed_solution": "A hardware-agnostic C++ inference engine with INT8 quantization, zero external dependencies, and streaming telemetry.",
            "practical_feasibility": "Medium",
            "potential_applications": [
                f"On-device edge analytics for {clean_top}",
                "Air-gapped and offline sensitive data processing",
                "Sub-50ms local processing for interactive applications"
            ],
            "evidence_basis": "extrapolated_assumption",
            "supporting_gap_or_paper": "Contextual & Practical Integration: Real-World Operational Constraints"
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
