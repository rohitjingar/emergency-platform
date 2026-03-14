# app/agents/state.py
from typing import TypedDict, Optional

class TriageState(TypedDict):
    # ── Input (set before graph runs) ──
    incident_text: str        # raw description from user
    incident_type: str        # "flood", "fire", "medical", "accident", "other"

    # ── Filled by Node 1 ──
    classified_type: Optional[str]     # what LLM thinks the type is
    type_confidence: Optional[float]   # how confident (0.0 - 1.0)

    # ── Filled by Node 2 ──
    rag_context: Optional[str]         # retrieved protocol text, or None
    rag_used: Optional[bool]           # did we retrieve or skip?

    # ── Filled by Node 3 ──
    severity: Optional[str]            # Critical / High / Medium / Low
    severity_confidence: Optional[float]
    reasoning: Optional[str]