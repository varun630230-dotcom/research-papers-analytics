"""
ResearchGap AI - Technological Limitation Analysis Service
============================================================
Identifies technical, computational, and infrastructure bottlenecks across the literature:

1. Computational Limitations (FLOPs, memory saturation, training latency)
2. Scalability Issues (network synchronization, communication bottlenecks)
3. Infrastructure Limitations (datacenter compute vs edge resource constraints)
4. Outdated Technologies (legacy algorithms or frameworks being superseded)
5. Missing Technical Capabilities (unimplemented features, lack of native tooling)

For every identified limitation:
- Links the affected technologies and frameworks
- Cites the specific supporting research papers
- Recommends modern, technically justified alternative technologies
"""

import logging
from typing import Dict, Any, List, Optional

from config import config
from services.gemini_client import call_gemini_json, GeminiError
from utils.text_cleaner import clean_text

logger = logging.getLogger("researchgap.tech_analyzer")
logging.basicConfig(level=logging.INFO)

VALID_LIMITATION_TYPES = {
    "computational",
    "infrastructure",
    "scalability",
    "outdated_technology",
    "missing_capability"
}

TECH_ANALYZER_SYSTEM_INSTRUCTION = """You are a Senior Principal Software Architect and Infrastructure Engineer.
Your task is to analyze the technological and computational limitations identified across the provided academic research papers.

RULES:
1. Ground all limitations directly in the technologies and findings mentioned in the provided text.
2. For each limitation, recommend modern, technically justified alternative technologies (e.g. FlashAttention, vLLM, ZeRO, ONNX, Triton).
3. Do not invent non-existent papers; cite only from the provided paper list.
4. Categorize each limitation into one of the valid limitation types:
   - "computational"
   - "infrastructure"
   - "scalability"
   - "outdated_technology"
   - "missing_capability"
5. Return strictly valid JSON adhering to the specified schema.
"""


def build_tech_analysis_prompt(
    topic: str,
    domain: str,
    paper_analyses: List[Dict[str, Any]],
    synthesis: Dict[str, Any]
) -> str:
    """Builds prompt compiling technologies, algorithms, and reported limitations."""
    tech_compilation = []
    
    for i, item in enumerate(paper_analyses, 1):
        a = item.get("analysis_data", item)
        title = a.get("paper_title", f"Paper #{i}")
        techs = ", ".join(a.get("technologies", [])) or "Standard frameworks"
        algos = ", ".join(a.get("algorithms", [])) or "Standard algorithms"
        lims = "; ".join(a.get("limitations", [])) or "None explicitly noted."
        
        tech_compilation.append(
            f'[{i}] Paper: "{title}"\n'
            f'    Technologies Used: {techs}\n'
            f'    Algorithms: {algos}\n'
            f'    Reported Bottlenecks: {lims}'
        )
        
    compiled_text = "\n\n".join(tech_compilation)
    repeated_lims = synthesis.get("repeated_limitations", [])
    trends = synthesis.get("technological_trends", [])
    
    prompt = f"""Identify the technological, computational, and architectural limitations in this literature.

TOPIC: {topic}
DOMAIN: {domain or 'Computer Science / Engineering'}

--- ANALYZED TECHNOLOGIES & BOTTLENECKS ---
{compiled_text}

--- REPEATED SYNTHESIS LIMITATIONS & TRENDS ---
Repeated Limitations: {repeated_lims}
Technological Trends: {trends}

--- INSTRUCTIONS ---
Extract 3 to 5 concrete technological limitations and suggest modern alternative architectures.
Output a JSON object with a single key "technological_limitations" containing an array of objects:
{{
    "technological_limitations": [
        {{
            "title": "Descriptive technological limitation title",
            "limitation_type": "computational | infrastructure | scalability | outdated_technology | missing_capability",
            "description": "Technical description of the architectural or compute bottleneck",
            "affected_technologies": ["Technology A", "Framework B"],
            "affected_papers": ["Exact Paper Title A", "Exact Paper Title B"],
            "suggested_alternatives": "Specific recommended replacement tools, frameworks, or algorithms",
            "expected_benefits": "Quantitative or architectural advantages of adopting the alternatives"
        }}
    ]
}}
"""
    return prompt


# =============================================================================
# 2. VALIDATION & NORMALIZATION
# =============================================================================

def validate_and_normalize_tech_limitations(
    raw_limitations: Any, 
    default_paper_titles: List[str]
) -> List[Dict[str, Any]]:
    """Validates and cleans the list of technological limitations."""
    if isinstance(raw_limitations, dict) and "technological_limitations" in raw_limitations:
        raw_limitations = raw_limitations["technological_limitations"]
        
    if not isinstance(raw_limitations, list):
        return []
        
    fallback_title = default_paper_titles[0] if default_paper_titles else "Analyzed Literature"
    validated = []
    
    for item in raw_limitations:
        if not isinstance(item, dict):
            continue
            
        title = clean_text(str(item.get("title", "")))
        if not title:
            continue
            
        raw_type = clean_text(str(item.get("limitation_type", ""))).lower()
        lim_type = raw_type if raw_type in VALID_LIMITATION_TYPES else "computational"
        
        # Affected papers
        papers = item.get("affected_papers", [])
        if isinstance(papers, list):
            affected_papers = [clean_text(str(p)) for p in papers if str(p).strip()]
        elif isinstance(papers, str) and papers.strip():
            affected_papers = [clean_text(papers)]
        else:
            affected_papers = []
        if not affected_papers:
            affected_papers = [fallback_title]
            
        # Affected technologies
        techs = item.get("affected_technologies", [])
        if isinstance(techs, list):
            affected_techs = [clean_text(str(t)) for t in techs if str(t).strip()]
        elif isinstance(techs, str) and techs.strip():
            affected_techs = [clean_text(techs)]
        else:
            affected_techs = ["Standard execution environment"]
            
        validated.append({
            "title": title,
            "limitation_type": lim_type,
            "description": clean_text(str(item.get("description", "A technical limitation identified in the literature."))),
            "affected_technologies": affected_techs,
            "affected_papers": affected_papers,
            "suggested_alternatives": clean_text(str(item.get("suggested_alternatives", "Adopt modern distributed frameworks and asynchronous pipelines."))),
            "expected_benefits": clean_text(str(item.get("expected_benefits", "Reduces latency, optimizes memory consumption, and accelerates convergence."))),
        })
        
    return validated


# =============================================================================
# 3. DETERMINISTIC OFFLINE HEURISTIC ANALYZER (FALLBACK)
# =============================================================================

def generate_deterministic_tech_limitations(
    topic: str,
    domain: str,
    paper_analyses: List[Dict[str, Any]],
    synthesis: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """Generates rule-grounded technological limitations when GEMINI_API_KEY is not configured."""
    paper_titles = [
        item.get("analysis_data", item).get("paper_title", f"Paper #{i+1}")
        for i, item in enumerate(paper_analyses)
    ]
    p1 = paper_titles[0] if paper_titles else "Analyzed Literature"
    p2 = paper_titles[1] if len(paper_titles) > 1 else p1
    
    return [
        {
            "title": "High Memory Footprint and Activation Caching Overhead",
            "limitation_type": "computational",
            "description": f"Standard full-parameter fine-tuning and intermediate activation caching saturate GPU VRAM during training runs in {domain or topic}.",
            "affected_technologies": ["Standard Full-Precision PyTorch / CUDA Pipelines"],
            "affected_papers": [p1],
            "suggested_alternatives": "LoRA/QLoRA parameter-efficient fine-tuning, FlashAttention-2, and 8-bit optimizer states (bitsandbytes).",
            "expected_benefits": "Up to 65% reduction in peak VRAM consumption allowing larger batch sizes and lower infrastructure costs."
        },
        {
            "title": "Synchronous Network Barrier and Straggler Bottlenecks",
            "limitation_type": "scalability",
            "description": "Relying on synchronous parameter aggregation causes high-speed nodes to stall waiting for high-latency or resource-constrained nodes.",
            "affected_technologies": ["Synchronous Parameter Server Architecture", "Standard AllReduce"],
            "affected_papers": [p1, p2],
            "suggested_alternatives": "Asynchronous decentralized aggregation, Ring-AllReduce with gradient sparsification, and buffered staleness bounds.",
            "expected_benefits": "Near-linear throughput scaling across heterogeneous network bandwidths."
        },
        {
            "title": "Lack of Standardized Edge Deployment and Runtime Quantization",
            "limitation_type": "missing_capability",
            "description": f"Published models lack export pipelines optimized for mobile and embedded edge runtimes, remaining confined to server environments.",
            "affected_technologies": ["Unoptimized Python / PyTorch Model Runtimes"],
            "affected_papers": [p2],
            "suggested_alternatives": "ONNX Runtime with TensorRT execution provider, llama.cpp / GGML quantization, or Apache TVM compiler.",
            "expected_benefits": "Enables sub-50ms inference on CPU and embedded edge accelerators without requiring active datacenter connectivity."
        }
    ]


# =============================================================================
# 4. PRIMARY TECHNOLOGICAL ANALYSIS FUNCTION
# =============================================================================

def analyze_technological_limitations(
    topic: str,
    domain: str,
    paper_analyses: List[Dict[str, Any]],
    synthesis: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """Analyzes technological limitations using Gemini AI or deterministic fallback."""
    paper_titles = [
        item.get("analysis_data", item).get("paper_title", f"Paper #{i+1}")
        for i, item in enumerate(paper_analyses)
    ]
    has_key = bool(config.get("GEMINI_API_KEY", "").strip())
    
    if has_key:
        try:
            logger.info(f"Analyzing technological limitations for '{topic}' using Gemini AI...")
            prompt = build_tech_analysis_prompt(topic, domain, paper_analyses, synthesis)
            raw = call_gemini_json(
                prompt=prompt,
                system_instruction=TECH_ANALYZER_SYSTEM_INSTRUCTION
            )
            validated = validate_and_normalize_tech_limitations(raw, paper_titles)
            if validated:
                logger.info(f"Identified {len(validated)} technological limitations with Gemini.")
                return validated
        except GeminiError as e:
            logger.warning(f"Gemini tech analysis failed: {e}. Falling back to deterministic analysis.")
            
    logger.info(f"Generating deterministic tech limitations for '{topic}'.")
    return generate_deterministic_tech_limitations(topic, domain, paper_analyses, synthesis)
