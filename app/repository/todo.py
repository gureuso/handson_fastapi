from datetime import datetime
from typing import List

from app.database.mysql import database, TodoEntity, todo_table


class TodoRepository:
    async def create(self, todo_entity: TodoEntity) -> TodoEntity:
        query = todo_table.insert().values(
            user_id=todo_entity.user_id, title=todo_entity.title, content=todo_entity.content,
            completed_at=todo_entity.completed_at, created_at=todo_entity.created_at
        )
        ai = await database.execute(query)
        todo_entity.id = ai
        return todo_entity

    async def find_one_by_id(self, todo_id: int, user_id: int):
        query = todo_table.select().where(todo_table.c.id == todo_id).where(todo_table.c.user_id == user_id)
        row = await database.fetch_one(query)
        return TodoEntity(**dict(row)) if row else None

    async def find_all(self, start: datetime, end: datetime) -> List[TodoEntity]:
        query = """
            SELECT T.* FROM Todo AS T WHERE T.created_at >= :start AND T.created_at <= :end;
        """
        rows = await database.fetch_all(query, {'start': start, 'end': end})
        return [TodoEntity(**dict(row)) for row in rows]

    async def complete(self, todo_id: int, user_id: int):
        query = """
            UPDATE Todo SET completed_at = :now WHERE id = :todo_id AND user_id = :user_id;
        """
        await database.execute(query, {'todo_id': todo_id, 'user_id': user_id, 'now': datetime.now()})
        return {}

    async def delete(self, todo_id: int, user_id: int):
        query = """
            DELETE FROM Todo WHERE id = :todo_id AND user_id = :user_id;
        """
        await database.execute(query, {'todo_id': todo_id, 'user_id': user_id})
        return {}
