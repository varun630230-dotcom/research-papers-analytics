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
    """Generates a rule-grounded architectural recommendation when GEMINI_API_KEY is not configured."""
    top_gap = research_gaps[0] if research_gaps else {}
    target_gap = top_gap.get("title", f"Primary Scalability Bottleneck in {topic}")
    
    return {
        "target_gap_addressed": target_gap,
        "problem_statement": (
            f"Current implementations in {topic} suffer from communication overhead, memory saturation, "
            f"and high synchronization latency under distributed heterogeneous constraints."
        ),
        "proposed_solution": (
            f"A tiered, modular system architecture that decouples model training, gradient compression, "
            f"and verification into asynchronous stages optimized for {domain or 'distributed computing'}."
        ),
        "system_components": [
            {
                "name": "Ingestion & Data Preparation Layer",
                "role": "Data validation, feature normalization, and non-IID client partitioning",
                "description": "Validates schema integrity, applies tokenization or image transforms, and handles streaming batches."
            },
            {
                "name": "Optimization & Training Engine",
                "role": "Parameter-efficient model execution and gradient calculation",
                "description": "Executes forward and backward passes using mixed-precision fp16/bf16 with gradient checkpointing."
            },
            {
                "name": "Communication & Aggregation Gateway",
                "role": "Asynchronous parameter synchronization and gossip routing",
                "description": "Applies top-k gradient sparsification and compressed all-reduce to minimize network payload."
            },
            {
                "name": "Verification & Continuous Benchmarking Engine",
                "role": "Automated evaluation, drift tracking, and safety bounds",
                "description": "Periodically evaluates model convergence against baseline validation suites and monitors degradation."
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
            "1. Raw telemetry and benchmark data are ingested and partitioned across worker nodes.",
            "2. Nodes compute local parameter updates using parameter-efficient fine-tuning (LoRA / QLoRA).",
            "3. Local gradients are compressed using top-k sparsification and broadcast via asynchronous gossip.",
            "4. The aggregation gateway updates global model weights with buffered staleness compensation.",
            "5. The updated checkpoint is validated against continuous benchmarking suites and dispatched for inference."
        ],
        "model_recommendations": [
            {
                "model_type": "Modular Transformer / Backbone Architecture",
                "architecture": "Pretrained foundation backbone with rank-16 Low-Rank Adapters (LoRA)",
                "loss_function": "Cross-Entropy with Proximal Regularization Term (mu = 0.01) for stability"
            }
        ],
        "implementation_considerations": [
            "Use bfloat16 mixed precision to avoid gradient underflow while saving half of memory bandwidth.",
            "Implement heartbeat monitoring on distributed nodes to detect stragglers early.",
            "Maintain versioned checkpoint snapshots in object storage (S3 / MinIO) for reproducible rollback."
        ],
        "expected_challenges": [
            "Balancing gradient compression ratio against numerical convergence stability.",
            "Managing asynchronous staleness when network latency variance across clients is high.",
            "Ensuring cross-platform numerical consistency across heterogeneous edge accelerator kernels."
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
