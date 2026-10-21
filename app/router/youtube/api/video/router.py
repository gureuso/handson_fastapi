# -*- coding: utf-8 -*-
from fastapi import APIRouter, Depends
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from app.common.response import verify_api_token
from app.database.mysql import UserEntity
from app.service.video import VideoService, VideoCommentService
from config import Config

router = APIRouter(prefix='/youtube/api/videos')
templates = Jinja2Templates(directory=Config.TEMPLATES_DIR)


class CreateCommentItem(BaseModel):
    content: str


@router.get('')
async def find_video_list(current_user: UserEntity | None = Depends(verify_api_token), video_service: VideoService = Depends()):
    return await video_service.find_video_list()


@router.get('/{video_id}')
async def find_video(video_id: int, current_user: UserEntity | None = Depends(verify_api_token), video_service: VideoService = Depends()):
    return await video_service.find_video(video_id, current_user)


@router.post('/{video_id}/like')
async def add_video_like_cnt(video_id: int, current_user: UserEntity | None = Depends(verify_api_token), video_service: VideoService = Depends()):
    return await video_service.toggle_like(video_id, current_user)


@router.post('/{video_id}/dislike')
async def add_video_dislike_cnt(video_id: int, current_user: UserEntity | None = Depends(verify_api_token), video_service: VideoService = Depends()):
    return await video_service.toggle_dislike(video_id, current_user)


@router.get('/{video_id}/comments')
async def get_comments(video_id: int, current_user: UserEntity | None = Depends(verify_api_token), video_comment_service: VideoCommentService = Depends()):
    comments = await video_comment_service.find_all(video_id, current_user)
    return {'comments': comments, 'user': {'id': current_user.id, 'nickname': current_user.nickname, 'profile_image': current_user.profile_image}}


@router.post('/{video_id}/comments')
async def add_comment(video_id: int, item: CreateCommentItem, current_user: UserEntity | None = Depends(verify_api_token), video_comment_service: VideoCommentService = Depends()):
    await video_comment_service.create(video_id, item.content, current_user)
    return {}


@router.post('/{video_id}/comments/{comment_id}')
async def add_child_comment(video_id: int, comment_id: int, item: CreateCommentItem, current_user: UserEntity | None = Depends(verify_api_token), video_comment_service: VideoCommentService = Depends()):
    await video_comment_service.create(video_id, item.content, current_user, parent_id=comment_id)
    return {}


@router.post('/{video_id}/comments/{comment_id}/like')
async def add_comment_like(video_id: int, comment_id: int, current_user: UserEntity | None = Depends(verify_api_token), video_comment_service: VideoCommentService = Depends()):
    return await video_comment_service.toggle_like(video_id, comment_id, current_user)


@router.post('/{video_id}/comments/{comment_id}/dislike')
async def add_video_dislike_cnt(video_id: int, comment_id: int, current_user: UserEntity | None = Depends(verify_api_token), video_comment_service: VideoCommentService = Depends()):
    return await video_comment_service.toggle_dislike(video_id, comment_id, current_user)


@router.post('/{video_id}/comments/{comment_id}/fix')
async def fix_comment(video_id: int, comment_id: int, current_user: UserEntity | None = Depends(verify_api_token), video_comment_service: VideoCommentService = Depends()):
    await video_comment_service.toggle_fixed(video_id, comment_id, current_user)
    return {}
