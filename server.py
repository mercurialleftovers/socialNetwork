from typing import Annotated
from fastapi import FastAPI, Request, Form, Depends
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy import select
from sqlalchemy.orm import Session

from database import get_db_session
from schemas import UserLogin, UserCreate, UserResponse, PostCreate
from models import User, Post

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


@app.post("/api/user/login", name="login_api", include_in_schema=False)
def login_api(
    user: Annotated[UserLogin, Form()],
    session: Annotated[Session, Depends(get_db_session)],
) -> UserResponse:
    db_user = session.execute(
        select(User).where(User.username == user.username)
    ).scalar_one_or_none()

    if not db_user:
        raise Exception(f"user {user.username} does not exist")

    return db_user


@app.post("/api/user/register", name="register_api", include_in_schema=False)
def register_api(
    user: Annotated[UserCreate, Form()],
    session: Annotated[Session, Depends(get_db_session)],
) -> UserResponse:
    db_user = session.execute(
        select(User).where(User.username == user.username)
    ).scalar_one_or_none()

    if db_user:
        raise Exception(f"user {user.username} already exists")

    session.add(User(**user.model_dump()))
    return user


# TODO(bader): here, you must set the auth cookie, to know the user_id
@app.post("/api/post/create", name="post_create_api", include_in_schema=False)
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
