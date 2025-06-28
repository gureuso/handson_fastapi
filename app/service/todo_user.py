from pydantic import EmailStr

from app.database.mysql import database, TodoUserEntity, todo_user_table


class TodoUserService:
    @staticmethod
    async def create(todo_user_entity: TodoUserEntity) -> TodoUserEntity:
        query = todo_user_table.insert().values(
            email=todo_user_entity.email, password=todo_user_entity.password,
            nickname=todo_user_entity.nickname, created_at=todo_user_entity.created_at,
        )
        ai = await database.execute(query)
        todo_user_entity.id = ai
        return todo_user_entity

    @staticmethod
    async def find_one_by_id(todo_user_id: int):
        query = todo_user_table.select().where(todo_user_table.c.id == todo_user_id)
        row = await database.fetch_one(query)
        return TodoUserEntity(**dict(row)) if row else None

    @staticmethod
    async def find_one_by_email(email: EmailStr):
        query = """
            SELECT TU.* FROM TodoUser AS TU WHERE TU.email = :email
        """
        row = await database.fetch_one(query, {'email': email})
        return TodoUserEntity(**dict(row)) if row else None
