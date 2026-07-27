from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserRead, UserUpdate

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserService:
    def __init__(self, session: Session) -> None:
        self.repository = UserRepository(session)

    def verify_password(self, plain_password: str, password_hash: str) -> bool:
        return password_context.verify(plain_password, password_hash)

    def hash_password(self, plain_password: str) -> str:
        return password_context.hash(plain_password)

    def list_users(self) -> list[UserRead]:
        return [self.to_read_model(user) for user in self.repository.list_users()]

    def get_user_by_username(self, username: str) -> User | None:
        return self.repository.get_by_username(username)

    def get_user_by_id(self, user_id: int) -> User | None:
        return self.repository.get_by_id(user_id)

    def create_user(self, payload: UserCreate) -> UserRead:
        user = self.repository.create_user(
            username=payload.username,
            password_hash=self.hash_password(payload.password),
            role=payload.role,
            is_active=payload.is_active,
        )
        return self.to_read_model(user)

    def update_user(self, user: User, payload: UserUpdate) -> UserRead:
        updated = self.repository.update_user(
            user,
            username=payload.username,
            password_hash=self.hash_password(payload.password) if payload.password else None,
            role=payload.role,
            is_active=payload.is_active,
        )
        return self.to_read_model(updated)

    def delete_user(self, user: User) -> None:
        self.repository.delete_user(user)

    def ensure_admin_user(self, username: str, password: str) -> None:
        existing = self.repository.get_by_username(username)
        password_hash = self.hash_password(password)
        if existing is None:
            self.repository.create_user(
                username=username,
                password_hash=password_hash,
                role="admin",
                is_active=True,
            )
            return
        self.repository.update_user(
            existing,
            password_hash=password_hash,
            role="admin",
            is_active=True,
        )

    def active_admin_count(self) -> int:
        return self.repository.count_active_admins()

    @staticmethod
    def to_read_model(user: User) -> UserRead:
        return UserRead(
            id=user.id,
            username=user.username,
            role=user.role,
            is_active=user.is_active,
        )
