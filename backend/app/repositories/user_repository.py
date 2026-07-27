from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User


class UserRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def list_users(self) -> list[User]:
        return list(self.session.scalars(select(User).order_by(User.created_at.desc())))

    def get_by_id(self, user_id: int) -> User | None:
        return self.session.get(User, user_id)

    def get_by_username(self, username: str) -> User | None:
        statement = select(User).where(User.username == username)
        return self.session.scalar(statement)

    def count_active_admins(self) -> int:
        statement = select(User).where(User.role == "admin", User.is_active.is_(True))
        return len(list(self.session.scalars(statement)))

    def create_user(self, username: str, password_hash: str, role: str, is_active: bool) -> User:
        user = User(
            username=username,
            password_hash=password_hash,
            role=role,
            is_active=is_active,
        )
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user

    def update_user(
        self,
        user: User,
        *,
        username: str | None = None,
        password_hash: str | None = None,
        role: str | None = None,
        is_active: bool | None = None,
    ) -> User:
        if username is not None:
            user.username = username
        if password_hash is not None:
            user.password_hash = password_hash
        if role is not None:
            user.role = role
        if is_active is not None:
            user.is_active = is_active
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user

    def delete_user(self, user: User) -> None:
        self.session.delete(user)
        self.session.commit()
