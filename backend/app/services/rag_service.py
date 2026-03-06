import chromadb
from chromadb.utils import embedding_functions
from chromadb.config import Settings
from knowledge_base.emergency_docs import EMERGENCY_DOCS

COLLECTION_NAME = "emergency_knowledge"

def get_chroma_client():
    return chromadb.PersistentClient(
        path="./chroma_db",
        settings=Settings(anonymized_telemetry=False)
    )

def get_embedding_function():
    return embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )

def load_knowledge_base():
    client = get_chroma_client()
    ef = get_embedding_function()
    
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=ef
    )

    existing = collection.get()
    if len(existing["ids"]) > 0:
        print(f"Knowledge base already loaded: {len(existing['ids'])} docs")
        return collection

    documents = [doc["content"] for doc in EMERGENCY_DOCS]
    ids = [doc["id"] for doc in EMERGENCY_DOCS]
    metadatas = [doc["metadata"] for doc in EMERGENCY_DOCS]

    collection.add(documents=documents, ids=ids, metadatas=metadatas)
    print(f"Loaded {len(documents)} emergency documents into ChromaDB")
    return collection

def query_knowledge_base(question: str, n_results: int = 2):
    client = get_chroma_client()
    ef = get_embedding_function()
    
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=ef
    )
    
    results = collection.query(
        query_texts=[question],
        n_results=n_results
    )
    
    docs = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]
    
    return [
        {
            "content": doc,
            "source": meta["source"],
            "category": meta["category"],
            "relevance_score": round(1 - distance, 3)
        }
        for doc, meta, distance in zip(docs, metadatas, distances)
    ]