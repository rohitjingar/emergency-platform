from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserRegister
from app.core.security import hash_password, verify_password, create_access_token

VALID_ROLES = {"affected_user", "volunteer", "hospital", "admin"}

def register_user(db: Session, data: UserRegister):
    if data.role not in VALID_ROLES:
        raise ValueError(f"Invalid role. Must be one of: {VALID_ROLES}")
    
    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        raise ValueError("Email already registered")
    
    user = User(
        email=data.email,
        hashed_password=hash_password(data.password),
        role=data.role
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def login_user(db: Session, email: str, password: str):
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.hashed_password):
        raise ValueError("Invalid email or password")
    
    token = create_access_token({"sub": str(user.id), "role": user.role})
    return {"access_token": token, "token_type": "bearer", "role": user.role}