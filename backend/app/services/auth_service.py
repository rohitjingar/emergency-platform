from sqlalchemy.orm import Session
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserRegister
from app.core.security import hash_password, verify_password, create_access_token
from app.core.exceptions import DuplicateEmailError, InvalidRoleError, InvalidCredentialsError
from app.core.config import settings

def register_user(db: Session, data: UserRegister) -> dict:
    if data.role not in settings.VALID_ROLES:
        raise InvalidRoleError(settings.VALID_ROLES)

    repo = UserRepository(db)

    if repo.get_by_email(data.email):
        raise DuplicateEmailError()

    user = repo.create(
        email=data.email,
        hashed_password=hash_password(data.password),
        role=data.role
    )
    return user

def login_user(db: Session, email: str, password: str) -> dict:
    repo = UserRepository(db)
    user = repo.get_by_email(email)

    if not user or not verify_password(password, user.hashed_password):
        raise InvalidCredentialsError()

    token = create_access_token({"sub": str(user.id), "role": user.role})
    return {"access_token": token, "token_type": "bearer", "role": user.role}