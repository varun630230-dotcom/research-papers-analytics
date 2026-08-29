from app.providers.llm_provider import BaseLLMProvider
from app.prompts.templates import CRITIC_REVIEW_PROMPT
import json
from app.utils.helpers import safe_json_loads

class CriticAgent:
    def __init__(self, llm: BaseLLMProvider):
        self.llm = llm

    async def review(self, project_result: dict) -> dict:
        prompt = CRITIC_REVIEW_PROMPT.format(results=json.dumps(project_result, default=str))
        try:
            reviewed = await self.llm.generate_json(prompt, system_prompt="You are a rigorous academic critic. Review evidence and claims.")
            if not reviewed:
                return project_result
            return reviewed
        except Exception as e:
            print(f"Critic review failed: {e}")
            return project_result
