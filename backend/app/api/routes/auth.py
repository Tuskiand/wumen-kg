from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.core.security import create_access_token, get_current_user
from app.db.mysql import get_db_session
from app.schemas.auth import LoginRequest, TokenResponse, UserResponse
from app.schemas.user import RegisterRequest, RegisterResponse, UserCreate
from app.services.user_service import UserService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(
    payload: LoginRequest,
    settings: Settings = Depends(get_settings),
    session: Session = Depends(get_db_session),
) -> TokenResponse:
    user_service = UserService(session)
    user = user_service.get_user_by_username(payload.username)
    if user is None or not user.is_active or not user_service.verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")
    return TokenResponse(
        token=create_access_token(user.id, user.username, user.role, settings),
        id=user.id,
        username=user.username,
        expires_in=settings.jwt_expire_minutes * 60,
        role=user.role,
    )


@router.get("/me", response_model=UserResponse)
def me(current_user: dict = Depends(get_current_user)) -> UserResponse:
    return UserResponse(**current_user)


@router.post("/register", response_model=RegisterResponse)
def register(
    payload: RegisterRequest,
    session: Session = Depends(get_db_session),
) -> RegisterResponse:
    user_service = UserService(session)
    existing = user_service.get_user_by_username(payload.username)
    if existing is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists")
    user = user_service.create_user(
        UserCreate(
            username=payload.username,
            password=payload.password,
            role="user",
            is_active=True,
        )
    )
    return RegisterResponse(**user.model_dump())


@router.post("/logout")
def logout() -> dict[str, str]:
    return {"message": "Logged out"}
