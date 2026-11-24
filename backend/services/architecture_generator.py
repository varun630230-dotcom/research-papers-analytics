"""
ResearchGap AI - Architecture Recommendation Service
======================================================
Generates technical systems architecture recommendations designed to resolve
the highest-priority research gaps and technological limitations:

1. Problem Statement & Proposed Solution
2. System Components & Structural Topology
3. Recommended Technologies (toolchains, runtimes, storage, inference engines)
4. End-to-End Data Flow Pipeline
5. Recommended Model Architectures & Loss Formulations
6. Practical Implementation Considerations & Anticipated Engineering Challenges
"""

import logging
from typing import Dict, Any, List, Optional

from config import config
from services.gemini_client import call_gemini_json, GeminiError
from utils.text_cleaner import clean_text
from utils.topic_context import extract_literature_context

logger = logging.getLogger("researchgap.architecture_generator")
logging.basicConfig(level=logging.INFO)

ARCHITECTURE_SYSTEM_INSTRUCTION = """You are a Chief AI Systems Architect and Lead Infrastructure Engineer.
Your task is to design a robust, modern system architecture addressing the primary research gap and technical bottlenecks identified in the literature.

RULES:
1. Choose modern, pragmatic technologies (e.g., PyTorch, Triton, ONNX, FastAPI, Redis, Docker, Ray, PostgreSQL).
2. Clearly define the data flow steps from ingestion through model training/inference to user presentation.
3. Explicitly state the recommended model architectures, loss functions, and optimization considerations.
4. Highlight real-world engineering challenges (e.g. synchronization latency, cold-start inference, memory saturation).
5. Return strictly valid JSON adhering to the specified schema.
"""


def build_architecture_prompt(
    topic: str,
    domain: str,
    research_gaps: List[Dict[str, Any]],
    tech_limitations: List[Dict[str, Any]]
) -> str:
    """Builds the prompt compiling the target gap and technological limitations."""
    top_gap = research_gaps[0] if research_gaps else {}
    gap_title = top_gap.get("title", f"Primary Bottleneck in {topic}")
    gap_desc = top_gap.get("description", "Unaddressed scalability and performance limitations.")
    gap_evidence = top_gap.get("evidence", "")
    
    limits_summary = []
    for lim in tech_limitations[:3]:
        limits_summary.append(f"- {lim.get('title')}: {lim.get('suggested_alternatives')}")
    limits_text = "\n".join(limits_summary) if limits_summary else "- General compute and memory constraints"
    
    prompt = f"""Design a technical systems architecture to solve the following primary research gap.

TOPIC: {topic}
DOMAIN: {domain or 'Computer Science / Engineering'}

--- PRIMARY RESEARCH GAP TO RESOLVE ---
Title: {gap_title}
Problem Description: {gap_desc}
Empirical Evidence: {gap_evidence}

--- KNOWN TECHNICAL LIMITATIONS & PROPOSED ALTERNATIVES ---
{limits_text}

--- INSTRUCTIONS ---
Formulate a comprehensive technical architecture recommendation.
Output a JSON object with EXACTLY the following structure:
{{
    "target_gap_addressed": "{gap_title}",
    "problem_statement": "Concise statement of the architectural bottleneck to be solved",
    "proposed_solution": "High-level overview of the proposed system architecture",
    "system_components": [
        {{"name": "Component Name 1", "role": "What this layer does", "description": "Technical details"}},
        {{"name": "Component Name 2", "role": "What this layer does", "description": "Technical details"}}
    ],
    "recommended_technologies": [
        {{"category": "Core Framework / Runtime / Database", "name": "Technology Name", "justification": "Why this specific technology is chosen"}}
    ],
    "data_flow": [
        "Step 1: Data ingestion and preprocessing",
        "Step 2: Representation learning and model training",
        "Step 3: Verification, inference, and result dispatch"
    ],
    "model_recommendations": [
        {{"model_type": "Model paradigm", "architecture": "Specific neural architecture", "loss_function": "Loss formulation and objective"}}
    ],
    "implementation_considerations": [
        "Key implementation consideration 1",
        "Key consideration 2"
    ],
    "expected_challenges": [
        "Anticipated engineering challenge 1",
        "Anticipated challenge 2"
    ]
}}
"""
    return prompt


# =============================================================================
# 2. VALIDATION & NORMALIZATION
# =============================================================================

def validate_and_normalize_architecture(raw_data: Any, topic: str, target_gap: str) -> Dict[str, Any]:
    """Validates and guarantees all architecture fields are present and structured."""
    if not isinstance(raw_data, dict):
        raw_data = {}
        
    def ensure_list(val: Any) -> List[Any]:
        return val if isinstance(val, list) else []

    return {
        "target_gap_addressed": clean_text(str(raw_data.get("target_gap_addressed", target_gap))),
        "problem_statement": clean_text(str(raw_data.get("problem_statement", f"Resolving key performance and scalability bottlenecks in {topic}."))),
        "proposed_solution": clean_text(str(raw_data.get("proposed_solution", f"A modular, distributed architecture coupling parameter-efficient adaptation with asynchronous aggregation."))),
        "system_components": ensure_list(raw_data.get("system_components")),
        "recommended_technologies": ensure_list(raw_data.get("recommended_technologies")),
        "data_flow": ensure_list(raw_data.get("data_flow")),
        "model_recommendations": ensure_list(raw_data.get("model_recommendations")),
        "implementation_considerations": ensure_list(raw_data.get("implementation_considerations")),
        "expected_challenges": ensure_list(raw_data.get("expected_challenges")),
    }


# =============================================================================
# 3. DETERMINISTIC OFFLINE HEURISTIC GENERATOR (FALLBACK)
# =============================================================================

def generate_deterministic_architecture(
    topic: str,
    domain: str,
    research_gaps: List[Dict[str, Any]],
    tech_limitations: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """Generates a dynamic, domain-specific architectural recommendation."""
    ctx = extract_literature_context(topic=topic, domain=domain)
    clean_top = ctx["topic"]
    dom = ctx["domain"]
    algo = ctx["algorithms"][0]
    metric = ctx["metrics"][0]
    
    top_gap = research_gaps[0] if research_gaps else {}
    target_gap = top_gap.get("title", f"Methodological Rigor and Scalability in {clean_top}")
    
    return {
        "target_gap_addressed": target_gap,
        "problem_statement": (
            f"Current implementations in {clean_top} face severe challenges with {ctx['challenges'][0].lower()} "
            f"when deployed in real-world high-throughput operational environments."
        ),
        "proposed_solution": (
            f"A tiered, modular system architecture that decouples input ingestion, {algo} representation inference, "
            f"and continuous verification into resilient asynchronous stages optimized for {dom}."
        ),
        "system_components": [
            {
                "name": "Ingestion & Feature Preparation Layer",
                "role": "Schema validation, input tokenization / transform, and streaming batching",
                "description": f"Validates incoming raw inputs, standardizes formats for {ctx['datasets'][0] if ctx['datasets'] else 'the target domain'}, and handles streaming queues."
            },
            {
                "name": f"Core Representation & {algo} Engine",
                "role": "High-throughput forward-pass inference and feature extraction",
                "description": f"Executes model passes using mixed-precision fp16/bf16 with fused attention kernels to minimize latency."
            },
            {
                "name": "Decision & Classification Service",
                "role": "Calibrated decision thresholding and confidence scoring",
                "description": f"Applies temperature-scaled probability calibration and multi-label dispatch logic tailored for {clean_top}."
            },
            {
                "name": "Verification & Continuous Drift Engine",
                "role": "Automated evaluation, out-of-distribution tracking, and audit logging",
                "description": f"Continuously monitors real-time {metric} metrics, logs input drift telemetry, and alerts on degradation."
            }
        ],
        "recommended_technologies": [
            {
                "category": "Deep Learning Framework",
                "name": "PyTorch 2.x + TorchCompile",
                "justification": "Industry-standard dynamic graph computation with fused kernel optimization."
            },
            {
                "category": "Optimization Toolchain",
                "name": "FlashAttention-2 + bitsandbytes",
                "justification": "Reduces peak VRAM by up to 60% and accelerates attention matrix computation."
            },
            {
                "category": "Inference & Runtime Engine",
                "name": "ONNX Runtime / TensorRT",
                "justification": "Provides low-latency deployment on CPU and heterogeneous GPU accelerators."
            },
            {
                "category": "Orchestration & Serving",
                "name": "FastAPI + Docker + Redis",
                "justification": "Lightweight asynchronous REST API with in-memory caching and containerized reproducibility."
            }
        ],
        "data_flow": [
            f"1. Ingestion: Raw input streams and multimodal assets are ingested, validated, and normalized by the API gateway.",
            f"2. Preprocessing: Feature transforms and tokenization are applied according to {dom} benchmark specifications.",
            f"3. Core Inference: The {algo} engine computes latent embeddings and classification logits with fp16 acceleration.",
            f"4. Calibration: Decision thresholds are dynamically calibrated to ensure optimal {metric} and minimize false alarms.",
            f"5. Telemetry & Audit: Predictions, explanation metadata, and latency telemetry are stored for continuous drift auditing."
        ],
        "model_recommendations": [
            {
                "model_type": f"Modular {algo} Backbone Architecture",
                "architecture": f"Pretrained foundation backbone with rank-16 Low-Rank Adapters (LoRA) optimized for {clean_top}",
                "loss_function": "Cross-Entropy with Focal Loss weighting to combat class imbalance"
            }
        ],
        "implementation_considerations": [
            "Use bfloat16 mixed precision to avoid gradient underflow while saving half of memory bandwidth.",
            f"Implement dynamic batching on the {algo} inference service to absorb traffic spikes.",
            "Maintain versioned checkpoint snapshots in object storage (S3 / MinIO) for reproducible rollback."
        ],
        "expected_challenges": [
            f"Minimizing tail latency during high-concurrency peak ingestion spikes in {clean_top}.",
            f"Handling out-of-distribution inputs and subtle edge cases without manual re-annotation in {dom}.",
            f"Maintaining low false-positive rates without sacrificing overall {metric} sensitivity."
        ]
    }


# =============================================================================
# 4. PRIMARY ARCHITECTURE GENERATION FUNCTION
# =============================================================================

def generate_architecture_recommendation(
    topic: str,
    domain: str,
    research_gaps: List[Dict[str, Any]],
    tech_limitations: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """Generates architecture recommendation using Gemini AI or deterministic fallback."""
    top_gap = research_gaps[0].get("title", f"Primary Gap in {topic}") if research_gaps else f"Primary Gap in {topic}"
    has_key = bool(config.get("GEMINI_API_KEY", "").strip())
    
    if has_key:
        try:
            logger.info(f"Generating architecture recommendations for '{topic}' using Gemini AI...")
            prompt = build_architecture_prompt(topic, domain, research_gaps, tech_limitations)
            raw = call_gemini_json(
                prompt=prompt,
                system_instruction=ARCHITECTURE_SYSTEM_INSTRUCTION
            )
            validated = validate_and_normalize_architecture(raw, topic, top_gap)
            if validated:
                logger.info(f"Generated architecture recommendation for '{topic}' with Gemini.")
                return validated
        except GeminiError as e:
            logger.warning(f"Gemini architecture generation failed: {e}. Falling back to deterministic architecture.")
            
    logger.info(f"Generating deterministic architecture recommendation for '{topic}'.")
    return generate_deterministic_architecture(topic, domain, research_gaps, tech_limitations)
