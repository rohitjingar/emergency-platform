from fastapi import APIRouter, Depends, HTTPException
from app.schemas.ai import AIRequest, AIResponse
from app.services.ai_service import ask_ai_assistant
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/ai", tags=["AI Assistant"])


@router.post("/ask", response_model=AIResponse)
def ask(
    data: AIRequest,
    current_user: dict = Depends(get_current_user)
):
    try:
        result = ask_ai_assistant(data.question)
        return result
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))