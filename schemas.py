from pydantic import BaseModel


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
