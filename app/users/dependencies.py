from datetime import datetime, timezone

import jwt
from fastapi import Request, HTTPException, status, Depends
from jwt.exceptions import InvalidTokenError

from app.config import settings
from app.users.dao import UsersDAO
from app.users.models import Users


def get_token(request: Request):
    token = request.cookies.get("booking_access_token")

    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    return token


async def get_current_user(token: str = Depends(get_token)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        expire: str = payload.get("exp")

        # TODO: Точно ли нужна это проверка??? Так как и без него выше дает ошибку ->  Signature has expired.
        if not expire or (int(expire) <= int(datetime.now(timezone.utc).timestamp())):
            raise credentials_exception

        if user_id is None:
            raise credentials_exception

    except InvalidTokenError:
        raise credentials_exception

    user = await UsersDAO().get_one_or_none(id=int(user_id))

    if user is None:
        raise credentials_exception

    return user


async def get_current_admin_user(current_user: Users = Depends(get_current_user)):
    if current_user.id != 3:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    return current_user
