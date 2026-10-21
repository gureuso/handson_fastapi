import random
import string
import jwt
from datetime import datetime
from typing import List

from pydantic import EmailStr

from app.common.auth import sha256_encrypt
from app.common.response import BadRequestException
from app.database.mysql import TodoUserEntity, TodoEntity
from app.repository.todo import TodoRepository
from app.repository.todo_user import TodoUserRepository
from config import JsonConfig


class TodoUserService:
    def __init__(self):
        self.todo_user_repository = TodoUserRepository()

    async def signup(self, email: EmailStr, password: str):
        todo_user = await self.todo_user_repository.find_one_by_email(email)
        if todo_user:
            raise BadRequestException()

        nickname = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))
        await self.todo_user_repository.create(TodoUserEntity(
            email=email,
            password=sha256_encrypt(password),
            nickname=nickname,
            created_at=datetime.now(),
        ))

    async def signin(self, email: EmailStr, password: str) -> str:
        todo_user = await self.todo_user_repository.find_one_by_email(email)
        if not todo_user:
            raise BadRequestException()

        if todo_user.password != sha256_encrypt(password):
            raise BadRequestException()

        return jwt.encode({'id': todo_user.id}, JsonConfig.get_data('SECRET'))


class TodoService:
    def __init__(self):
        self.todo_repository = TodoRepository()

    async def create(self, user_id: int, title: str, content: str, created_at: datetime):
        await self.todo_repository.create(TodoEntity(
            user_id=user_id, title=title, content=content, completed_at=None, created_at=created_at,
        ))

    async def find_all(self, start: datetime, end: datetime) -> List[TodoEntity]:
        return await self.todo_repository.find_all(start, end)

    async def find_one_by_id(self, todo_id: int, user_id: int) -> TodoEntity:
        todo = await self.todo_repository.find_one_by_id(todo_id, user_id)
        if not todo:
            raise BadRequestException()
        return todo

    async def delete(self, todo_id: int, user_id: int):
        await self.todo_repository.delete(todo_id, user_id)

    async def complete(self, todo_id: int, user_id: int):
        await self.todo_repository.complete(todo_id, user_id)
