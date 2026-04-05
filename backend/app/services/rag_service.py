import chromadb
from chromadb.utils import embedding_functions
from chromadb.config import Settings as ChromaSettings
from knowledge_base.emergency_docs import EMERGENCY_DOCS
from app.core.config import settings

def get_chroma_client():
    from app.core.config import settings
    if settings.CHROMA_HOST:
        # Docker mode — connect to ChromaDB container via HTTP
        return chromadb.HttpClient(
            host=settings.CHROMA_HOST,
            port=8000
        )
    # Local mode — use persistent local path
    return chromadb.PersistentClient(
        path=settings.CHROMA_PATH,
        settings=ChromaSettings(anonymized_telemetry=False)
    )

def get_embedding_function():
    return embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=settings.EMBEDDING_MODEL
    )

def load_knowledge_base() -> None:
    try:
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
    except Exception as e:
        print(f"Warning: Failed to load knowledge base: {e}")
        print("The application will continue without RAG functionality.")

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