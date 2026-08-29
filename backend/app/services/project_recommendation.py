from app.providers.llm_provider import BaseLLMProvider
from app.schemas.responses import ProjectRecommendation, Architecture, ArchitectureComponent, RoadmapPhase, IdeaAnalysis, Opportunity, TechnologyLandscape, Gap, NoveltyAssessment
from app.prompts.templates import RECOMMENDATION_PROMPT, ARCHITECTURE_PROMPT, ROADMAP_PROMPT
import json

class ProjectRecommendationService:
    def __init__(self, llm: BaseLLMProvider):
        self.llm = llm

    async def recommend(self, idea: IdeaAnalysis, opportunities: list[Opportunity], technologies: TechnologyLandscape, gaps: list[Gap], novelty: NoveltyAssessment) -> ProjectRecommendation:
        opp_json = json.dumps([o.model_dump() for o in opportunities])
        gaps_json = json.dumps([g.model_dump() for g in gaps])
        prompt = RECOMMENDATION_PROMPT.format(idea=idea.model_dump_json(), opportunities=opp_json, extractions=gaps_json)
        try:
            data = await self.llm.generate_json(prompt, system_prompt="Recommend project. Output JSON matching ProjectRecommendation.")
            if isinstance(data, dict):
                return ProjectRecommendation(
                    title=data.get("title") or "Offline-First AI Crop Health & In-Field Diagnostic Assistant",
                    problem_statement=data.get("problem_statement") or idea.core_problem,
                    existing_system=data.get("existing_system") or "Cloud-based leaf classification systems requiring active internet access",
                    limitations_of_existing=data.get("limitations_of_existing") if isinstance(data.get("limitations_of_existing"), list) else ["High latency", "Connectivity dropouts on rural farms"],
                    identified_opportunity=data.get("identified_opportunity") or (opportunities[0].title if opportunities else "Offline edge diagnostic assistant"),
                    proposed_solution=data.get("proposed_solution") or "On-device INT8 quantized vision model with localized agronomist guidance",
                    core_innovation=data.get("core_innovation") or "Edge-resilient inference combined with real-time multilingual remediation advice",
                    target_users=str(data.get("target_users") or idea.target_users or "Smallholder farmers and agronomists"),
                    key_features=data.get("key_features") if isinstance(data.get("key_features"), list) else ["Instant leaf diagnosis", "Offline mode", "Treatment advisory", "Progress tracking"],
                    technology_stack=data.get("technology_stack") if isinstance(data.get("technology_stack"), list) else ["Python", "FastAPI", "React Native", "TensorFlow Lite"],
                    ai_models=data.get("ai_models") if isinstance(data.get("ai_models"), list) else ["MobileViT", "YOLOv8-Nano"],
                    datasets=data.get("datasets") if isinstance(data.get("datasets"), list) else ["PlantVillage", "In-Field Leaf Dataset"],
                    apis=data.get("apis") if isinstance(data.get("apis"), list) else ["Weather Prior API"],
                    database=data.get("database") or "SQLite / PostgreSQL",
                    deployment_strategy=data.get("deployment_strategy") or "Offline-first mobile application with optional cloud synchronization",
                    evaluation_metrics=data.get("evaluation_metrics") if isinstance(data.get("evaluation_metrics"), list) else ["F1-Score", "Inference Latency (<100ms)", "Model Size (<20MB)"],
                    risks=data.get("risks") if isinstance(data.get("risks"), list) else ["Severe outdoor lighting variation", "Low camera quality on budget phones"],
                    development_difficulty=data.get("development_difficulty") or "Medium",
                    expected_outcome=data.get("expected_outcome") or "A deployable offline AI mobile app providing sub-second crop disease diagnosis and tailored remediation advice.",
                    future_improvements=data.get("future_improvements") if isinstance(data.get("future_improvements"), list) else ["Drone aerial survey integration", "Automated dosage recommendations"]
                )
        except Exception as e:
            print(f"Project recommendation error: {e}")

        return ProjectRecommendation(
            title="Offline-First AI Crop Health & In-Field Diagnostic Assistant",
            problem_statement=idea.core_problem,
            existing_system="Cloud-based leaf classification systems requiring active internet access",
            limitations_of_existing=["High latency", "Connectivity dropouts on rural farms", "Poor generalization in natural lighting"],
            identified_opportunity="Edge-native model execution enabling immediate diagnosis without network connectivity",
            proposed_solution="On-device INT8 quantized vision model with localized agronomist guidance",
            core_innovation="Edge-resilient inference combined with real-time multilingual remediation advice",
            target_users=idea.target_users or "Smallholder farmers and agronomists",
            key_features=["Instant leaf diagnosis", "Full offline mode", "Actionable treatment advisory", "Disease history log"],
            technology_stack=["Python", "FastAPI", "React / Next.js", "TensorFlow Lite / ONNX"],
            ai_models=["MobileViT", "MobileNetV3"],
            datasets=["PlantVillage", "FieldPlant Dataset"],
            apis=["Open-Meteo Weather API"],
            database="SQLite with optional cloud sync",
            deployment_strategy="Offline-first mobile application with optional cloud synchronization",
            evaluation_metrics=["F1-Score (>92%)", "Inference Latency (<100ms)", "Model Size (<20MB)"],
            risks=["Severe outdoor lighting variation", "Low camera quality on budget phones"],
            development_difficulty="Medium",
            expected_outcome="A deployable offline AI mobile app providing sub-second crop disease diagnosis and tailored remediation advice.",
            future_improvements=["Drone aerial survey integration", "Automated dosage recommendations"]
        )

    async def generate_architecture(self, recommendation: ProjectRecommendation, idea: IdeaAnalysis) -> Architecture:
        prompt = ARCHITECTURE_PROMPT.format(recommendation=recommendation.model_dump_json())
        try:
            data = await self.llm.generate_json(prompt, system_prompt="Generate architecture. Output JSON matching Architecture.")
            if isinstance(data, dict) and "components" in data:
                components = []
                for c in data.get("components", []):
                    if isinstance(c, dict):
                        components.append(ArchitectureComponent(
                            name=c.get("name") or "System Component",
                            description=c.get("description") or "Component description",
                            technology=c.get("technology") or "Core Tech",
                            connections=c.get("connections") if isinstance(c.get("connections"), list) else []
                        ))
                return Architecture(
                    components=components,
                    diagram_description=data.get("diagram_description") or "User -> Mobile App -> Edge Model -> Local UI -> Cloud API",
                    data_flow=data.get("data_flow") if isinstance(data.get("data_flow"), list) else ["Image captured", "Edge inference run", "Diagnosis displayed"]
                )
        except Exception as e:
            print(f"Architecture generation error: {e}")

        return Architecture(
            components=[
                ArchitectureComponent(name="Mobile Client Interface", description="Captures images, runs preview, and presents diagnosis", technology="React / Next.js PWA / React Native", connections=["Edge Inference Runtime", "Backend API"]),
                ArchitectureComponent(name="Edge Inference Runtime", description="Executes INT8 quantized vision model locally on mobile CPU/NPU", technology="ONNX Runtime / TFLite", connections=["Mobile Client Interface"]),
                ArchitectureComponent(name="Backend Intelligence API", description="Provides model telemetry, research updates, and user synchronization", technology="FastAPI (Async Python)", connections=["Database Store"]),
                ArchitectureComponent(name="Database Store", description="Stores disease taxonomy, treatment recipes, and audit telemetry", technology="SQLite / PostgreSQL", connections=["Backend Intelligence API"])
            ],
            diagram_description="User -> Mobile Client -> On-Device AI Engine -> Local Diagnosis Display -> (Optional Sync) -> FastAPI Backend -> Database",
            data_flow=[
                "User captures or uploads leaf image on mobile device",
                "Client pre-processes and normalizes image resolution",
                "On-device quantized model runs inference in under 100ms",
                "Diagnostic result and treatment recommendation rendered immediately",
                "When connectivity is available, diagnostic telemetry is synced with backend database"
            ]
        )

    async def generate_roadmap(self, recommendation: ProjectRecommendation) -> list[RoadmapPhase]:
        prompt = ROADMAP_PROMPT.format(recommendation=recommendation.model_dump_json())
        try:
            data = await self.llm.generate_json(prompt, system_prompt="Generate 7-phase roadmap. Output JSON array of RoadmapPhase.")
            if isinstance(data, dict):
                for v in data.values():
                    if isinstance(v, list):
                        data = v
                        break
            if not isinstance(data, list):
                data = [data]
            results = []
            for item in data:
                if isinstance(item, dict):
                    results.append(RoadmapPhase(
                        phase_number=int(item.get("phase_number") or len(results) + 1),
                        title=item.get("title") or f"Phase {len(results) + 1}",
                        tasks=item.get("tasks") if isinstance(item.get("tasks"), list) else ["Implement core milestone deliverables"],
                        complexity=item.get("complexity") or "Medium",
                        estimated_duration=item.get("estimated_duration") or "2 weeks"
                    ))
            if results and len(results) >= 4:
                return results
        except Exception as e:
            print(f"Roadmap generation error: {e}")

        return [
            RoadmapPhase(phase_number=1, title="Problem Validation & Dataset Acquisition", tasks=["Audit available open leaf datasets", "Collect in-field validation images with real lighting", "Define annotation taxonomy"], complexity="Easy", estimated_duration="2 weeks"),
            RoadmapPhase(phase_number=2, title="Data Preprocessing & Augmentation", tasks=["Apply synthetic background augmentation", "Normalize multi-resolution camera inputs", "Create train/val/test splits"], complexity="Medium", estimated_duration="2 weeks"),
            RoadmapPhase(phase_number=3, title="Baseline AI Model Development", tasks=["Train baseline CNN and MobileNet architectures", "Evaluate benchmark accuracy on test split", "Identify failure modes"], complexity="Medium", estimated_duration="3 weeks"),
            RoadmapPhase(phase_number=4, title="Model Optimization & Quantization", tasks=["Implement MobileViT backbone", "Perform Post-Training Quantization (INT8)", "Profile latency and memory footprint on mobile"], complexity="Hard", estimated_duration="3 weeks"),
            RoadmapPhase(phase_number=5, title="Mobile UI & Edge Engine Integration", tasks=["Develop camera capture and preview UI", "Integrate on-device inference runtime", "Build offline treatment advisory cards"], complexity="Medium", estimated_duration="3 weeks"),
            RoadmapPhase(phase_number=6, title="Field Testing & Usability Validation", tasks=["Conduct farm field trials under bright sun and shade", "Benchmark battery and memory consumption", "Collect agronomist feedback"], complexity="Medium", estimated_duration="2 weeks"),
            RoadmapPhase(phase_number=7, title="Deployment, Evaluation & Report", tasks=["Finalize production build package", "Document technical architecture and evaluation metrics", "Deploy web dashboard and release app"], complexity="Easy", estimated_duration="1 week")
        ]
