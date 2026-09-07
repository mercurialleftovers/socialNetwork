from pydantic import BaseModel
from datetime import datetime


class UserLogin(BaseModel):
    username: str
    password: str


class UserCreate(UserLogin):
    email: str


class UserResponse(BaseModel):
    username: str
    email: str


class PostCreate(BaseModel):
    title: str
    content: str


class AccessToken(BaseModel):
    username: str
    expire: bool = False
    exp: datetime | None = None


class TokenResponse(BaseModel):
    token: str
