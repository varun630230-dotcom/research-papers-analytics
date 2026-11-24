"""
ResearchGap AI - Topic & Literature Context Extractor
======================================================
Dynamically extracts domain-specific entities, algorithms, datasets,
challenges, and architectural patterns from user inputs and discovered
academic papers. Ensures that every topic produces unique, literature-grounded
content across all views even when operating in deterministic/offline mode.
"""

import re
from typing import Dict, Any, List, Optional


# =============================================================================
# DOMAIN TAXONOMY & KEYWORD SIGNATURES
# =============================================================================

DOMAIN_SIGNATURES = {
    "nlp": {
        "name": "Natural Language Processing & Text Analytics",
        "keywords": [
            "nlp", "language", "text", "sentiment", "cyberbullying", "hate speech",
            "fake news", "summarization", "translation", "llm", "transformer",
            "bert", "roberta", "token", "corpus", "dialogue", "qa", "retrieval",
            "misinformation", "toxicity", "harassment", "offensive", "stance"
        ],
        "default_algos": ["Transformer Backbone", "Fine-Tuned BERT/RoBERTa", "Contrastive Representation Learning", "Attention Mechanisms"],
        "default_datasets": ["Domain-Specific Social / Web Corpora", "Annotated Benchmark Datasets", "Synthetic Contrast Sets"],
        "metrics": ["Macro F1-Score", "Accuracy", "Precision / Recall", "AUC-ROC"],
        "challenges": [
            "Subtle sarcasm, linguistic nuance, and implicit meaning",
            "Annotation bias and class imbalance in real-world samples",
            "Cross-platform and multilingual domain drift"
        ]
    },
    "vision": {
        "name": "Computer Vision & Visual Intelligence",
        "keywords": [
            "vision", "image", "video", "segmentation", "object detection",
            "cnn", "resnet", "vit", "visual", "optical", "yolo", "diffusion",
            "generative", "multimodal", "clip", "pixels", "camera", "depth"
        ],
        "default_algos": ["Vision Transformers (ViT)", "Convolutional Backbones (ConvNeXt/ResNet)", "Cross-Modal Dual Encoders", "Feature Pyramid Networks"],
        "default_datasets": ["Standard Visual Benchmarks (e.g. COCO/ImageNet)", "Specialized Domain Image Sets", "Video Frame Sequences"],
        "metrics": ["mAP (Mean Average Precision)", "Intersection over Union (IoU)", "Top-1 Accuracy", "Inference FPS"],
        "challenges": [
            "High computational complexity of high-resolution video streams",
            "Sensitivity to occlusion, variable lighting, and perspective distortion",
            "Scarcity of fine-grained pixel-level annotations"
        ]
    },
    "multimodal": {
        "name": "Multimodal AI & Cross-Media Analytics",
        "keywords": [
            "multimodal", "cross-modal", "vision-language", "audio-visual",
            "clip", "multimedia", "image-text", "video-audio", "fusion"
        ],
        "default_algos": ["Cross-Attention Fusion Encoders", "Contrastive Vision-Language Alignment (CLIP)", "Late Fusion Classifiers", "Graph Cross-Modal Networks"],
        "default_datasets": ["Multimodal Web / Social Repositories", "Paired Image-Text Collections", "Video-Audio Action Datasets"],
        "metrics": ["Multimodal F1-Score", "Recall@K", "Alignment Score", "Joint Accuracy"],
        "challenges": [
            "Modal imbalance where one dominant modality overshadows others",
            "Missing modality handling during real-time deployment",
            "Temporal alignment across asynchronous media streams"
        ]
    },
    "healthcare": {
        "name": "Healthcare & Biomedical Informatics",
        "keywords": [
            "health", "medical", "clinical", "patient", "disease", "cancer",
            "diagnosis", "ehr", "electronic health", "hospital", "biomedical",
            "drug", "genomic", "pathology", "radiology", "cardiac", "x-ray", "mri"
        ],
        "default_algos": ["Graph Neural Networks", "Self-Supervised Biomedical Transformers", "Survival Analysis Models", "Convolutional Segmentation Nets"],
        "default_datasets": ["Clinical EHR & Diagnostic Records", "De-Identified Medical Imaging Repositories", "Multi-Center Cohort Studies"],
        "metrics": ["Sensitivity & Specificity", "AUC-ROC", "F1-Score", "C-Index"],
        "challenges": [
            "Extreme class imbalance between healthy and pathological cases",
            "Stringent clinical safety, explainability, and regulatory compliance constraints",
            "Distribution shift across different hospital acquisition hardware"
        ]
    },
    "security": {
        "name": "Cybersecurity, Privacy & Adversarial Robustness",
        "keywords": [
            "security", "privacy", "attack", "malware", "vulnerability", "defense",
            "adversarial", "intrusion", "cryptography", "zero-day", "phishing",
            "differential privacy", "authentication", "threat"
        ],
        "default_algos": ["Adversarial Training Objectives", "Graph-Based Anomaly Detectors", "Autoencoder Bottlenecks", "Differential Privacy Mechanisms"],
        "default_datasets": ["Network Traffic PCAP Logs", "Adversarial Perturbation Benchmarks", "System Telemetry Datasets"],
        "metrics": ["False Alarm Rate (FAR)", "Detection Rate", "Evasion Success Rate", "Throughput"],
        "challenges": [
            "Rapid evolution of novel zero-day attack vectors",
            "Trade-off between formal privacy guarantees and downstream analytical utility",
            "Sub-millisecond latency requirements on line-rate packet inspection"
        ]
    },
    "distributed": {
        "name": "Distributed Systems, Cloud & Edge Computing",
        "keywords": [
            "distributed", "federated", "edge", "cloud", "latency", "bandwidth",
            "consensus", "cluster", "decentralized", "iot", "straggler",
            "synchronous", "asynchronous", "microservice", "orchestration"
        ],
        "default_algos": ["Federated Optimization (FedAvg/FedProx)", "Gossip Protocols", "Gradient Sparsification", "Dynamic Workload Balancers"],
        "default_datasets": ["Heterogeneous Distributed Traces", "Simulated Non-IID Network Benchmarks", "IoT Sensor Feeds"],
        "metrics": ["Communication Overhead (MB)", "Wall-Clock Convergence Time", "Throughput (req/sec)", "Device Memory"],
        "challenges": [
            "Communication bottlenecks across heterogeneous bandwidth networks",
            "Straggler nodes stalling global synchronization rounds",
            "Device memory constraints on embedded edge accelerators"
        ]
    },
    "robotics": {
        "name": "Robotics, Autonomous Systems & Control",
        "keywords": [
            "robot", "autonomous", "vehicle", "drone", "control", "rl",
            "reinforcement learning", "trajectory", "navigation", "lidar", "sensor",
            "kinematics", "slam", "manipulation"
        ],
        "default_algos": ["Deep Reinforcement Learning (PPO/SAC)", "Model Predictive Control (MPC)", "Sim-to-Real Domain Randomization", "Visual SLAM"],
        "default_datasets": ["Physics Simulation Environments", "Real-World Robot Teleoperation Logs", "LiDAR / Sensor Point Clouds"],
        "metrics": ["Task Success Rate", "Collision Avoidance Margin", "Tracking Error", "Execution Time"],
        "challenges": [
            "Sim-to-real reality gap causing catastrophic deployment failures",
            "Real-time sensor fusion under hard millisecond timing deadlines",
            "Sample inefficiency of reinforcement learning exploration"
        ]
    }
}


def detect_domain_profile(topic: str, domain_input: str = "", keywords: str = "") -> Dict[str, Any]:
    """Detects the most accurate domain profile based on text matching."""
    text = f"{topic} {domain_input} {keywords}".lower()
    
    # Check for multimodal explicitly
    if ("multimodal" in text or "image" in text and "text" in text or "video" in text and "text" in text):
        return DOMAIN_SIGNATURES["multimodal"]
        
    best_match = None
    max_count = 0
    
    for key, profile in DOMAIN_SIGNATURES.items():
        count = sum(1 for kw in profile["keywords"] if kw in text)
        if count > max_count:
            max_count = count
            best_match = profile
            
    if best_match and max_count > 0:
        return best_match
        
    # Default fallback profile
    return {
        "name": domain_input.strip() or "Computer Science & Artificial Intelligence",
        "default_algos": ["Deep Neural Networks", "State-of-the-Art Foundation Models", "Empirical Optimization Frameworks"],
        "default_datasets": ["Standardized Benchmark Corpora", "Real-World Empirical Evaluation Sets"],
        "metrics": ["Target Task Accuracy", "F1-Score", "Generalization Error", "Throughput"],
        "challenges": [
            "Limited real-world generalizability across shifting deployment environments",
            "High computational and memory demands during large-scale evaluation",
            "Lack of unified benchmark datasets and standardized evaluation protocols"
        ]
    }


def extract_key_terms(text: str, max_terms: int = 8) -> List[str]:
    """Extracts significant capitalized multi-word terms and domain phrases from text."""
    if not text:
        return []
    
    terms = []
    
    # 1. Look for acronyms (e.g. BERT, LoRA, GNN, CNN, SVM, BLEU, AUC)
    acronyms = re.findall(r'\b[A-Z]{2,8}\b', text)
    for acr in acronyms:
        if acr not in ["THE", "AND", "FOR", "WITH", "THAT", "THIS", "FROM", "JSON", "API", "HTTP", "URL", "PDF"]:
            if acr not in terms:
                terms.append(acr)
                
    # 2. Look for Title Case multi-word phrases (e.g. "Multimodal Fusion", "Fake News Detection")
    phrases = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+\b', text)
    for ph in phrases:
        cleaned = ph.strip()
        if len(cleaned) > 5 and cleaned not in terms:
            terms.append(cleaned)
            
    # 3. Look for terms in quotes or parentheses
    quoted = re.findall(r'["\']([^"\']{3,30})["\']', text)
    for q in quoted:
        if q not in terms:
            terms.append(q)
            
    return terms[:max_terms]


def extract_literature_context(
    topic: str,
    domain: str = "",
    keywords: str = "",
    objectives: str = "",
    papers: Optional[List[Dict[str, Any]]] = None,
    paper_analyses: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """
    Constructs a rich, dynamic literature context from the input parameters and
    discovered research papers.
    """
    papers = papers or []
    paper_analyses = paper_analyses or []
    
    # Clean topic string
    clean_topic = topic.strip()
    if clean_topic.lower().startswith("research on ") or clean_topic.lower().startswith("analysis of "):
        clean_topic = clean_topic[12:].strip()
        
    profile = detect_domain_profile(clean_topic, domain, keywords)
    domain_name = domain.strip() if domain.strip() else profile["name"]
    
    # Collect all titles and abstracts
    titles = []
    abstracts = []
    full_text_snippets = []
    
    for p in papers:
        t = p.get("title", "").strip()
        if t and t not in titles:
            titles.append(t)
        a = p.get("abstract", "").strip()
        if a:
            abstracts.append(a)
            
    for a in paper_analyses:
        d = a.get("analysis_data", a)
        t = d.get("paper_title", "").strip()
        if t and t not in titles:
            titles.append(t)
            
    combined_corpus = " ".join(titles + abstracts[:5])
    
    # Extract real mentioned algorithms from the discovered papers
    real_algos = []
    known_algos = [
        "BERT", "RoBERTa", "DeBERTa", "GPT", "LLaMA", "T5", "CLIP", "ViT",
        "ResNet", "DenseNet", "BiLSTM", "LSTM", "CNN", "GNN", "GCN", "GAT",
        "AutoML", "XGBoost", "LightGBM", "Random Forest", "SVM", "Naive Bayes",
        "Contrastive Learning", "Self-Supervised Learning", "Reinforcement Learning",
        "PPO", "DPO", "Diffusion Model", "VAE", "GAN", "TF-IDF", "Word2Vec",
        "Cross-Attention", "Dual-Stream", "Late Fusion", "Early Fusion", "Attention Mechanism"
    ]
    for algo in known_algos:
        if re.search(r'\b' + re.escape(algo) + r'\b', combined_corpus, re.IGNORECASE):
            if algo not in real_algos:
                real_algos.append(algo)
                
    # Also grab capitalized terms
    paper_terms = extract_key_terms(combined_corpus, max_terms=6)
    
    # Combine algorithms: real discovered + profile defaults
    selected_algos = (real_algos + profile["default_algos"])[:4]
    
    # Discovered datasets
    known_datasets = [
        "Twitter", "Reddit", "Weibo", "Instagram", "Facebook", "TikTok", "YouTube",
        "Wikipedia", "Common Crawl", "Kaggle", "PolitiFact", "LIAR", "MMHS150K",
        "OffensEval", "HASOC", "HateXplain", "COCO", "ImageNet", "MIMIC", "GLUE",
        "SQuAD", "PubMed", "arXiv", "SemEval", "Formspring", "Ask.fm"
    ]
    real_datasets = []
    for ds in known_datasets:
        if re.search(r'\b' + re.escape(ds) + r'\b', combined_corpus, re.IGNORECASE):
            if ds not in real_datasets:
                real_datasets.append(ds)
                
    selected_datasets = (real_datasets + profile["default_datasets"])[:3]
    
    # Format primary paper titles
    p1 = titles[0] if len(titles) > 0 else f"Foundational Studies in {clean_topic}"
    p2 = titles[1] if len(titles) > 1 else (titles[0] if titles else f"Recent Advances in {clean_topic}")
    p3 = titles[2] if len(titles) > 2 else p2
    
    return {
        "topic": clean_topic,
        "domain": domain_name,
        "primary_papers": [p1, p2, p3],
        "all_titles": titles[:5],
        "algorithms": selected_algos,
        "datasets": selected_datasets,
        "metrics": profile["metrics"],
        "challenges": profile["challenges"],
        "key_terms": paper_terms,
        "paper_count": len(titles)
    }
