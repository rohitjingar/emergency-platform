from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str

    # JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Groq AI
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.1-8b-instant"
    AI_MAX_TOKENS: int = 512
    AI_TEMPERATURE: float = 0.1

    # RAG
    RELEVANCE_THRESHOLD: float = 0.15
    RAG_N_RESULTS: int = 2
    CHROMA_PATH: str = "./chroma_db"
    CHROMA_COLLECTION: str = "emergency_knowledge"
    EMBEDDING_MODEL: str = "all-mpnet-base-v2"

    # Auth
    VALID_ROLES: set = {"affected_user", "volunteer", "hospital", "admin"}
    
    # ── new Redis fields ──
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_INCIDENT_QUEUE: str = "incidents:new"
    IDEMPOTENCY_WINDOW_SECONDS: int = 300  # 5 minutes

    class Config:
        env_file = ".env"

settings = Settings()