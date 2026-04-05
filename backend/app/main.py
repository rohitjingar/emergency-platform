from contextlib import asynccontextmanager
import threading
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db.database import Base, engine
from app.models import user, incident, volunteer, notification
from app.api.routes import auth, incidents, ai, volunteers, notifications, admin, system

Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup - load knowledge base in background thread
    def load_in_background():
        try:
            from app.services.rag_service import load_knowledge_base
            print("Loading emergency knowledge base in background...")
            load_knowledge_base()
            print("Knowledge base ready!")
        except Exception as e:
            print(f"Warning: Knowledge base loading failed: {e}")
    
    thread = threading.Thread(target=load_in_background, daemon=True)
    thread.start()
    
    yield

app = FastAPI(
    title="Emergency Coordination Platform",
    description="AI-powered emergency response coordination",
    version="0.1.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(incidents.router)
app.include_router(ai.router)
app.include_router(volunteers.router)
app.include_router(notifications.router)
app.include_router(admin.router)
app.include_router(system.router)

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "Emergency Platform is running"}
