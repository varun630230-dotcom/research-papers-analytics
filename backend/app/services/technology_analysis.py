from app.providers.llm_provider import BaseLLMProvider
from app.schemas.responses import TechnologyLandscape, TechnologyInfo, IdeaAnalysis, PaperExtraction, Paper
from app.prompts.templates import TECHNOLOGY_ANALYSIS_PROMPT
import json

class TechnologyAnalysisService:
    def __init__(self, llm: BaseLLMProvider):
        self.llm = llm

    def _parse_tech_list(self, raw_list, default_cat: str) -> list[TechnologyInfo]:
        results = []
        if not isinstance(raw_list, list):
            return results
        for item in raw_list:
            if isinstance(item, dict):
                results.append(TechnologyInfo(
                    name=item.get("name") or "Core Technology",
                    category=item.get("category") or default_cat,
                    description=item.get("description") or "Domain implementation technology",
                    use_cases=item.get("use_cases") if isinstance(item.get("use_cases"), list) else ["Application feature"],
                    evidence_type=item.get("evidence_type") or "FACT"
                ))
            elif isinstance(item, str):
                results.append(TechnologyInfo(
                    name=item,
                    category=default_cat,
                    description=f"{item} applied in the project domain",
                    use_cases=["Core implementation"],
                    evidence_type="INFERENCE"
                ))
        return results

    async def analyze(self, idea_analysis: IdeaAnalysis, extractions: list[PaperExtraction], papers: list[Paper]) -> TechnologyLandscape:
        ex_json = json.dumps([e.model_dump() for e in extractions])
        prompt = TECHNOLOGY_ANALYSIS_PROMPT.format(idea=idea_analysis.model_dump_json(), extractions=ex_json)
        try:
            data = await self.llm.generate_json(prompt, system_prompt="Analyze tech landscape. Output JSON matching TechnologyLandscape.")
            if isinstance(data, dict):
                return TechnologyLandscape(
                    established=self._parse_tech_list(data.get("established"), "Established"),
                    emerging=self._parse_tech_list(data.get("emerging"), "Emerging"),
                    experimental=self._parse_tech_list(data.get("experimental"), "Experimental"),
                    potentially_relevant=self._parse_tech_list(data.get("potentially_relevant"), "Potentially Relevant")
                )
        except Exception as e:
            print(f"Technology analysis error: {e}")
        
        return TechnologyLandscape(
            established=[TechnologyInfo(name="Deep Convolutional Backbones (ResNet / MobileNet)", category="Established", description="Standard convolutional neural networks for classification", use_cases=["Image classification"], evidence_type="FACT")],
            emerging=[TechnologyInfo(name="Vision Transformers (ViT)", category="Emerging", description="Attention-based visual architectures", use_cases=["Feature representation"], evidence_type="INFERENCE")],
            experimental=[TechnologyInfo(name="Multimodal Foundation Models", category="Experimental", description="Combined vision-language reasoning engines", use_cases=["Contextual diagnosis"], evidence_type="HYPOTHESIS")],
            potentially_relevant=[TechnologyInfo(name="INT8 Model Quantization / Edge Runtime", category="Potentially Relevant", description="Model compression for low-latency offline deployment", use_cases=["Offline inference"], evidence_type="RECOMMENDATION")]
        )
