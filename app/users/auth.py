from datetime import datetime, timedelta, timezone

import jwt
from passlib.context import CryptContext
from pydantic import EmailStr

from app.users.dao import UsersDAO
from app.users.models import Users
from app.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY, ALGORITHM = settings.secret_key_and_algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


async def authenticate_user(email: EmailStr, password: str) -> Users | None:
    user: Users = await UsersDAO().get_one_or_none(email=email)

    if user is None or not verify_password(password, user.hashed_password):
        return None

    return user
