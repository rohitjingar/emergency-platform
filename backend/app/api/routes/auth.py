from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.user import UserRegister, UserLogin, UserResponse, TokenResponse
from app.services.auth_service import register_user, login_user
from app.core.exceptions import AppException

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserResponse)
def register(data: UserRegister, db: Session = Depends(get_db)):
    try:
        return register_user(db, data)
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)

@router.post("/login", response_model=TokenResponse)
def login(data: UserLogin, db: Session = Depends(get_db)):
    try:
        return login_user(db, data.email, data.password)
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)