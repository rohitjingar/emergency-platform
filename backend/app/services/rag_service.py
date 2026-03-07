import chromadb
from chromadb.utils import embedding_functions
from chromadb.config import Settings as ChromaSettings
from knowledge_base.emergency_docs import EMERGENCY_DOCS
from app.core.config import settings

def get_chroma_client() -> chromadb.PersistentClient:
    return chromadb.PersistentClient(
        path=settings.CHROMA_PATH,
        settings=ChromaSettings(anonymized_telemetry=False)
    )

def get_embedding_function():
    return embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=settings.EMBEDDING_MODEL
    )

def load_knowledge_base() -> None:
    client = get_chroma_client()
    ef = get_embedding_function()
    collection = client.get_or_create_collection(
        name=settings.CHROMA_COLLECTION,
        embedding_function=ef
    )
    existing = collection.get()
    if len(existing["ids"]) > 0:
        print(f"Knowledge base already loaded: {len(existing['ids'])} docs")
        return

    collection.add(
        documents=[doc["content"] for doc in EMERGENCY_DOCS],
        ids=[doc["id"] for doc in EMERGENCY_DOCS],
        metadatas=[doc["metadata"] for doc in EMERGENCY_DOCS]
    )
    print(f"Loaded {len(EMERGENCY_DOCS)} emergency documents into ChromaDB")

def query_knowledge_base(question: str, n_results: int = 2) -> list[dict]:
    client = get_chroma_client()
    ef = get_embedding_function()
    collection = client.get_or_create_collection(
        name=settings.CHROMA_COLLECTION,
        embedding_function=ef
    )
    results = collection.query(query_texts=[question], n_results=n_results)
    return [
        {
            "content": doc,
            "source": meta["source"],
            "category": meta["category"],
            "relevance_score": round(1 - distance, 3)
        }
        for doc, meta, distance in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0]
        )
    ]