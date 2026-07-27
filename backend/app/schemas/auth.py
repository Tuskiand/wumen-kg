from pydantic import BaseModel


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    token: str
    id: int
    username: str
    expires_in: int
    role: str


class UserResponse(BaseModel):
    id: int
    username: str
    role: str
    is_active: bool
