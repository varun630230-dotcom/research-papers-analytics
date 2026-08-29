from abc import ABC, abstractmethod
import json
import re
import asyncio
from app.config import settings

class BaseLLMProvider(ABC):
    @abstractmethod
    async def generate(self, prompt: str, system_prompt: str = '', temperature: float = 0.3, max_tokens: int = 4000) -> str:
        pass

    @abstractmethod
    async def generate_json(self, prompt: str, system_prompt: str = '', temperature: float = 0.2, max_tokens: int = 4000) -> dict:
        pass

    def _parse_json_response(self, response: str) -> dict:
        try:
            cleaned = response.strip()
            match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', cleaned)
            if match:
                cleaned = match.group(1).strip()
            return json.loads(cleaned)
        except json.JSONDecodeError as e:
            # Try to find the first { or [ and last } or ]
            start_idx = min([i for i in [cleaned.find('{'), cleaned.find('[')] if i != -1], default=-1)
            end_idx = max([cleaned.rfind('}'), cleaned.rfind(']')], default=-1)
            if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                try:
                    return json.loads(cleaned[start_idx:end_idx+1])
                except Exception:
                    pass
            raise ValueError(f"Failed to parse JSON response: {str(e)} -> Response: {response[:200]}...")

class GeminiProvider(BaseLLMProvider):
    def __init__(self):
        from google import genai
        api_key = settings.GEMINI_API_KEY or settings.GOOGLE_API_KEY
        self.client = genai.Client(api_key=api_key)
        self.model_name = settings.gemini_model

    async def _execute_with_retry(self, fn, max_retries: int = 5):
        for attempt in range(max_retries):
            try:
                loop = asyncio.get_running_loop()
                return await loop.run_in_executor(None, fn)
            except Exception as e:
                err_str = str(e)
                if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str or "quota" in err_str.lower():
                    delay = 8.0 + (attempt * 4.0)
                    print(f"Gemini rate limit hit (attempt {attempt + 1}/{max_retries}). Backing off for {delay}s...")
                    await asyncio.sleep(delay)
                else:
                    raise e
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, fn)

    async def generate(self, prompt: str, system_prompt: str = '', temperature: float = 0.3, max_tokens: int = 4000) -> str:
        from google.genai import types
        config = types.GenerateContentConfig(
            system_instruction=system_prompt if system_prompt else None,
            temperature=temperature,
            max_output_tokens=max_tokens,
        )
        response = await self._execute_with_retry(
            lambda: self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=config
            )
        )
        return response.text

    async def generate_json(self, prompt: str, system_prompt: str = '', temperature: float = 0.2, max_tokens: int = 4000) -> dict:
        from google.genai import types
        config = types.GenerateContentConfig(
            system_instruction=system_prompt if system_prompt else None,
            temperature=temperature,
            max_output_tokens=max_tokens,
            response_mime_type="application/json"
        )
        response = await self._execute_with_retry(
            lambda: self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=config
            )
        )
        return self._parse_json_response(response.text)

class OpenAIProvider(BaseLLMProvider):
    def __init__(self):
        from openai import AsyncOpenAI
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.openai_model

    async def generate(self, prompt: str, system_prompt: str = '', temperature: float = 0.3, max_tokens: int = 4000) -> str:
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=temperature,
            max_tokens=max_tokens
        )
        return response.choices[0].message.content

    async def generate_json(self, prompt: str, system_prompt: str = '', temperature: float = 0.2, max_tokens: int = 4000) -> dict:
        response_text = await self.generate(prompt, system_prompt, temperature, max_tokens)
        return self._parse_json_response(response_text)

class AnthropicProvider(BaseLLMProvider):
    def __init__(self):
        from anthropic import AsyncAnthropic
        self.client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.model = settings.anthropic_model

    async def generate(self, prompt: str, system_prompt: str = '', temperature: float = 0.3, max_tokens: int = 4000) -> str:
        response = await self.client.messages.create(
            model=self.model,
            system=system_prompt,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=max_tokens
        )
        return response.content[0].text

    async def generate_json(self, prompt: str, system_prompt: str = '', temperature: float = 0.2, max_tokens: int = 4000) -> dict:
        response_text = await self.generate(prompt, system_prompt, temperature, max_tokens)
        return self._parse_json_response(response_text)

class GroqProvider(BaseLLMProvider):
    def __init__(self):
        from groq import AsyncGroq
        self.client = AsyncGroq(api_key=settings.GROQ_API_KEY)
        self.model = settings.groq_model

    async def generate(self, prompt: str, system_prompt: str = '', temperature: float = 0.3, max_tokens: int = 4000) -> str:
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=temperature,
            max_tokens=max_tokens
        )
        return response.choices[0].message.content

    async def generate_json(self, prompt: str, system_prompt: str = '', temperature: float = 0.2, max_tokens: int = 4000) -> dict:
        response_text = await self.generate(prompt, system_prompt, temperature, max_tokens)
        return self._parse_json_response(response_text)

def get_llm_provider(config) -> BaseLLMProvider:
    if config.GEMINI_API_KEY or config.GOOGLE_API_KEY:
        return GeminiProvider()
    elif config.OPENAI_API_KEY:
        return OpenAIProvider()
    elif config.ANTHROPIC_API_KEY:
        return AnthropicProvider()
    elif config.GROQ_API_KEY:
        return GroqProvider()
    else:
        raise ValueError("No LLM provider configured. Please set GEMINI_API_KEY, OPENAI_API_KEY, ANTHROPIC_API_KEY, or GROQ_API_KEY in your .env file.")
