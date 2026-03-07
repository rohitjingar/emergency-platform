from pydantic import BaseModel
from typing import List

class AIRequest(BaseModel):
    question: str

class SourceDoc(BaseModel):
    source: str
    category: str
    relevance_score: float

class AIResponse(BaseModel):
    question: str
    answer: str
    sources: List[SourceDoc]
    grounded: bool
    injection_detected: bool = False