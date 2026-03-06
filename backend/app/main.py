from fastapi import FastAPI
from app.db.database import Base, engine
from app.models import user, incident
from app.api.routes import auth, incidents
from app.services.rag_service import load_knowledge_base

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Emergency Coordination Platform",
    description="AI-powered emergency response coordination",
    version="0.1.0"
)

app.include_router(auth.router)
app.include_router(incidents.router)


@app.on_event("startup")
async def startup_event():
    print("Loading emergency knowledge base...")
    load_knowledge_base()
    print("Knowledge base ready!")


@app.get("/health")
def health_check():
    return {"status": "ok", "message": "Emergency Platform is running"}