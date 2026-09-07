import jwt
from pwdlib import PasswordHash
from dotenv import load_dotenv
from pydantic import BaseModel
from schemas import UserLogin, AccessToken
from models import User
from datetime import datetime, UTC, timedelta, timezone
import os

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", default="15")  # default is 15 minutes
)

password_hasher = PasswordHash.recommended()


class Token(BaseModel):
    username: str
    expire: int


class TokenResponse(BaseModel):
    payload: str  # signed Token


def sign_jwt(payload: str):
    return f"secret_jwt: {payload}"


def verify_password(password: str, hash: str) -> bool:
    return password_hasher.verify(password=password, hash=hash)


def authenticate_user(user: User, db_user: UserLogin) -> bool:
    verified: bool = verify_password(user.password, db_user.password_hash)
    return verified


def create_access_token(data: AccessToken):
    payload = data.model_dump()
    if not payload["exp"]:
        payload.update(
            {
                "exp": datetime.now(UTC)
                + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
                "expire": True,
            }
        )

    encoded_payload = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_payload


def decode_token(token: str) -> AccessToken:
    decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    return AccessToken(**decoded)
