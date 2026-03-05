from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import settings
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def decode_access_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError:
        return None
    
    
def require_role(allowed_roles: list):
    def role_checker(credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
        token = credentials.credentials
        payload = decode_access_token(token)
        if not payload:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        if payload.get("role") not in allowed_roles:
            raise HTTPException(status_code=403, detail=f"Access denied. Required roles: {allowed_roles}")
        return payload
    return role_checker