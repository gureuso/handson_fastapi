# -*- coding: utf-8 -*-
from uuid import uuid4

from fastapi import APIRouter
from fastapi.templating import Jinja2Templates

from config import Config

router = APIRouter(prefix='/ch1')
templates = Jinja2Templates(directory=Config.TEMPLATES_DIR)


@router.get('')
async def main():
    return {'ping': 'pong'}


posts = []
@router.get('/posts')
async def ch1_get():
    return {'posts': posts}


@router.post('/posts')
async def ch1_post():
    posts.append({'id': str(uuid4()), 'content': 'content'})
    return {}


@router.put('/posts/{post_id}')
async def ch1_put(post_id: str):
    for post in posts:
        if post['id'] == post_id:
            post['content'] = 'put content'
    return {}


@router.patch('/posts/{post_id}')
async def ch1_patch(post_id: str):
    for post in posts:
        if post['id'] == post_id:
            post['content'] = 'patch content'
    return {}


@router.delete('/posts/{post_id}')
async def ch1_delete(post_id: str):
    del_post_idx = None
    for idx, post in enumerate(posts):
        if post['id'] == post_id:
            del_post_idx = idx
            break
    posts.pop(del_post_idx)
    return {}
