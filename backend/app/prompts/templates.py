IDEA_ANALYSIS_PROMPT = """Analyze the following user idea:
Idea: {idea}
Goal: {goal}
Domain: {domain}
Level: {technical_level}
Constraints: {constraints}

Extract:
1. Problem domain and core problem statement.
2. Target users and deployment contexts.
3. Potential modalities (text, vision, audio, tabular, multimodal).
4. Potential algorithms and technical approaches.
5. Key constraints.
6. 6 to 10 specific, high-precision academic search queries tailored to find both direct problem research and relevant benchmarks (e.g., specific task terms, classification variants, dataset benchmarks).

Output JSON matching this exact structure:
{{
  "problem_domain": "string",
  "core_problem": "string",
  "target_users": "string",
  "potential_input": "string",
  "potential_output": "string",
  "potential_technologies": ["tech1", "tech2"],
  "key_constraints": ["constraint1"],
  "search_queries": ["query1", "query2", "query3", "query4", "query5", "query6"]
}}"""

RELEVANCE_CLASSIFICATION_PROMPT = """You are a rigorous scientific reviewer.
Evaluate the following candidate academic papers against the specific research problem:
User Idea / Core Problem: {idea_summary}
Target Domain: {domain}

For each candidate paper, classify its relevance into EXACTLY ONE of:
- "DIRECT": The paper directly addresses the user's specific problem, target task, or core research objective.
- "RELATED": The paper addresses a closely related problem, adjacent task, domain dataset, or evaluation challenge.
- "BACKGROUND": The paper introduces foundational theory, general architectures (e.g. BERT, RoBERTa, Transformers, general LLMs, PaLM, CNNs) without specifically focusing on the user's core problem.
- "IRRELEVANT": The paper does not provide meaningful evidence or relevance for the user's specific problem.

IMPORTANT CRITICAL RULES:
1. A foundational language model paper (like PaLM, GPT, BERT) MUST be classified as "BACKGROUND" unless the paper specifically evaluates the user's exact problem.
2. Direct problem papers MUST receive higher relevance_scores (80-100) than general background papers (40-65) or irrelevant papers (0-30).
3. Do NOT let citation counts alone elevate a general background paper into a direct paper.

Candidate Papers:
{papers_json}

Return a JSON list of objects matching:
[
  {{
    "paper_id": "string",
    "relevance_category": "DIRECT",
    "relevance_score": 95,
    "relevance_explanation": "Directly evaluates automated cyberbullying detection using transformer models on social media text.",
    "key_method": "BiLSTM with Attention / Fine-tuned RoBERTa",
    "key_dataset": "Twitter / Formspring Cyberbullying Dataset",
    "main_finding": "Contextual embeddings improve detection of subtle harassment by 14% over baselines.",
    "main_limitation": "High false positive rate on sarcastic and slang-heavy comments."
  }}
]"""

SCIENTIFIC_EXTRACTION_PROMPT = """Extract deep structured scientific findings from the provided academic text:
Title: {title}
Paper ID: {paper_id}
Document Content:
{content}

Rules:
- If a field cannot be found from the text, return an empty list or "Not explicitly detailed in document".
- Do NOT fabricate metrics, dataset sizes, or baseline numbers.
- Distinguish directly stated facts (evidence_type: "FACT") from analytical interpretations (evidence_type: "INFERENCE").

Return JSON matching:
{{
  "paper_id": "{paper_id}",
  "title": "{title}",
  "problem": "string",
  "objective": "string",
  "methodology": "string",
  "algorithms": ["algo1", "algo2"],
  "models": ["model1", "model2"],
  "datasets_used": ["dataset1"],
  "dataset_size": ["e.g. 10,000 labeled samples"],
  "features": ["text tokens", "user metadata"],
  "metrics": ["F1-score", "Accuracy", "Precision", "Recall"],
  "results": ["Achieved 89.4% F1-score on benchmark test split"],
  "strengths": ["Robust feature extraction", "Evaluated on multi-source corpus"],
  "limitations": ["Limited generalization across different social platforms", "High computational latency"],
  "future_work": ["Multimodal image-text integration", "Adversarial robustness evaluation"],
  "key_findings": ["Contextual representations outperform bag-of-words by significant margin"],
  "research_contribution": "Novel attention-based mechanism for subtle abuse pattern identification",
  "extraction_level": "{extraction_level}",
  "evidence_type": "FACT"
}}"""

METHOD_COMPARISON_PROMPT = """Compare the methods and algorithms extracted from the verified DIRECT and RELATED papers:
{extractions}

Rules:
- Match each row to its source paper.
- Include extraction level ("Full-text PDF analyzed" or "Abstract-only").
- If studies evaluated different datasets, tasks, or conditions, provide an explicit comparability_warning: "Results are reported across different datasets and experimental conditions; direct numerical comparison should be interpreted cautiously."

Return a JSON list of MethodComparison objects:
[
  {{
    "paper_title": "string",
    "method": "Fine-Tuned RoBERTa with Adversarial Training",
    "dataset": "Twitter Harassment Corpus",
    "performance": "F1-Score: 0.884",
    "advantages": "Captures semantic nuance in short informal text",
    "limitations": "Requires substantial GPU memory for batch inference",
    "source_paper_id": "string",
    "evidence_type": "FACT",
    "extraction_level": "Full-text PDF analyzed",
    "comparability_warning": "Evaluated on Twitter short-text; performance differs from long-form comments."
  }}
]"""

DATASET_ANALYSIS_PROMPT = """Identify and evaluate datasets mentioned in the DIRECT and RELATED research extractions:
{extractions}

Classify datasets into:
- "Core Dataset": Dedicated to the user's specific problem.
- "Benchmark Dataset": Broadly used domain benchmark.
- "Background Pretraining Corpus": Generic language/vision pretraining corpora (e.g. Common Crawl, Wikipedia, BookCorpus).

Return a JSON list of DatasetInfo objects:
[
  {{
    "name": "Wikipedia Toxic Comments Dataset",
    "domain": "Online Content Moderation / NLP",
    "size": "159,571 labeled comments",
    "data_type": "Text with multi-label annotations",
    "classes": "toxic, severe_toxic, obscene, threat, insult, identity_hate",
    "availability": "Public Open Access (Kaggle / CC0)",
    "license": "CC0 Public Domain",
    "common_usage": "Benchmarking toxicity and abusive language detectors",
    "strengths": "Large diverse crowd-annotated sample size",
    "limitations": "Severe class imbalance and demographic annotation bias",
    "potential_gaps": "Lack of conversational thread context and cross-platform metadata",
    "papers_using": ["Paper Title 1", "Paper Title 2"],
    "dataset_category": "Core Dataset",
    "evidence_type": "INFERENCE"
  }}
]"""

TECHNOLOGY_ANALYSIS_PROMPT = """Analyze the technology landscape based on the user's idea and verified research:
Idea: {idea}
Extractions: {extractions}

Categorize technologies into:
- Established: Standard mature tools and models (e.g. BERT, RoBERTa, PyTorch, HuggingFace).
- Emerging: Rapidly growing modern approaches (e.g. Parameter-Efficient Fine-Tuning LoRA, MobileViT, Small Language Models).
- Experimental: Novel architectures with early proof-of-concept (e.g. Multimodal Graph-Transformer Fusion, Neuro-symbolic safety rules).
- Potentially Relevant: Technologies from adjacent domains worth integrating (e.g. ONNX Runtime INT8 edge quantization, Differential Privacy).

Return JSON matching TechnologyLandscape:
{{
  "established": [
    {{
      "name": "RoBERTa / DeBERTa Backbones",
      "category": "Transformer NLP",
      "description": "Pretrained masked language models for text classification",
      "use_cases": ["Text representation", "Toxicity scoring"],
      "relevant_papers": ["Paper Title"],
      "advantages": "High benchmark accuracy on standard text",
      "limitations": "Compute-heavy for high-throughput stream inference",
      "maturity_level": "Established",
      "evidence_type": "FACT"
    }}
  ],
  "emerging": [
    {{
      "name": "Lightweight LoRA / Quantized Adapters",
      "category": "Efficient AI",
      "description": "Adapter-based fine-tuning reducing parameter count and memory",
      "use_cases": ["Domain adaptation with low RAM"],
      "relevant_papers": [],
      "advantages": "Enables deployment on low-cost compute",
      "limitations": "Requires careful rank tuning to prevent catastrophic forgetting",
      "maturity_level": "Emerging",
      "evidence_type": "INFERENCE"
    }}
  ],
  "experimental": [
    {{
      "name": "Multimodal Vision-Language Graph Reasoning",
      "category": "Multimodal AI",
      "description": "Joint reasoning over meme images, OCR text, and user interaction graphs",
      "use_cases": ["Multimodal cyberbullying and hateful meme detection"],
      "relevant_papers": [],
      "advantages": "Handles visual metaphors and overlaid hateful captions",
      "limitations": "Complex multi-stage alignment and high inference latency",
      "maturity_level": "Experimental",
      "evidence_type": "HYPOTHESIS"
    }}
  ],
  "potentially_relevant": [
    {{
      "name": "INT8 ONNX Runtime Edge Optimization",
      "category": "Edge AI",
      "description": "Post-training quantization for real-time browser/mobile inference",
      "use_cases": ["Client-side privacy-preserving moderation"],
      "relevant_papers": [],
      "advantages": "Zero server data transmission and sub-20ms inference",
      "limitations": "Slight precision degradation on fine-grained classes",
      "maturity_level": "Established",
      "evidence_type": "RECOMMENDATION"
    }}
  ]
}}"""

EXISTING_SOLUTIONS_PROMPT = """Analyze existing solutions, benchmarks, and products in the problem area:
Idea: {idea}
Extractions: {extractions}

Classify each solution into:
- Academic Model (e.g. published baseline architectures)
- Open-Source Implementation (e.g. Detoxify, Perspective API wrappers, HuggingFace models)
- Commercial Product (e.g. OpenAI Moderation API, Google Perspective API, Two Hat, Utopia Analytics)
- API / Platform
- General-Purpose Technology (e.g. general LLMs like GPT-4/PaLM used generally)

Return a JSON list of ExistingSolution objects:
[
  {{
    "name": "Google Perspective API / Detoxify",
    "type": "API / Platform",
    "target_users": "Online platform moderators, game developers, social forums",
    "purpose": "Automated scoring of toxicity, severe toxicity, and profanity in comments",
    "main_features": ["REST API", "Pretrained toxicity models", "Multi-attribute scoring"],
    "technology": "Convolutional Neural Networks & Multilingual BERT",
    "strengths": ["High throughput", "Widely benchmarked API", "Multilingual support"],
    "weaknesses": ["False positives on benign reclaimed slurs or non-hostile swear words", "Ignores conversation thread context"],
    "missing_features": ["Conversational context tracking", "Custom platform community guidelines fine-tuning", "Offline client-side inference"],
    "source": "Public Documentation & Academic Benchmarks",
    "evidence_type": "FACT"
  }}
]"""

MULTI_PAPER_GAP_PROMPT = """You are a senior research scientist.
Synthesize recurring limitations, conflicting results, and future work across ALL analyzed DIRECT and RELATED papers to identify multi-paper evidence-backed research gaps:

Analyzed Paper Extractions:
{extractions}

Idea Context:
{idea}

RULES:
1. Do NOT elevate a single isolated paper limitation into a high-confidence domain gap.
2. Group semantically similar limitations into unified clusters (e.g., cross-platform generalization failure, sarcasm/implicit abuse misclassification, conversational context omission, multimodal discordance, severe class imbalance).
3. For each gap, list the exact supporting paper titles and synthesize the extracted evidence.
4. Gap types must be one of: Knowledge, Methodological, Dataset / Data, Evaluation, Technology, Application, Integration, Generalization, Explainability, Deployment.
5. Set confidence based on the number of corroborating papers (>=2 papers = High / Medium-High).

Return a JSON list of Gap objects:
[
  {{
    "title": "Severe Generalization Degradation in Cross-Platform and Out-of-Domain Settings",
    "type": "Generalization",
    "description": "Models trained on one platform (e.g., Twitter) experience steep performance drops when evaluated on other platforms (e.g., Reddit or Instagram) due to platform-specific slang, character limits, and community norms.",
    "evidence": "Multiple studies demonstrate that F1-scores drop by 15-30% in zero-shot cross-platform evaluations.",
    "supporting_sources": ["Paper Title A", "Paper Title B"],
    "supporting_evidence_passages": [
      "Paper A: 'Model performance dropped from 0.88 to 0.61 F1 when tested on unseen Reddit dataset.'",
      "Paper B: 'Out-of-domain evaluation revealed severe reliance on platform-specific hashtag artifacts.'"
    ],
    "number_of_supporting_papers": 2,
    "confidence": "High",
    "potential_impact": "Solving this enables deployable moderation systems that do not require massive per-platform re-annotation.",
    "validation_status": "Evidence-backed",
    "reasoning_summary": "Corroborated across independent cross-domain benchmark evaluations in literature."
  }}
]"""

MARKET_GAP_PROMPT = """Analyze product and market gaps in the target problem area:
Idea: {idea}
Existing Solutions: {solutions}
Research Gaps: {research_gaps}

Focus on operational, commercial, accessibility, cost, and user-experience bottlenecks (NOT merely algorithmic limitations).
Examples:
- Privacy-sensitive client-side processing vs cloud server logging
- Custom community rule adaptation vs rigid global toxicity filters
- Explainable moderation with appeal workflows vs black-box bans
- Cost barrier for small community moderators

Return a JSON list of MarketGap objects:
[
  {{
    "problem": "Small online communities cannot afford commercial moderation APIs or maintain dedicated human moderation teams",
    "type": "Cost",
    "affected_users": "Community moderators, Discord server owners, niche open-source forums",
    "current_solutions": "Commercial cloud APIs charging per-request or rigid keyword blocklists",
    "current_features": "Per-call API pricing, generic global toxicity scores",
    "current_limitations": "Expensive at high volume; rigid blocklists cause excessive false positives",
    "missing_capability": "Self-hostable, lightweight open-source moderation engine with customizable community guidelines",
    "potential_opportunity": "An open-source or affordable edge-native moderation bot with local rule tuning",
    "evidence": "Analysis of current commercial API pricing models and community moderator forum reports",
    "confidence": "High",
    "validation_required": "Pilot deployment and cost comparison across small-to-medium community forums",
    "evidence_type": "INFERENCE"
  }}
]"""

TECHNOLOGY_GAP_PROMPT = """Identify concrete technology and engineering gaps:
Idea: {idea}
Technologies: {technologies}
Extractions: {extractions}

Focus on engineering bottlenecks: compute requirements, latency, edge deployment, explainability, multimodal pipeline synchronization.

Return a JSON list of TechnologyGap objects:
[
  {{
    "technology_problem": "High memory footprint and latency of large transformer ensembles during real-time stream moderation",
    "current_technology": "Heavy BERT/RoBERTa ensemble models running on cloud GPUs",
    "limitation": "High inference latency (>200ms) and prohibitive cloud hosting costs for continuous real-time chat monitoring",
    "emerging_technology": "Knowledge Distillation + INT8 Quantized Small Language Models",
    "potential_combination": "DistilRoBERTa student model with hardware-accelerated ONNX runtime execution",
    "opportunity": "Sub-25ms real-time chat filtering with 80% reduced memory footprint",
    "implementation_difficulty": "Medium",
    "evidence_type": "INFERENCE"
  }}
]"""

OPPORTUNITY_PROMPT = """Synthesize research gaps, market gaps, and technology gaps into ranked, buildable innovation opportunities:
Research Gaps: {research_gaps}
Market Gaps: {market_gaps}
Technology Gaps: {tech_gaps}
User Idea: {idea}

RULES:
- Provide transparent scores (0–100) across all 8 dimensions.
- The 'overall' score should reflect the weighted formula: Research Gap (30%), Market Evidence (20%), Tech Feasibility (20%), Data Availability (10%), Differentiation (10%), Evidence Confidence (10%).
- Do NOT invent unverified precise numerical claims (e.g. write "Target low-latency real-time inference (target to validate experimentally)" instead of unsupported numbers).

Return a JSON list of Opportunity objects:
[
  {{
    "title": "Context-Aware & Privacy-Preserving Cyberbullying Detection Engine with Local Rule Adaptation",
    "problem": "Current moderation tools rely on rigid out-of-context keyword matching or expensive cloud APIs that misclassify informal slang and violate user privacy.",
    "existing_situation": "Cloud-based generic toxicity APIs with high false positives on slang and zero thread-context awareness.",
    "identified_gap": "Absence of lightweight, context-aware models capable of running locally with customizable community rules.",
    "proposed_innovation": "A lightweight distilled language model incorporating conversational thread context and customizable community rule embeddings.",
    "target_users": "Community moderators, social platform developers, messaging app creators",
    "required_technologies": ["DistilBERT / TinyLlama", "ONNX Runtime", "FastAPI", "React / Next.js Dashboard"],
    "data_requirements": "Multi-turn conversational moderation benchmarks and community-annotated slang datasets",
    "potential_impact": "Reduces false positive bans by an estimated 20-30% while preserving user chat privacy through on-premise execution.",
    "technical_difficulty": "Medium",
    "research_potential": "High",
    "market_potential": "High",
    "differentiation_potential": "High differentiation via localized privacy-first architecture and thread-context modeling",
    "novelty_assessment": "Moderate to High similarity on base classification, High differentiation on conversational context and local rule tuning",
    "evidence_level": "Evidence-backed",
    "validation_steps": [
      "Benchmark cross-domain accuracy on Twitter and Reddit datasets",
      "Measure inference latency on target CPU hardware",
      "Conduct double-blind moderator testing on ambiguous slang comments"
    ],
    "scores": {{
      "research_gap": 90,
      "market_gap": 88,
      "technology_feasibility": 85,
      "implementation_difficulty": 50,
      "data_availability": 82,
      "innovation_potential": 92,
      "market_potential": 90,
      "evidence_confidence": 88,
      "overall": 89
    }}
  }}
]"""

NOVELTY_PROMPT = """Perform an objective novelty and differentiation assessment for the user's idea:
Idea: {idea}
Core Research: {core_papers}
Existing Solutions: {solutions}

CRITICAL RULES:
- Never claim the idea is '100% novel', 'completely unique', or 'guaranteed patentable'.
- Use objective similarity levels: 'Low similarity detected', 'Moderate similarity detected', 'High similarity detected'.
- Highlight both common existing baselines and genuine potential differentiators.
- Include explicit disclaimer that this is an AI-assisted analysis and not a formal prior art / patent search.

Return JSON matching NoveltyAssessment:
{{
  "similarity_score": "Moderate similarity detected",
  "common_approaches": [
    "Standard fine-tuning of BERT/RoBERTa on isolated single comments",
    "Keyword blocklists and dictionary-based profanity filters"
  ],
  "unique_aspects": [
    "Incorporation of multi-turn conversational thread context",
    "Edge-native execution ensuring user chat data remains private"
  ],
  "potential_differentiators": [
    "Custom community guideline adapter weights",
    "Explainable reasoning rationale generated for moderator review"
  ],
  "overcrowded_areas": [
    "Generic single-sentence toxicity classification on Wikipedia benchmark data"
  ],
  "innovation_directions": [
    "Focus on subtle harassment, gaslighting, and sarcasm",
    "Multimodal meme and image caption joint moderation"
  ],
  "novelty_confidence": "High",
  "component_assessments": [
    {{
      "component": "Core Text Classifier",
      "novelty_level": "Moderate",
      "explanation": "Builds on established transformer architectures while integrating conversational context"
    }},
    {{
      "component": "Privacy-Preserving Edge Architecture",
      "novelty_level": "High",
      "explanation": "Solves major data privacy and latency bottlenecks present in cloud API solutions"
    }}
  ],
  "final_assessment": "The proposed project addresses recognized generalization and privacy limitations in current moderation systems, demonstrating strong practical innovation potential.",
  "disclaimer": "This novelty assessment is AI-assisted and based on indexed scientific and technical literature. It does not constitute a formal patent search or legal novelty opinion."
}}"""

RECOMMENDATION_PROMPT = """Generate an actionable, evidence-derived project recommendation:
Idea: {idea}
Top Opportunities: {opportunities}
Research Findings: {extractions}

Show the logical chain from Research Findings -> Identified Gaps -> Technology Opportunity -> Recommended Architecture.

Return JSON matching ProjectRecommendation:
{{
  "title": "string",
  "problem_statement": "string",
  "existing_system": "string",
  "limitations_of_existing": ["limitation1", "limitation2"],
  "identified_opportunity": "string",
  "proposed_solution": "string",
  "core_innovation": "string",
  "target_users": "string",
  "key_features": ["feature1", "feature2", "feature3", "feature4"],
  "technology_stack": ["Python", "FastAPI", "React / Next.js", "ONNX Runtime", "PostgreSQL / SQLite"],
  "ai_models": ["DistilRoBERTa", "DeBERTa-v3"],
  "datasets": ["Wikipedia Toxic Comments", "Jigsaw Unintended Bias", "Twitter Cyberbullying Corpus"],
  "apis": ["HuggingFace Transformers", "Perspective API (for baseline benchmarking)"],
  "database": "SQLite / PostgreSQL for audit logs and custom rule storage",
  "deployment_strategy": "Containerized microservice (Docker) deployable on-premise or cloud with sub-30ms latency target",
  "evaluation_metrics": ["Macro F1-Score (>0.88)", "Cross-Platform F1 Retention (>85%)", "Inference Latency (target <30ms)", "False Positive Rate (<4%)"],
  "risks": ["Demographic bias in crowd-annotated training data", "Adversarial evasion through obfuscated leetspeak"],
  "development_difficulty": "Medium",
  "expected_outcome": "A complete, deployable context-aware moderation intelligence system providing real-time abuse detection with transparent explanations.",
  "future_improvements": ["Multimodal image-text meme moderation", "Federated learning across decentralized community nodes"]
}}"""

ARCHITECTURE_PROMPT = """Generate system architecture components and data flow for:
Recommendation: {recommendation}

Return JSON matching Architecture:
{{
  "components": [
    {{
      "name": "Moderation Web UI / Client",
      "description": "Dashboard for real-time alert review, rule management, and false positive audit",
      "technology": "Next.js 14, Tailwind CSS, TypeScript",
      "connections": ["Backend API Service"]
    }},
    {{
      "name": "Backend Intelligence API",
      "description": "Asynchronous REST / WebSocket service handling text stream ingestion and scoring",
      "technology": "FastAPI (Async Python)",
      "connections": ["Inference Engine", "Database Store"]
    }},
    {{
      "name": "Edge AI Inference Runtime",
      "description": "Optimized ONNX / PyTorch runtime executing quantized transformer models with conversational context memory",
      "technology": "ONNX Runtime / TensorRT",
      "connections": ["Backend Intelligence API"]
    }},
    {{
      "name": "Database Store",
      "description": "Stores community rules, flagged audit history, feedback annotations, and performance telemetry",
      "technology": "SQLite / PostgreSQL",
      "connections": ["Backend Intelligence API"]
    }}
  ],
  "diagram_description": "Chat Stream -> FastAPI API -> Context Buffer -> ONNX Inference Engine -> Alert / Action -> Web Dashboard",
  "data_flow": [
    "Incoming text comment or message received via REST/WebSocket",
    "Pre-processor extracts text, normalizes character obfuscations, and attaches conversational thread history",
    "Quantized transformer runs inference to compute fine-grained toxicity and abuse category probabilities",
    "Rules engine compares scores against custom community guideline thresholds",
    "Action triggered (allow, flag for moderator review, or soft-mute) and telemetry logged to database"
  ]
}}"""

ROADMAP_PROMPT = """Generate a realistic 7-phase implementation roadmap for:
Recommendation: {recommendation}

Return a JSON list of 7 RoadmapPhase objects:
[
  {{
    "phase_number": 1,
    "title": "Problem Scoping, Literature & Benchmark Dataset Curation",
    "tasks": [
      "Acquire and clean public moderation datasets (Jigsaw, Twitter Harassment)",
      "Establish evaluation split and baseline performance benchmarks",
      "Define annotation taxonomy and ethical guidelines"
    ],
    "complexity": "Easy",
    "estimated_duration": "2 weeks"
  }},
  {{
    "phase_number": 2,
    "title": "Data Preprocessing, Slang Normalization & Context Pipeline",
    "tasks": [
      "Build text normalization module for leetspeak and informal shorthand",
      "Construct sliding-window conversational context buffer",
      "Analyze and mitigate class imbalance"
    ],
    "complexity": "Medium",
    "estimated_duration": "2 weeks"
  }},
  {{
    "phase_number": 3,
    "title": "Core AI Model Development & Multi-Domain Fine-Tuning",
    "tasks": [
      "Fine-tune DeBERTa and RoBERTa backbones with cross-domain regularization",
      "Implement contextual attention head",
      "Evaluate cross-platform transfer on held-out datasets"
    ],
    "complexity": "Hard",
    "estimated_duration": "3 weeks"
  }},
  {{
    "phase_number": 4,
    "title": "Model Optimization, Knowledge Distillation & Quantization",
    "tasks": [
      "Distill knowledge into lightweight student model (DistilRoBERTa)",
      "Perform INT8 post-training quantization via ONNX Runtime",
      "Profile latency and memory consumption across target hardware"
    ],
    "complexity": "Hard",
    "estimated_duration": "3 weeks"
  }},
  {{
    "phase_number": 5,
    "title": "Backend API & Custom Rules Engine Development",
    "tasks": [
      "Implement high-throughput async FastAPI service with WebSocket stream support",
      "Build customizable community threshold rules engine",
      "Create audit logging and appeal queue database models"
    ],
    "complexity": "Medium",
    "estimated_duration": "3 weeks"
  }},
  {{
    "phase_number": 6,
    "title": "Web Dashboard UI & Real-Time Alert System",
    "tasks": [
      "Develop moderator dashboard with real-time flag feed and explanation cards",
      "Implement rule configuration and false-positive feedback loops",
      "Conduct end-to-end load testing under simulated high-volume traffic"
    ],
    "complexity": "Medium",
    "estimated_duration": "2 weeks"
  }},
  {{
    "phase_number": 7,
    "title": "Deployment, In-Field Pilot & Evaluation Report",
    "tasks": [
      "Deploy containerized service to target environment",
      "Execute pilot trial with community moderators",
      "Compile comprehensive technical evaluation and validation report"
    ],
    "complexity": "Easy",
    "estimated_duration": "1 week"
  }}
]"""

CRITIC_REVIEW_PROMPT = """Review the analysis results:
{results}

Check for:
1. Irrelevant or general papers erroneously categorized as core Top 5 papers.
2. Fabricated numbers or metrics without evidence.
3. Unsupported novelty or gap claims.
4. Correct mapping of datasets and methods to papers.

Return the cleaned, validated JSON structure."""
