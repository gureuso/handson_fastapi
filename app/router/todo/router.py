# -*- coding: utf-8 -*-
import random
import string
import jwt
from datetime import datetime
from fastapi import APIRouter, Depends
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, EmailStr

from app.common.auth import sha256_encrypt
from app.common.response import BadRequestException, verify_todo_api_token
from app.database.mysql import TodoUserEntity, UserEntity, TodoEntity
from app.service.todo import TodoService
from app.service.todo_user import TodoUserService
from config import Config, JsonConfig

router = APIRouter(prefix='/todo')
templates = Jinja2Templates(directory=Config.TEMPLATES_DIR)


class TodoItem(BaseModel):
    title: str
    content: str
    created_at: datetime


class TodoUserItem(BaseModel):
    email: EmailStr
    password: str


class TodoResponse(BaseModel):
    todo: TodoEntity


@router.post('/users/signup', tags=['todo'])
async def signup_todo_user(item: TodoUserItem):
    todo_user = await TodoUserService.find_one_by_email(item.email)
    if todo_user:
        raise BadRequestException()

    nickname = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))
    await TodoUserService.create(TodoUserEntity(
        email=item.email,
        password=sha256_encrypt(item.password),
        nickname=nickname,
        created_at=datetime.now(),
    ))
    return {}


@router.post('/users/signin', tags=['todo'])
async def signin_todo_user(item: TodoUserItem):
    todo_user = await TodoUserService.find_one_by_email(item.email)
    if not todo_user:
        raise BadRequestException()

    if todo_user.password != sha256_encrypt(item.password):
        raise BadRequestException()

    x_access_token = jwt.encode({'id': todo_user.id}, JsonConfig.get_data('SECRET'))
    return {'x_access_token': x_access_token}


@router.post('', tags=['todo'])
async def add_todo(item: TodoItem, current_user: UserEntity | None = Depends(verify_todo_api_token)):
    await TodoService.create(TodoEntity(
        user_id=current_user.id, title=item.title, content=item.content, completed_at=None, created_at=item.created_at,
    ))
    return {}


@router.get('', tags=['todo'])
async def get_todo_list(start: datetime, end: datetime, current_user: UserEntity | None = Depends(verify_todo_api_token)):
    todos = await TodoService.find_all(start, end)
    return {'todos': todos}


@router.get('/{todo_id}', tags=['todo'], response_model=TodoResponse)
async def get_todo(todo_id: int, current_user: UserEntity | None = Depends(verify_todo_api_token)):
    todo = await TodoService.find_one_by_id(todo_id, current_user.id)
    if not todo:
        raise BadRequestException()

    return {'todo': todo}


@router.delete('/{todo_id}', tags=['todo'])
async def delete_todo(todo_id: int, current_user: UserEntity | None = Depends(verify_todo_api_token)):
    await TodoService.delete(todo_id, current_user.id)
    return {}


@router.patch('/{todo_id}/complete', tags=['todo'])
async def complete(todo_id: int, current_user: UserEntity | None = Depends(verify_todo_api_token)):
    await TodoService.complete(todo_id, current_user.id)
    return {}
