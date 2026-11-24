"""
ResearchGap AI - Development Roadmap Generator Service
========================================================
Generates a practical, step-by-step engineering and research execution plan
structured across 8 defined phases:

- Phase 1: Problem Definition & Formalization
- Phase 2: Literature Review & Baseline Selection
- Phase 3: Dataset Collection & Curation
- Phase 4: Data Preprocessing & Partitioning
- Phase 5: Model / System Development
- Phase 6: Rigorous Evaluation & Ablation Trials
- Phase 7: Hardware & Latency Optimization
- Phase 8: Production Deployment & Continuous Monitoring

Adapts the tasks, deliverables, and timelines directly to the specific research topic
and system architecture.
"""

import logging
from typing import Dict, Any, List, Optional

from config import config
from services.gemini_client import call_gemini_json, GeminiError
from utils.text_cleaner import clean_text
from utils.topic_context import extract_literature_context

logger = logging.getLogger("researchgap.roadmap_generator")
logging.basicConfig(level=logging.INFO)

ROADMAP_SYSTEM_INSTRUCTION = """You are a Principal Engineering Director and Research Program Manager.
Your task is to generate a realistic, tailored 8-phase technical development roadmap for executing the proposed research project.

RULES:
1. Cover exactly the 8 standard development phases:
   - Phase 1: Problem Definition
   - Phase 2: Literature Review
   - Phase 3: Dataset Collection
   - Phase 4: Data Preprocessing
   - Phase 5: Model/System Development
   - Phase 6: Evaluation
   - Phase 7: Optimization
   - Phase 8: Deployment
2. Tailor every task directly to the specific technologies and research topic provided.
3. Define concrete deliverables and estimated timeframes (in weeks) for each phase.
4. Return strictly valid JSON adhering to the specified schema.
"""


def build_roadmap_prompt(
    topic: str,
    domain: str,
    architecture: Dict[str, Any]
) -> str:
    """Builds prompt tailoring the 8 phases to the chosen architecture and topic."""
    sol = architecture.get("proposed_solution", f"Research system for {topic}")
    techs = [t.get("name") for t in architecture.get("recommended_technologies", []) if isinstance(t, dict)]
    tech_str = ", ".join(techs) if techs else "PyTorch, Docker, FastAPI"
    
    prompt = f"""Generate a practical 8-phase development roadmap for executing this research project.

TOPIC: {topic}
DOMAIN: {domain or 'Computer Science / Engineering'}
PROPOSED ARCHITECTURE: {sol}
RECOMMENDED TECHNOLOGIES: {tech_str}

--- INSTRUCTIONS ---
Formulate an 8-phase development roadmap.
Output a JSON object with a single key "phases" containing an array of 8 objects:
{{
    "phases": [
        {{
            "phase_number": 1,
            "title": "Phase 1: Problem Definition & Mathematical Formulation",
            "objective": "Clear description of phase objective",
            "tasks": ["Specific task 1", "Specific task 2", "Specific task 3"],
            "deliverable": "Concrete artifact produced (e.g. Formal specification doc)",
            "estimated_weeks": 2
        }}
    ]
}}
"""
    return prompt


# =============================================================================
# 2. VALIDATION & NORMALIZATION
# =============================================================================

def validate_and_normalize_roadmap(raw_data: Any, topic: str) -> Dict[str, Any]:
    """Validates that all 8 development phases are populated and structured."""
    phases = []
    if isinstance(raw_data, dict):
        phases = raw_data.get("phases", [])
    elif isinstance(raw_data, list):
        phases = raw_data
        
    if not isinstance(phases, list) or len(phases) < 8:
        return generate_deterministic_roadmap(topic, "", {})
        
    validated_phases = []
    for i, p in enumerate(phases[:8], 1):
        if not isinstance(p, dict):
            continue
        validated_phases.append({
            "phase_number": i,
            "title": clean_text(str(p.get("title", f"Phase {i}"))),
            "objective": clean_text(str(p.get("objective", "Execute research milestones."))),
            "tasks": [clean_text(str(t)) for t in p.get("tasks", []) if str(t).strip()],
            "deliverable": clean_text(str(p.get("deliverable", "Milestone technical report."))),
            "estimated_weeks": int(p.get("estimated_weeks", 2)),
        })
        
    return {
        "project_topic": topic,
        "total_phases": len(validated_phases),
        "total_estimated_weeks": sum(p["estimated_weeks"] for p in validated_phases),
        "phases": validated_phases
    }


# =============================================================================
# 3. DETERMINISTIC OFFLINE HEURISTIC ROADMAP (FALLBACK)
# =============================================================================

def generate_deterministic_roadmap(
    topic: str,
    domain: str,
    architecture: Dict[str, Any]
) -> Dict[str, Any]:
    """Generates an 8-phase development roadmap tailored to the topic and domain."""
    ctx = extract_literature_context(topic=topic, domain=domain)
    clean_top = ctx["topic"]
    dom = ctx["domain"]
    algo = ctx["algorithms"][0]
    dataset = ctx["datasets"][0] if ctx["datasets"] else "domain benchmark corpora"
    metric = ctx["metrics"][0]

    phases = [
        {
            "phase_number": 1,
            "title": "Phase 1: Problem Definition & Formalization",
            "objective": f"Formalize the mathematical and architectural scope for {clean_top}.",
            "tasks": [
                f"Define objective functions and operational constraints for {clean_top}.",
                f"Establish quantifiable target metrics ({metric}, latency budget, memory limit).",
                f"Draft the technical requirements specification and system scope for {dom}."
            ],
            "deliverable": "Mathematical problem formulation document & engineering specification.",
            "estimated_weeks": 2
        },
        {
            "phase_number": 2,
            "title": "Phase 2: Literature Review & Baseline Selection",
            "objective": f"Select and reproduce state-of-the-art academic baselines for {clean_top}.",
            "tasks": [
                f"Select 3 to 4 open-source published baseline models ({algo} variants) from literature.",
                "Set up reference benchmark environments in containerized Docker images.",
                "Validate reproducible baseline numbers against reported publication metrics."
            ],
            "deliverable": "Reproduced baseline repository with benchmark validation scripts.",
            "estimated_weeks": 2
        },
        {
            "phase_number": 3,
            "title": "Phase 3: Dataset Collection & Curation",
            "objective": f"Acquire, audit, and structure evaluation datasets including {dataset}.",
            "tasks": [
                f"Gather standardized public benchmark datasets ({dataset}) and domain telemetry.",
                "Perform data quality profiling (missing attributes, label skew, distribution bounds).",
                "Establish deterministic training, validation, and holdout test splits."
            ],
            "deliverable": "Version-controlled data catalog with automated validation checks.",
            "estimated_weeks": 3
        },
        {
            "phase_number": 4,
            "title": "Phase 4: Data Preprocessing & Validation Pipelines",
            "objective": f"Build automated data transformation, tokenization, and cleaning pipelines for {dom}.",
            "tasks": [
                f"Implement feature normalization and synthetic noise injection scripts tailored for {clean_top}.",
                "Create cross-validation generators simulating realistic domain and demographic shifts.",
                "Build automated unit tests verifying pipeline integrity and zero data leakage."
            ],
            "deliverable": "Automated data preprocessing module with reproducible seed generation.",
            "estimated_weeks": 2
        },
        {
            "phase_number": 5,
            "title": "Phase 5: Core System & Model Development",
            "objective": f"Implement proposed {algo} architecture and optimization engine.",
            "tasks": [
                f"Develop the core {algo} architecture and parameter-efficient adapter layers for {clean_top}.",
                "Implement custom loss formulations with class-imbalance weighting.",
                "Integrate asynchronous streaming pipeline and feature caching modules."
            ],
            "deliverable": "Fully functional model implementation with end-to-end training loop.",
            "estimated_weeks": 4
        },
        {
            "phase_number": 6,
            "title": "Phase 6: Rigorous Evaluation & Ablation Trials",
            "objective": f"Conduct comprehensive {metric} benchmark evaluations and ablation studies.",
            "tasks": [
                f"Benchmark empirical performance ({metric}) against all selected baseline models.",
                "Execute systematic ablation studies isolating each architectural component's impact.",
                "Perform cross-domain out-of-distribution stress testing."
            ],
            "deliverable": "Experimental evaluation report with statistical significance analysis.",
            "estimated_weeks": 3
        },
        {
            "phase_number": 7,
            "title": "Phase 7: Hardware & Latency Optimization",
            "objective": f"Optimize computational throughput, memory usage, and inference latency for {algo}.",
            "tasks": [
                "Profile GPU kernel execution times and memory allocation bottlenecks.",
                "Apply post-training quantization (INT8/FP8) and operator fusion.",
                "Export optimized computation graphs to ONNX Runtime and TensorRT."
            ],
            "deliverable": "Quantized, compiled model artifacts achieving sub-50ms inference targets.",
            "estimated_weeks": 2
        },
        {
            "phase_number": 8,
            "title": "Phase 8: Production Deployment & Monitoring",
            "objective": f"Deploy the {clean_top} system into production infrastructure with continuous monitoring.",
            "tasks": [
                "Package inference services into scalable Docker containers orchestrated via FastAPI.",
                f"Implement real-time Prometheus telemetry tracking {metric}, latency, and data drift.",
                "Publish comprehensive developer documentation, API schemas, and replication guide."
            ],
            "deliverable": "Production-ready deployment repository with live monitoring dashboard.",
            "deliverable": "Production-ready deployment repository with live monitoring dashboard.",
            "estimated_weeks": 2
        }
    ]
    
    return {
        "project_topic": topic,
        "total_phases": 8,
        "total_estimated_weeks": sum(p["estimated_weeks"] for p in phases),
        "phases": phases
    }


# =============================================================================
# 4. PRIMARY ROADMAP GENERATION FUNCTION
# =============================================================================

def generate_development_roadmap(
    topic: str,
    domain: str,
    architecture: Dict[str, Any]
) -> Dict[str, Any]:
    """Generates the 8-phase development roadmap using Gemini AI or deterministic fallback."""
    has_key = bool(config.get("GEMINI_API_KEY", "").strip())
    
    if has_key:
        try:
            logger.info(f"Generating 8-phase development roadmap for '{topic}' using Gemini AI...")
            prompt = build_roadmap_prompt(topic, domain, architecture)
            raw = call_gemini_json(
                prompt=prompt,
                system_instruction=ROADMAP_SYSTEM_INSTRUCTION
            )
            validated = validate_and_normalize_roadmap(raw, topic)
            if validated and len(validated.get("phases", [])) == 8:
                logger.info(f"Generated 8-phase development roadmap for '{topic}' with Gemini.")
                return validated
        except GeminiError as e:
            logger.warning(f"Gemini roadmap generation failed: {e}. Falling back to deterministic roadmap.")
            
    logger.info(f"Generating deterministic 8-phase roadmap for '{topic}'.")
    return generate_deterministic_roadmap(topic, domain, architecture)
