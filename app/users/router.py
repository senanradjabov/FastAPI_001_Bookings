from fastapi import APIRouter, HTTPException, status, Response, Depends

from app.users.auth import get_password_hash, authenticate_user, create_access_token
from app.users.dao import UsersDAO
from app.users.models import Users
from app.users.schemes import SUserAuth, SUser
from app.users.dependencies import get_current_user, get_current_admin_user

router = APIRouter(
    prefix="/auth",
    tags=["Auth & Users"]
)


@router.post("/register")
async def register_user(response: Response, user_data: SUserAuth):
    existing_user = await UsersDAO().get_one_or_none(email=user_data.email)

    if existing_user:
        raise HTTPException(status_code=404, detail="User with this email have.")

    hashed_password = get_password_hash(user_data.password)

    await UsersDAO().add(email=user_data.email, hashed_password=hashed_password)

    user = await UsersDAO().get_one_or_none(email=user_data.email)

    access_token = create_access_token({"sub": str(user.id)})
    response.set_cookie("booking_access_token", access_token, httponly=True)

    return {"message": "Successfully register"}


@router.post("/login")
async def login_user(response: Response, user_data: SUserAuth):
    user: Users | None = await authenticate_user(user_data.email, user_data.password)

    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    access_token = create_access_token({"sub": str(user.id)})
    response.set_cookie("booking_access_token", access_token, httponly=True)

    return {"access_token": access_token}


@router.post("/logout")
async def logout_user(response: Response) -> dict:
    response.delete_cookie("booking_access_token", httponly=True)

    return {"message": "Successfully logout"}


@router.get("/me")
async def get_user_by_self(user: SUser = Depends(get_current_user)) -> SUser:
    return user


@router.get("/all")
async def get_all_users_by_admin(user: Users = Depends(get_current_admin_user)) -> list[SUser]:
    if user:
        return await UsersDAO().get_all()
