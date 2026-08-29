from app.providers.llm_provider import BaseLLMProvider
from app.schemas.responses import IdeaAnalysis
from app.prompts.templates import IDEA_ANALYSIS_PROMPT

class IdeaAnalysisService:
    def __init__(self, llm: BaseLLMProvider):
        self.llm = llm

    async def analyze(self, idea: str, goal: str, domain: str, technical_level: str, constraints: str) -> IdeaAnalysis:
        prompt = IDEA_ANALYSIS_PROMPT.format(
            idea=idea, goal=goal, domain=domain, technical_level=technical_level, constraints=constraints
        )
        data = await self.llm.generate_json(prompt, system_prompt="You are an expert AI research scientist.")
        return IdeaAnalysis(**data)
