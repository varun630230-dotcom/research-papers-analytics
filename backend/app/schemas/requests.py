from pydantic import BaseModel
from typing import Literal

class AnalyzeRequest(BaseModel):
    idea: str
    goal: str = "Final Year Project"
    domain: str = "Artificial Intelligence"
    technical_level: str = "Intermediate"
    constraints: str = ""

class ExportRequest(BaseModel):
    format: Literal["markdown", "json"]
