from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import require_admin
from app.db.mysql import get_db_session
from app.schemas.admin import ActionResponse
from app.schemas.user import UserCreate, UserRead, UserUpdate
from app.services.user_service import UserService

router = APIRouter(
    prefix="/admin/users",
    tags=["admin-users"],
    dependencies=[Depends(require_admin)],
)


@router.get("", response_model=list[UserRead])
def list_users(session: Session = Depends(get_db_session)) -> list[UserRead]:
    return UserService(session).list_users()


@router.post("", response_model=UserRead)
def create_user(payload: UserCreate, session: Session = Depends(get_db_session)) -> UserRead:
    user_service = UserService(session)
    existing = user_service.get_user_by_username(payload.username)
    if existing is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists")
    return user_service.create_user(payload)


@router.put("/{user_id}", response_model=UserRead)
def update_user(user_id: int, payload: UserUpdate, session: Session = Depends(get_db_session)) -> UserRead:
    user_service = UserService(session)
    user = user_service.get_user_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if payload.username and payload.username != user.username:
        existing = user_service.get_user_by_username(payload.username)
        if existing is not None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists")
    if user.role == "admin" and payload.role == "user" and user_service.active_admin_count() <= 1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot demote the last active admin")
    if user.role == "admin" and payload.is_active is False and user_service.active_admin_count() <= 1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot disable the last active admin")
    return user_service.update_user(user, payload)


@router.delete("/{user_id}", response_model=ActionResponse)
def delete_user(user_id: int, session: Session = Depends(get_db_session)) -> ActionResponse:
    user_service = UserService(session)
    user = user_service.get_user_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if user.role == "admin" and user_service.active_admin_count() <= 1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot delete the last active admin")
    user_service.delete_user(user)
    return ActionResponse(message="User deleted")
