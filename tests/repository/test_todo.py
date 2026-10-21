import random
from datetime import datetime

import pytest

from app.database.mysql import TodoUserEntity, TodoEntity
from app.repository.todo import TodoRepository
from app.repository.todo_user import TodoUserRepository
from tests.repository.utils import random_name


@pytest.mark.asyncio
async def test_todo_user(cleanup):
    repository = TodoUserRepository()
    email = f'{random_name()}@test.com'

    todo_user = await repository.create(TodoUserEntity(
        email=email, password='hashed', nickname=random_name(), created_at=datetime.now(),
    ))
    cleanup.add('TodoUser', todo_user.id)
    assert todo_user.id is not None

    assert (await repository.find_one_by_id(todo_user.id)).email == email
    assert (await repository.find_one_by_email(email)).id == todo_user.id
    assert await repository.find_one_by_email(f'{random_name()}@test.com') is None


@pytest.mark.asyncio
async def test_todo(cleanup):
    repository = TodoRepository()
    # 실제 사용자와 겹치지 않는 user_id
    user_id = random.randint(2_000_000_000, 2_100_000_000)
    # 다른 데이터와 겹치지 않는 날짜 범위를 사용
    created_at = datetime(2001, 1, 1, 0, 0, 0)

    todo = await repository.create(TodoEntity(
        user_id=user_id, title='title', content='content', completed_at=None, created_at=created_at,
    ))
    cleanup.add('Todo', todo.id)

    found = await repository.find_one_by_id(todo.id, user_id)
    assert (found.title, found.content, found.completed_at) == ('title', 'content', None)
    assert await repository.find_one_by_id(todo.id, user_id + 1) is None

    todos = await repository.find_all(datetime(2001, 1, 1), datetime(2001, 1, 2))
    assert todo.id in [x.id for x in todos]

    await repository.complete(todo.id, user_id)
    assert (await repository.find_one_by_id(todo.id, user_id)).completed_at is not None

    await repository.delete(todo.id, user_id + 1)
    assert await repository.find_one_by_id(todo.id, user_id) is not None

    await repository.delete(todo.id, user_id)
    assert await repository.find_one_by_id(todo.id, user_id) is None
