from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.db.database import Base, engine
from app.models import user, incident, volunteer, notification
from app.api.routes import auth, incidents, ai, volunteers, notifications, admin
from app.services.rag_service import load_knowledge_base

Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    print("Loading emergency knowledge base...")
    load_knowledge_base()
    print("Knowledge base ready!")
    
    yield
    # shutdown (add cleanup here later if needed)

app = FastAPI(
    title="Emergency Coordination Platform",
    description="AI-powered emergency response coordination",
    version="0.1.0",
    lifespan=lifespan
)

app.include_router(auth.router)
app.include_router(incidents.router)
app.include_router(ai.router)
app.include_router(volunteers.router)
app.include_router(notifications.router)
app.include_router(admin.router)

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "Emergency Platform is running"}