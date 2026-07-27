from pydantic import BaseModel, Field


class UserBase(BaseModel):
    username: str = Field(min_length=3, max_length=64)
    role: str = "user"
    is_active: bool = True


class UserCreate(UserBase):
    password: str = Field(min_length=6, max_length=128)


class UserUpdate(BaseModel):
    username: str | None = Field(default=None, min_length=3, max_length=64)
    password: str | None = Field(default=None, min_length=6, max_length=128)
    role: str | None = None
    is_active: bool | None = None


class UserRead(BaseModel):
    id: int
    username: str
    role: str
    is_active: bool


class RegisterRequest(BaseModel):
    username: str = Field(min_length=3, max_length=64)
    password: str = Field(min_length=6, max_length=128)


class RegisterResponse(BaseModel):
    id: int
    username: str
    role: str
    is_active: bool
