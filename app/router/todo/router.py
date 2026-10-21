# -*- coding: utf-8 -*-
from datetime import datetime
from fastapi import APIRouter, Depends
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, EmailStr

from app.common.response import verify_todo_api_token
from app.database.mysql import UserEntity, TodoEntity
from app.service.todo import TodoService, TodoUserService
from config import Config

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
async def signup_todo_user(item: TodoUserItem, todo_user_service: TodoUserService = Depends()):
    await todo_user_service.signup(item.email, item.password)
    return {}


@router.post('/users/signin', tags=['todo'])
async def signin_todo_user(item: TodoUserItem, todo_user_service: TodoUserService = Depends()):
    x_access_token = await todo_user_service.signin(item.email, item.password)
    return {'x_access_token': x_access_token}


@router.post('', tags=['todo'])
async def add_todo(item: TodoItem, current_user: UserEntity | None = Depends(verify_todo_api_token), todo_service: TodoService = Depends()):
    await todo_service.create(current_user.id, item.title, item.content, item.created_at)
    return {}


@router.get('', tags=['todo'])
async def get_todo_list(start: datetime, end: datetime, current_user: UserEntity | None = Depends(verify_todo_api_token), todo_service: TodoService = Depends()):
    todos = await todo_service.find_all(start, end)
    return {'todos': todos}


@router.get('/{todo_id}', tags=['todo'], response_model=TodoResponse)
async def get_todo(todo_id: int, current_user: UserEntity | None = Depends(verify_todo_api_token), todo_service: TodoService = Depends()):
    todo = await todo_service.find_one_by_id(todo_id, current_user.id)
    return {'todo': todo}


@router.delete('/{todo_id}', tags=['todo'])
async def delete_todo(todo_id: int, current_user: UserEntity | None = Depends(verify_todo_api_token), todo_service: TodoService = Depends()):
    await todo_service.delete(todo_id, current_user.id)
    return {}


@router.patch('/{todo_id}/complete', tags=['todo'])
async def complete(todo_id: int, current_user: UserEntity | None = Depends(verify_todo_api_token), todo_service: TodoService = Depends()):
    await todo_service.complete(todo_id, current_user.id)
    return {}
