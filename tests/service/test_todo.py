from datetime import datetime

import jwt
import pytest

from app.common.auth import sha256_encrypt
from app.common.response import BadRequestException
from app.database.mysql import TodoUserEntity, TodoEntity
from app.service.todo import TodoUserService, TodoService
from config import JsonConfig
from tests.service.utils import mock_repositories


@pytest.fixture
def todo_user_service() -> TodoUserService:
    return mock_repositories(TodoUserService())


@pytest.fixture
def todo_service() -> TodoService:
    return mock_repositories(TodoService())


def make_todo_user(password: str = '1234') -> TodoUserEntity:
    return TodoUserEntity(
        id=7, email='todo@gmail.com', password=sha256_encrypt(password), nickname='TODOUSER', created_at=datetime.now(),
    )


@pytest.mark.asyncio
async def test_signup(todo_user_service):
    todo_user_service.todo_user_repository.find_one_by_email.return_value = None

    await todo_user_service.signup('todo@gmail.com', '1234')

    entity = todo_user_service.todo_user_repository.create.call_args.args[0]
    assert entity.email == 'todo@gmail.com'
    assert entity.password == sha256_encrypt('1234')
    assert len(entity.nickname) == 8


@pytest.mark.asyncio
async def test_signup_duplicated_email(todo_user_service):
    todo_user_service.todo_user_repository.find_one_by_email.return_value = make_todo_user()

    with pytest.raises(BadRequestException):
        await todo_user_service.signup('todo@gmail.com', '1234')
    todo_user_service.todo_user_repository.create.assert_not_awaited()


@pytest.mark.asyncio
async def test_signin(todo_user_service):
    todo_user_service.todo_user_repository.find_one_by_email.return_value = make_todo_user()

    token = await todo_user_service.signin('todo@gmail.com', '1234')

    assert jwt.decode(token, JsonConfig.get_data('SECRET'), algorithms=['HS256']) == {'id': 7}


@pytest.mark.asyncio
async def test_signin_fail(todo_user_service):
    todo_user_service.todo_user_repository.find_one_by_email.return_value = None
    with pytest.raises(BadRequestException):
        await todo_user_service.signin('none@gmail.com', '1234')

    todo_user_service.todo_user_repository.find_one_by_email.return_value = make_todo_user()
    with pytest.raises(BadRequestException):
        await todo_user_service.signin('todo@gmail.com', 'wrong')


@pytest.mark.asyncio
async def test_create(todo_service):
    created_at = datetime(2025, 5, 1, 11, 11, 11)

    await todo_service.create(7, 'title', 'content', created_at)

    entity = todo_service.todo_repository.create.call_args.args[0]
    assert (entity.user_id, entity.title, entity.content) == (7, 'title', 'content')
    assert entity.completed_at is None
    assert entity.created_at == created_at


@pytest.mark.asyncio
async def test_find_all(todo_service):
    start, end = datetime(2025, 5, 1), datetime(2025, 5, 3)
    todo_service.todo_repository.find_all.return_value = ['todo']

    assert await todo_service.find_all(start, end) == ['todo']
    todo_service.todo_repository.find_all.assert_awaited_once_with(start, end)


@pytest.mark.asyncio
async def test_find_one_by_id(todo_service):
    todo = TodoEntity(id=1, user_id=7, title='title', content='content')
    todo_service.todo_repository.find_one_by_id.return_value = todo
    assert await todo_service.find_one_by_id(1, 7) is todo

    todo_service.todo_repository.find_one_by_id.return_value = None
    with pytest.raises(BadRequestException):
        await todo_service.find_one_by_id(9999, 7)


@pytest.mark.asyncio
async def test_delete_and_complete(todo_service):
    await todo_service.delete(1, 7)
    todo_service.todo_repository.delete.assert_awaited_once_with(1, 7)

    await todo_service.complete(1, 7)
    todo_service.todo_repository.complete.assert_awaited_once_with(1, 7)
