# -*- coding: utf-8 -*-
from fastapi import APIRouter, Depends
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from app.common.response import verify_api_token
from app.database.mysql import UserEntity
from app.service.shorts import ShortsService, ShortsCommentService
from config import Config

router = APIRouter(prefix='/youtube/api/shorts')
templates = Jinja2Templates(directory=Config.TEMPLATES_DIR)


class CreateCommentItem(BaseModel):
    content: str


@router.get('/{shorts_id}')
async def get_shorts(shorts_id: int, current_user: UserEntity = Depends(verify_api_token), shorts_service: ShortsService = Depends()):
    return await shorts_service.find_shorts(shorts_id, current_user)


@router.post('/{shorts_id}/like')
async def add_shorts_like_cnt(shorts_id: int, current_user: UserEntity = Depends(verify_api_token), shorts_service: ShortsService = Depends()):
    return await shorts_service.toggle_like(shorts_id, current_user)


@router.post('/{shorts_id}/dislike')
async def add_shorts_dislike_cnt(shorts_id: int, current_user: UserEntity = Depends(verify_api_token), shorts_service: ShortsService = Depends()):
    return await shorts_service.toggle_dislike(shorts_id, current_user)


@router.get('/{shorts_id}/comments')
async def get_comments(shorts_id: int, current_user: UserEntity = Depends(verify_api_token), shorts_comment_service: ShortsCommentService = Depends()):
    return {'comments': await shorts_comment_service.find_all(shorts_id, current_user)}


@router.post('/{shorts_id}/comments')
async def add_comment(shorts_id: int, item: CreateCommentItem, current_user: UserEntity = Depends(verify_api_token), shorts_comment_service: ShortsCommentService = Depends()):
    await shorts_comment_service.create(shorts_id, item.content, current_user)
    return {}


@router.post('/{shorts_id}/comments/{comment_id}')
async def add_child_comment(shorts_id: int, comment_id: int, item: CreateCommentItem, current_user: UserEntity = Depends(verify_api_token), shorts_comment_service: ShortsCommentService = Depends()):
    await shorts_comment_service.create(shorts_id, item.content, current_user, parent_id=comment_id)
    return {}


@router.post('/{shorts_id}/comments/{comment_id}/like')
async def add_comment_like(shorts_id: int, comment_id: int, current_user: UserEntity = Depends(verify_api_token), shorts_comment_service: ShortsCommentService = Depends()):
    return await shorts_comment_service.toggle_like(shorts_id, comment_id, current_user)


@router.post('/{shorts_id}/comments/{comment_id}/dislike')
async def add_shorts_dislike_cnt(shorts_id: int, comment_id: int, current_user: UserEntity = Depends(verify_api_token), shorts_comment_service: ShortsCommentService = Depends()):
    return await shorts_comment_service.toggle_dislike(shorts_id, comment_id, current_user)
