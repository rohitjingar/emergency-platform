from groq import Groq
from app.core.config import settings
from app.core.exceptions import AIServiceError
from app.services.rag_service import query_knowledge_base

# Groq client created once, reused for all requests
_groq_client: Groq | None = None

def get_groq_client() -> Groq:
    global _groq_client
    if _groq_client is None:
        _groq_client = Groq(api_key=settings.GROQ_API_KEY)
    return _groq_client

SYSTEM_PROMPT = """You are an emergency response assistant for a disaster coordination platform.

CRITICAL RULES:
1. Answer ONLY using the provided emergency documents below
2. If the documents don't contain relevant information, say exactly: "I don't have verified information on this topic. Please contact emergency services."
3. Never make up procedures, medications, or advice not in the documents
4. Always be clear, calm, and actionable
5. Start with the most critical action first
6. Keep answers concise — people in emergencies need quick guidance

Your answer must be grounded in the provided documents only."""

def _build_context(docs: list[dict]) -> str:
    context = "VERIFIED EMERGENCY DOCUMENTS:\n\n"
    for i, doc in enumerate(docs, 1):
        context += f"Document {i} (Source: {doc['source']}, Category: {doc['category']}):\n"
        context += f"{doc['content']}\n\n"
    return context

def ask_ai_assistant(question: str) -> dict:
    # Step 1 — retrieve + filter by relevance threshold
    retrieved = query_knowledge_base(question, n_results=settings.RAG_N_RESULTS)
    relevant = [d for d in retrieved if d["relevance_score"] >= settings.RELEVANCE_THRESHOLD]

    # Step 2 — fallback if nothing relevant found
    if not relevant:
        return {
            "question": question,
            "answer": "I don't have verified information on this topic. Please contact emergency services immediately by calling 112.",
            "sources": [],
            "grounded": False
        }

    # Step 3 — call LLM with context
    try:
        client = get_groq_client()
        response = client.chat.completions.create(
            model=settings.GROQ_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"{_build_context(relevant)}\n\nQuestion: {question}"}
            ],
            temperature=settings.AI_TEMPERATURE,
            max_tokens=settings.AI_MAX_TOKENS
        )
        return {
            "question": question,
            "answer": response.choices[0].message.content,
            "sources": [
                {
                    "source": d["source"],
                    "category": d["category"],
                    "relevance_score": d["relevance_score"]
                }
                for d in relevant
            ],
            "grounded": True
        }
    except Exception as e:
        raise AIServiceError(str(e))