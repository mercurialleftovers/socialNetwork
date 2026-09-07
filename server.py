from typing import Annotated
from fastapi import FastAPI, Request, Response, Form, Depends
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy import select
from sqlalchemy.orm import Session

from database import get_db_session
from schemas import (
    UserLogin,
    UserCreate,
    UserResponse,
    PostCreate,
    TokenResponse,
    AccessToken,
)
from models import User, Post
from auth import sign_jwt, password_hasher, verify_password, create_access_token

import random
import os

os.system("cls")

templates = Jinja2Templates(directory="templates")

app = FastAPI(name="My FastAPI app")

app.mount(
    path="/static",
    app=StaticFiles(directory="static"),
    name="static",
)


@app.get("/", name="root_view", include_in_schema=False)
@app.get("/home", name="home_view", include_in_schema=False)
def home_view(req: Request):
    return templates.TemplateResponse(
        name="home.html",
        request=req,
        context={"title": "Home"},
    )


@app.get("/login", name="login_view", include_in_schema=False)
def login_view(req: Request):
    return templates.TemplateResponse(
        name="login.html",
        request=req,
        context={"title": "Login"},
    )


@app.get("/register", name="register_view", include_in_schema=False)
def register_view(req: Request):
    return templates.TemplateResponse(
        name="register.html",
        request=req,
        context={"title": "Register"},
    )


@app.get("/post/create", name="create_post_view", include_in_schema=False)
def create_post_view(req: Request):
    return templates.TemplateResponse(
        name="create_post.html",
        request=req,
        context={"title": "post"},
    )


@app.get("/post/view/{id_}", name="post_view", include_in_schema=False)
def post_view(
    req: Request,
    id_: int,
    session: Annotated[Session, Depends(get_db_session)],
):
    post: Post = session.execute(select(Post, id_)).scalars().all()[0]
    print(post)
    print(post.author)

    return templates.TemplateResponse(
        name="post.html",
        request=req,
        context={
            "title": "post",
            "post": post,
        },
    )


@app.get("/users/view", name="users_view", include_in_schema=False)
def users_view(
    req: Request,
    session: Annotated[Session, Depends(get_db_session)],
):
    q = select(User)
    users = session.execute(q).scalars().all()
    return templates.TemplateResponse(
        name="users.html",
        request=req,
        context={
            "title": "post",
            "users": users,
        },
    )


@app.post(
    "/api/user/login",
    name="login_api",
)
def login_api(
    user: Annotated[UserLogin, Form()],
    session: Annotated[Session, Depends(get_db_session)],
    res: Response,
) -> TokenResponse | dict[str, str]:
    db_user = session.execute(
        select(User).where(User.username == user.username)
    ).scalar_one_or_none()

    # authentication:
    if not db_user:
        raise Exception(f"user {user.username} does not exist")

    if verify_password(user.password, db_user.password_hash):
        res.set_cookie(
            "token", create_access_token(AccessToken(username=user.username))
        )
        return {
            "token": create_access_token(AccessToken(username=user.username)),
        }

    return {"msg": "wrong password"}


@app.post(
    "/api/user/register",
    name="register_api",
)
def register_api(
    user: Annotated[UserCreate, Form()],
    session: Annotated[Session, Depends(get_db_session)],
) -> UserResponse:
    db_user = session.execute(
        select(User).where(User.username == user.username)
    ).scalar_one_or_none()

    if db_user:
        raise Exception(f"user {user.username} already exists")

    new_user = user.model_dump()
    new_user["password_hash"] = password_hasher.hash(new_user["password"])
    del new_user[
        "password"
    ]  # TODO(bader): this seems to be against best practices to me, but it works nontheless
    session.add(User(**new_user))
    return user


# TODO(bader): here, you must set the auth cookie, to know the user_id
@app.post(
    "/api/post/create",
    name="post_create_api",
)
def post_api(
    post: Annotated[PostCreate, Form()],
    session: Annotated[Session, Depends(get_db_session)],
) -> PostCreate:
    q = select(User)
    user_id: int = random.choice(
        session.execute(q).scalars().all()
    ).id  # TODO(bader): do cookie stuff here
    # TODO(bader): when getting a random id, use select(Count), instead of getting all users
    new_post = Post(**post.model_dump(), author_id=user_id)
    session.add(new_post)
    return post


@app.get("/token")
def token(res: Response):
    res.set_cookie(key="payload", value=sign_jwt("secret"))
    return {}
