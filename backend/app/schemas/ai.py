from pydantic import BaseModel
from typing import List, Optional

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
    grounded: bool  # True = answer from docs, False = no docs found