# app/agents/triage_agent.py
import json
import time
from langgraph.graph import StateGraph, END
from langchain_groq import ChatGroq
from app.agents.state import TriageState
from app.services.rag_service import query_knowledge_base
from app.core.config import settings

# ── LLM client (reuses your Groq key from config) ──────────────
def get_llm():
    return ChatGroq(
        api_key=settings.GROQ_API_KEY,
        model_name=settings.GROQ_MODEL,
        temperature=0.0,   # 0 for consistent classification
        max_tokens=256
    )

# ── NODE 1: Classify incident type ─────────────────────────────
def classify_type(state: TriageState) -> TriageState:
    """
    Takes raw incident text.
    Outputs: classified_type + type_confidence.
    """
    llm = get_llm()

    prompt = f"""You are an emergency dispatcher. Classify this incident into exactly one type.

        Incident: "{state['incident_text']}"

        Respond in JSON only. No other text. Format:
        {{
        "type": "flood" | "fire" | "medical" | "accident" | "other",
        "confidence": 0.0 to 1.0,
        "reason": "one sentence why"
        }}"""

    response = llm.invoke(prompt)
    
    try:
        # parse JSON from LLM response
        raw = response.content.strip()
        # strip markdown code blocks if LLM wraps in ```json
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        result = json.loads(raw.strip())
        
        return {
            **state,
            "classified_type": result.get("type", state["incident_type"]),
            "type_confidence": float(result.get("confidence", 0.5)),
        }
    except (json.JSONDecodeError, KeyError):
        # fallback: use the type the user submitted
        return {
            **state,
            "classified_type": state["incident_type"],
            "type_confidence": 0.5,
        }

# ── NODE 2: Agentic RAG ─────────────────────────────────────────
def retrieve_context(state: TriageState) -> TriageState:
    """
    DECIDES whether to retrieve from ChromaDB.
    Retrieves only if type_confidence is low OR type is ambiguous.
    This is the 'agentic' part — it thinks before retrieving.
    """
    confidence = state.get("type_confidence", 0.5)
    incident_type = state.get("classified_type", "other")
    
    print(f"DEBUG: classified_type={incident_type}, confidence={confidence}")

    # Decision: skip retrieval if we're very confident about a clear type
    if confidence >= 0.85 and incident_type != "other":
        return {
            **state,
            "rag_context": None,
            "rag_used": False,
        }

    # Otherwise retrieve — build a targeted query
    query = f"{incident_type} emergency: {state['incident_text']}"
    docs = query_knowledge_base(query, n_results=2)
    
    # filter by relevance threshold (reuse your existing setting)
    relevant = [d for d in docs if d["relevance_score"] >= settings.RELEVANCE_THRESHOLD]

    if not relevant:
        return {
            **state,
            "rag_context": None,
            "rag_used": False,
        }

    # Build context string from retrieved docs
    context = "\n\n".join([
        f"[{d['source']}]: {d['content']}" for d in relevant
    ])

    return {
        **state,
        "rag_context": context,
        "rag_used": True,
    }

# ── NODE 3: Score severity ──────────────────────────────────────
def score_severity(state: TriageState) -> TriageState:
    """
    Final reasoning node.
    Has everything: incident text, classified type, optional RAG context.
    Outputs: severity + confidence + reasoning.
    """
    llm = get_llm()

    # build context section only if RAG was used
    context_section = ""
    if state.get("rag_used") and state.get("rag_context"):
        context_section = f"""
            Relevant emergency protocols:
            {state['rag_context']}
            """

    prompt = f"""You are an emergency triage specialist. Assess the severity of this incident.

            Incident type: {state.get('classified_type', 'unknown')}
            Incident description: "{state['incident_text']}"
            {context_section}

            Severity levels:
            - Critical: immediate life threat, requires response in minutes
            - High: serious situation, response within 30 minutes
            - Medium: urgent but stable, response within 2 hours  
            - Low: non-urgent, can wait for next available responder

            Respond in JSON only. No other text. Format:
            {{
            "severity": "Critical" | "High" | "Medium" | "Low",
            "confidence": 0.0 to 1.0,
            "reasoning": "2-3 sentences explaining why this severity"
            }}"""

    response = llm.invoke(prompt)

    try:
        raw = response.content.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        result = json.loads(raw.strip())

        return {
            **state,
            "severity": result.get("severity", "High"),
            "severity_confidence": float(result.get("confidence", 0.5)),
            "reasoning": result.get("reasoning", "Unable to determine reasoning"),
        }
    except (json.JSONDecodeError, KeyError):
        return {
            **state,
            "severity": "High",   # safe default — better to over-triage
            "severity_confidence": 0.3,
            "reasoning": "Classification failed — defaulting to High for safety",
        }

# ── Build the graph ─────────────────────────────────────────────
def build_triage_graph() -> StateGraph:
    graph = StateGraph(TriageState)

    # add nodes
    graph.add_node("classify_type", classify_type)
    graph.add_node("retrieve_context", retrieve_context)
    graph.add_node("score_severity", score_severity)

    # add edges — linear flow for now
    graph.set_entry_point("classify_type")
    graph.add_edge("classify_type", "retrieve_context")
    graph.add_edge("retrieve_context", "score_severity")
    graph.add_edge("score_severity", END)

    return graph.compile()

# ── Public function called by incident_service ──────────────────
def run_triage(incident_text: str, incident_type: str) -> dict:
    """
    Entry point for the triage agent.
    Returns triage result as a plain dict.
    """
    start = time.time()

    graph = build_triage_graph()

    initial_state: TriageState = {
        "incident_text": incident_text,
        "incident_type": incident_type,
        "classified_type": None,
        "type_confidence": None,
        "rag_context": None,
        "rag_used": None,
        "severity": None,
        "severity_confidence": None,
        "reasoning": None,
    }

    result = graph.invoke(initial_state)

    processing_ms = int((time.time() - start) * 1000)

    return {
        "severity": result["severity"],
        "confidence": result["severity_confidence"],
        "reasoning": result["reasoning"],
        "rag_used": result["rag_used"],
        "classified_type": result["classified_type"],
        "processing_ms": processing_ms,
    }