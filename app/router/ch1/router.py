# -*- coding: utf-8 -*-
from uuid import uuid4

from fastapi import APIRouter
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from pydantic import BaseModel

from config import Config

router = APIRouter(prefix='/ch1')
templates = Jinja2Templates(directory=Config.TEMPLATES_DIR)


class PostItem(BaseModel):
    content: str


class PostEntity(BaseModel):
    id: str
    content: str


@router.get('')
async def main():
    return {'ping': 'pong'}


@router.get('/ws')
async def ws(request: Request):
    return templates.TemplateResponse('ws.html', {'request': request})


posts: list[PostEntity] = []
@router.get('/posts')
async def ch1_get(offset: int=0, limit: int=10):
    return {'posts': posts[offset:limit]}


@router.post('/posts')
async def ch1_post(item: PostItem):
    posts.append(PostEntity(id=str(uuid4()), content=item.content))
    return {}


@router.put('/posts/{post_id}')
async def ch1_put(post_id: str, item: PostItem):
    for post in posts:
        if post.id == post_id:
            post.content = item.content
    return {}


@router.patch('/posts/{post_id}')
async def ch1_patch(post_id: str, item: PostItem):
    for post in posts:
        if post.id == post_id:
            post.content = item.content
    return {}


@router.delete('/posts/{post_id}')
async def ch1_delete(post_id: str):
    del_post_idx = None
    for idx, post in enumerate(posts):
        if post.id == post_id:
            del_post_idx = idx
            break
    posts.pop(del_post_idx)
    return {}
