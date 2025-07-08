# -*- coding: utf-8 -*-
import json
from datetime import datetime
from fastapi import APIRouter, Depends
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from app.common.response import verify_api_token, NotFoundException, BadRequestException, PermissionDeniedException
from app.database.cache import Cache
from app.database.mysql import UserEntity, VideoLikeEnum, VideoLikeEntity, VideoCommentEntity, VideoCommentLikeEnum, \
    VideoCommentLikeEntity
from app.service.channel import ChannelService
from app.service.channel_subscription import ChannelSubscriptionService
from app.service.shorts import ShortsService
from app.service.tag import TagService
from app.service.user import UserService
from app.service.video import VideoService
from app.service.video_comment import VideoCommentService
from app.service.video_comment_like import VideoCommentLikeService
from app.service.video_like import VideoLikeService
from config import Config

router = APIRouter(prefix='/youtube/api/videos')
templates = Jinja2Templates(directory=Config.TEMPLATES_DIR)


class CreateCommentItem(BaseModel):
    content: str


@router.get('')
async def find_video_list(current_user: UserEntity | None = Depends(verify_api_token)):
    tags = await TagService.find_unique_tag()
    videos = await VideoService.find_all()
    shorts = await ShortsService.find_all()
    return {'tags': tags, 'videos': videos, 'shorts': shorts}


@router.get('/{video_id}')
async def find_video(video_id: int, current_user: UserEntity | None = Depends(verify_api_token)):
    video = await VideoService.find_one_by_id(video_id)
    if not video:
        raise NotFoundException()

    channel = await ChannelService.find_one_by_id(video.channel_id)
    if not channel:
        raise NotFoundException()

    liked: dict = await VideoLikeService.find_one_by_liked(video_id, current_user.id)
    disliked: dict = await VideoLikeService.find_one_by_disliked(video_id, current_user.id)

    messages = await Cache.lrange(f'fastapi_room_{video_id}', 0, 100)
    messages.reverse()
    for idx, message in enumerate(messages):
        messages[idx] = json.loads(message)

    sub = await ChannelSubscriptionService.find_one_by_id(channel.id, current_user.id)
    video_user = await UserService.find_one_by_id(video.user_id)

    return {
        'video': video, 'channel': channel, 'liked': liked, 'disliked': disliked, 'messages': messages,
        'subscription': True if sub else False, 'video_user': video_user,
    }


@router.post('/{video_id}/like')
async def add_video_like_cnt(video_id: int, current_user: UserEntity | None = Depends(verify_api_token)):
    dislike = await VideoLikeService.find_one_by_disliked(video_id, current_user.id)
    if dislike['disliked'] is True:
        await VideoLikeService.delete_by_user_id(video_id, current_user.id, VideoLikeEnum.DISLIKE)
        await VideoService.update_dislike_cnt(video_id, disliked=True)
        dislike['disliked'] = False
        dislike['cnt'] -= 1

    like = await VideoLikeService.find_one_by_liked(video_id, current_user.id)
    if like['liked'] is True:
        await VideoLikeService.delete_by_user_id(video_id, current_user.id, VideoLikeEnum.LIKE)
        await VideoService.update_like_cnt(video_id, liked=True)
        like['liked'] = False
        like['cnt'] -= 1
    else:
        await VideoLikeService.create(
            VideoLikeEntity(
                kind=VideoLikeEnum.LIKE, video_id=video_id, user_id=current_user.id,
                created_at=datetime.now()
            )
        )
        await VideoService.update_like_cnt(video_id, liked=False)
        like['liked'] = True
        like['cnt'] += 1
    return {'like': like, 'dislike': dislike}


@router.post('/{video_id}/dislike')
async def add_video_dislike_cnt(video_id: int, current_user: UserEntity | None = Depends(verify_api_token)):
    like = await VideoLikeService.find_one_by_liked(video_id, current_user.id)
    if like['liked'] is True:
        await VideoLikeService.delete_by_user_id(video_id, current_user.id, VideoLikeEnum.LIKE)
        await VideoService.update_like_cnt(video_id, liked=True)
        like['liked'] = False
        like['cnt'] -= 1

    dislike = await VideoLikeService.find_one_by_disliked(video_id, current_user.id)
    if dislike['disliked'] is True:
        await VideoLikeService.delete_by_user_id(video_id, current_user.id, VideoLikeEnum.DISLIKE)
        await VideoService.update_dislike_cnt(video_id, disliked=True)
        dislike['disliked'] = False
        dislike['cnt'] -= 1
    else:
        await VideoLikeService.create(
            VideoLikeEntity(
                kind=VideoLikeEnum.DISLIKE, video_id=video_id, user_id=current_user.id,
                created_at=datetime.now()
            )
        )
        await VideoService.update_dislike_cnt(video_id, disliked=False)
        dislike['disliked'] = True
        dislike['cnt'] += 1
    return {'like': like, 'dislike': dislike}


@router.get('/{video_id}/comments')
async def get_comments(video_id: int, current_user: UserEntity | None = Depends(verify_api_token)):
    comments = await VideoCommentService.find_all(video_id)
    for comment in comments:
        comment.child_comments = await VideoCommentService.find_all_by_parent_id(video_id, comment.id)
        for child_comment in comment.child_comments:
            child_comment.liked = (await VideoCommentLikeService.find_one_by_liked(child_comment.id, current_user.id))['liked']
            child_comment.disliked = (await VideoCommentLikeService.find_one_by_disliked(child_comment.id, current_user.id))['disliked']

        comment.liked = (await VideoCommentLikeService.find_one_by_liked(comment.id, current_user.id))['liked']
        comment.disliked = (await VideoCommentLikeService.find_one_by_disliked(comment.id, current_user.id))['disliked']

    return {'comments': comments, 'user': {'id': current_user.id, 'nickname': current_user.nickname, 'profile_image': current_user.profile_image}}


@router.post('/{video_id}/comments')
async def add_comment(video_id: int, item: CreateCommentItem, current_user: UserEntity | None = Depends(verify_api_token)):
    await VideoCommentService.create(
        VideoCommentEntity(
            content=item.content, video_id=video_id, user_id=current_user.id, created_at=datetime.now(),
            parent_id=None,
        )
    )
    return {}


@router.post('/{video_id}/comments/{comment_id}')
async def add_child_comment(video_id: int, comment_id: int, item: CreateCommentItem, current_user: UserEntity | None = Depends(verify_api_token)):
    await VideoCommentService.create(
        VideoCommentEntity(
            content=item.content, video_id=video_id, user_id=current_user.id, created_at=datetime.now(),
            parent_id=comment_id,
        )
    )
    return {}


@router.post('/{video_id}/comments/{comment_id}/like')
async def add_comment_like(video_id: int, comment_id: int, current_user: UserEntity | None = Depends(verify_api_token)):
    dislike = await VideoCommentLikeService.find_one_by_disliked(comment_id, current_user.id)
    if dislike['disliked'] is True:
        await VideoCommentLikeService.delete_by_user_id(comment_id, current_user.id, VideoCommentLikeEnum.DISLIKE)
        await VideoCommentService.update_dislike_cnt(comment_id, disliked=True)
        dislike['disliked'] = False
        dislike['cnt'] -= 1

    like = await VideoCommentLikeService.find_one_by_liked(comment_id, current_user.id)
    if like['liked'] is True:
        await VideoCommentLikeService.delete_by_user_id(comment_id, current_user.id, VideoCommentLikeEnum.LIKE)
        await VideoCommentService.update_like_cnt(comment_id, liked=True)
        like['liked'] = False
        like['cnt'] -= 1
    else:
        await VideoCommentLikeService.create(
            VideoCommentLikeEntity(
                kind=VideoCommentLikeEnum.LIKE, video_id=video_id, user_id=current_user.id,
                created_at=datetime.now(), comment_id=comment_id,
            )
        )
        await VideoCommentService.update_like_cnt(comment_id, liked=False)
        like['liked'] = True
        like['cnt'] += 1
    return {'like': like, 'dislike': dislike}


@router.post('/{video_id}/comments/{comment_id}/dislike')
async def add_video_dislike_cnt(video_id: int, comment_id: int, current_user: UserEntity | None = Depends(verify_api_token)):
    like = await VideoCommentLikeService.find_one_by_liked(comment_id, current_user.id)
    if like['liked'] is True:
        await VideoCommentLikeService.delete_by_user_id(comment_id, current_user.id, VideoCommentLikeEnum.LIKE)
        await VideoCommentService.update_like_cnt(comment_id, liked=True)
        like['liked'] = False
        like['cnt'] -= 1

    dislike = await VideoCommentLikeService.find_one_by_disliked(comment_id, current_user.id)
    if dislike['disliked'] is True:
        await VideoCommentLikeService.delete_by_user_id(comment_id, current_user.id, VideoCommentLikeEnum.DISLIKE)
        await VideoCommentService.update_dislike_cnt(comment_id, disliked=True)
        dislike['disliked'] = False
        dislike['cnt'] -= 1
    else:
        await VideoCommentLikeService.create(
            VideoCommentLikeEntity(
                kind=VideoCommentLikeEnum.DISLIKE, video_id=video_id, user_id=current_user.id,
                created_at=datetime.now(), comment_id=comment_id,
            )
        )
        await VideoCommentService.update_dislike_cnt(comment_id, disliked=False)
        dislike['disliked'] = True
        dislike['cnt'] += 1
    return {'like': like, 'dislike': dislike}


@router.post('/{video_id}/comments/{comment_id}/fix')
async def fix_comment(video_id: int, comment_id: int, current_user: UserEntity | None = Depends(verify_api_token)):
    comment = await VideoCommentService.find_one_by_id(comment_id)
    if not comment:
        raise BadRequestException()
    video = await VideoCommentService.find_one_by_id(video_id)
    if not video:
        raise BadRequestException()

    if video.user_id != current_user.id:
        raise PermissionDeniedException()

    is_fixed = False if comment.is_fixed else True
    await VideoCommentService.update_is_fixed(comment_id, is_fixed)
    return {}
