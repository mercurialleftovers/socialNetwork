from __future__ import annotations
from sqlalchemy import ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from database import engine


class Model(DeclarativeBase):
    pass


class User(Model):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    email: Mapped[str] = mapped_column(unique=True)
    password_hash: Mapped[str] = mapped_column()
    # password: Mapped[str] = mapped_column()
    posts: Mapped[list[Post]] = relationship(back_populates="author")

    def __repr__(self) -> str:
        return f"<User {self.username}>"


class Post(Model):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column()
    content: Mapped[str] = mapped_column()
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    author: Mapped[User] = relationship(back_populates="posts")

    def __repr__(self) -> str:
        return f"<Post {self.title} by {self.author.username}>"


# Model.metadata.drop_all(bind=engine)
Model.metadata.create_all(bind=engine)
