from sqlalchemy import insert

from app.dao.base import BaseDAO
from app.database import async_session_maker
from app.users.models import Users


class UsersDAO(BaseDAO):
    model = Users

    @classmethod
    async def add(cls, **data):
        async with async_session_maker() as session:
            query = insert(cls.model).values(**data).returning(cls.model.id)

            result = await session.execute(query)
            await session.commit()

        return result.scalar()
