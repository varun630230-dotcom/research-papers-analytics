from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite+aiosqlite:///./innovate_ai.db"
    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""
    GROQ_API_KEY: str = ""
    GEMINI_API_KEY: str = ""
    GOOGLE_API_KEY: str = ""
    OPENALEX_EMAIL: str = ""
    SEMANTIC_SCHOLAR_API_KEY: str = ""
    CORS_ORIGINS: str = "http://localhost:3000"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    @property
    def has_llm_provider(self) -> bool:
        return bool(self.GEMINI_API_KEY or self.GOOGLE_API_KEY or self.OPENAI_API_KEY or self.ANTHROPIC_API_KEY or self.GROQ_API_KEY)

    @property
    def has_research_sources(self) -> bool:
        return True

    @property
    def gemini_model(self) -> str:
        return "gemini-3.5-flash-lite"

    @property
    def openai_model(self) -> str:
        return "gpt-4o-mini"

    @property
    def anthropic_model(self) -> str:
        return "claude-3-5-haiku-latest"

    @property
    def groq_model(self) -> str:
        return "llama-3.1-70b-versatile"

settings = Settings()
