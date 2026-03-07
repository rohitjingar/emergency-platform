from fastapi import APIRouter, Depends, HTTPException
from app.schemas.ai import AIRequest, AIResponse
from app.services.ai_service import ask_ai_assistant
from app.core.dependencies import get_current_user
from app.core.exceptions import AppException

router = APIRouter(prefix="/ai", tags=["AI Assistant"])

@router.post("/ask", response_model=AIResponse)
def ask(
    data: AIRequest,
    current_user: dict = Depends(get_current_user)
):
    try:
        return ask_ai_assistant(data.question)
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)