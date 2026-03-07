from groq import Groq
from app.core.config import settings
from app.services.rag_service import query_knowledge_base

RELEVANCE_THRESHOLD = 0.3
GROQ_MODEL = "llama-3.1-8b-instant"

SYSTEM_PROMPT = """You are an emergency response assistant for a disaster coordination platform.

CRITICAL RULES:
1. Answer ONLY using the provided emergency documents below
2. If the documents don't contain relevant information, say exactly: "I don't have verified information on this topic. Please contact emergency services."
3. Never make up procedures, medications, or advice not in the documents
4. Always be clear, calm, and actionable
5. Start with the most critical action first
6. Keep answers concise — people in emergencies need quick guidance

Your answer must be grounded in the provided documents only."""

def build_context(retrieved_docs: list) -> str:
    if not retrieved_docs:
        return ""
    context = "VERIFIED EMERGENCY DOCUMENTS:\n\n"
    for i, doc in enumerate(retrieved_docs, 1):
        context += f"Document {i} (Source: {doc['source']}, Category: {doc['category']}):\n"
        context += f"{doc['content']}\n\n"
    return context

def ask_ai_assistant(question: str) -> dict:
    # Step 1 — retrieve relevant docs from ChromaDB
    retrieved_docs = query_knowledge_base(question, n_results=2)

    # Step 2 — filter by relevance threshold
    relevant_docs = [doc for doc in retrieved_docs if doc["relevance_score"] >= RELEVANCE_THRESHOLD]

    # Step 3 — if no relevant docs found, return safe fallback
    if not relevant_docs:
        return {
            "question": question,
            "answer": "I don't have verified information on this topic. Please contact emergency services immediately by calling 112.",
            "sources": [],
            "grounded": False
        }

    # Step 4 — build context from relevant docs
    context = build_context(relevant_docs)

    # Step 5 — call Groq LLM with context + question
    client = Groq(api_key=settings.GROQ_API_KEY)

    try:
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"{context}\n\nQuestion: {question}"}
            ],
            temperature=0.1,  # low temperature = more factual, less creative
            max_tokens=512
        )

        answer = response.choices[0].message.content

        return {
            "question": question,
            "answer": answer,
            "sources": [
                {
                    "source": doc["source"],
                    "category": doc["category"],
                    "relevance_score": doc["relevance_score"]
                }
                for doc in relevant_docs
            ],
            "grounded": True
        }

    except Exception as e:
        raise RuntimeError(f"AI service error: {str(e)}")