# -*- coding: utf-8 -*-
import json
from typing import List
from datetime import datetime
from fastapi import APIRouter, Depends
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from app.common.response import verify_api_token
from app.database.cache import Cache
from app.database.mysql import ShortsEntity, UserEntity, ShortsLikeEnum, ShortsLikeEntity, ShortsCommentEntity, \
    ShortsCommentLikeEntity, ShortsCommentLikeEnum
from app.service.shorts import ShortsService
from app.service.shorts_comment import ShortsCommentService
from app.service.shorts_comment_like import ShortsCommentLikeService
from app.service.shorts_like import ShortsLikeService
from config import Config

router = APIRouter(prefix='/youtube/api/shorts')
templates = Jinja2Templates(directory=Config.TEMPLATES_DIR)


class CreateComment(BaseModel):
    content: str


@router.get('/{shorts_id}')
async def get_shorts(shorts_id: int, current_user: UserEntity | None = Depends(verify_api_token)):
    def custom_serializer(obj):
        if isinstance(obj, datetime):
            return datetime.strftime(obj, '%Y-%m-%d %H:%M:%S')
        elif hasattr(obj, '__dict__'):
            return obj.__dict__
        else:
            raise TypeError(f'Type {type(obj)} not serializable')
    
    shorts_list_json = await Cache.get('fastapi_get_shorts_list')
    if shorts_list_json:
        shorts_list: List[ShortsEntity] = []
        for shorts in json.loads(shorts_list_json):
            shorts_entity = ShortsEntity(
                id=shorts['id'],
                channel_id=shorts['channel_id'],
                tag=shorts['tag'],
                title=shorts['title'],
                thumbnail=shorts['thumbnail'],
                content=shorts['content'],
                view_cnt=shorts['view_cnt'],
                like_cnt=shorts['like_cnt'],
                dislike_cnt=shorts['dislike_cnt'],
                created_at=datetime.strptime(shorts['created_at'], '%Y-%m-%d %H:%M:%S'),
            )
            shorts_list.append(shorts_entity)
    else:
        shorts_list: List[ShortsEntity] = await ShortsService.find_all_with_random()
        await Cache.setex('fastapi_get_shorts_list', 60, json.dumps([x.dict() for x in shorts_list], default=custom_serializer))

    current_shorts = {}
    next_shorts = {}
    for idx, shorts in enumerate(shorts_list):
        if shorts.id == shorts_id:
            current_shorts = shorts
            next_shorts = shorts_list[0] if len(shorts_list) == idx + 1 else shorts_list[idx + 1]

    liked: dict = await ShortsLikeService.find_one_by_liked(current_shorts.id, current_user.id)
    disliked: dict = await ShortsLikeService.find_one_by_disliked(current_shorts.id, current_user.id)
    return {
        'current_shorts': current_shorts, 'next_shorts': next_shorts,
        'liked': liked, 'disliked': disliked,
    }


@router.post('/{shorts_id}/like')
async def add_shorts_like_cnt(shorts_id: int, current_user: UserEntity | None = Depends(verify_api_token)):
    dislike = await ShortsLikeService.find_one_by_disliked(shorts_id, current_user.id)
    if dislike['disliked'] is True:
        await ShortsLikeService.delete_by_user_id(shorts_id, current_user.id, ShortsLikeEnum.DISLIKE)
        await ShortsService.update_dislike_cnt(shorts_id, disliked=True)
        dislike['disliked'] = False
        dislike['cnt'] -= 1

    like = await ShortsLikeService.find_one_by_liked(shorts_id, current_user.id)
    if like['liked'] is True:
        await ShortsLikeService.delete_by_user_id(shorts_id, current_user.id, ShortsLikeEnum.LIKE)
        await ShortsService.update_like_cnt(shorts_id, liked=True)
        like['liked'] = False
        like['cnt'] -= 1
    else:
        await ShortsLikeService.create(
            ShortsLikeEntity(
                kind=ShortsLikeEnum.LIKE, shorts_id=shorts_id, user_id=current_user.id,
                created_at=datetime.now()
            )
        )
        await ShortsService.update_like_cnt(shorts_id, liked=False)
        like['liked'] = True
        like['cnt'] += 1
    return {'like': like, 'dislike': dislike}


@router.post('/{shorts_id}/dislike')
async def add_shorts_dislike_cnt(shorts_id: int, current_user: UserEntity | None = Depends(verify_api_token)):
    like = await ShortsLikeService.find_one_by_liked(shorts_id, current_user.id)
    if like['liked'] is True:
        await ShortsLikeService.delete_by_user_id(shorts_id, current_user.id, ShortsLikeEnum.LIKE)
        await ShortsService.update_like_cnt(shorts_id, liked=True)
        like['liked'] = False
        like['cnt'] -= 1

    dislike = await ShortsLikeService.find_one_by_disliked(shorts_id, current_user.id)
    if dislike['disliked'] is True:
        await ShortsLikeService.delete_by_user_id(shorts_id, current_user.id, ShortsLikeEnum.DISLIKE)
        await ShortsService.update_dislike_cnt(shorts_id, disliked=True)
        dislike['disliked'] = False
        dislike['cnt'] -= 1
    else:
        await ShortsLikeService.create(
            ShortsLikeEntity(
                kind=ShortsLikeEnum.DISLIKE, shorts_id=shorts_id, user_id=current_user.id,
                created_at=datetime.now()
            )
        )
        await ShortsService.update_dislike_cnt(shorts_id, disliked=False)
        dislike['disliked'] = True
        dislike['cnt'] += 1
    return {'like': like, 'dislike': dislike}


@router.get('/{shorts_id}/comments')
async def get_comments(shorts_id: int, current_user: UserEntity | None = Depends(verify_api_token)):
    comments = await ShortsCommentService.find_all(shorts_id)
    for comment in comments:
        comment.child_comments = await ShortsCommentService.find_all_by_parent_id(shorts_id, comment.id)
        for child_comment in comment.child_comments:
            child_comment.liked = (await ShortsCommentLikeService.find_one_by_liked(child_comment.id, child_comment.user_id))['liked']
            child_comment.disliked = (await ShortsCommentLikeService.find_one_by_disliked(child_comment.id, child_comment.user_id))['disliked']

        comment.liked = (await ShortsCommentLikeService.find_one_by_liked(comment.id, comment.user_id))['liked']
        comment.disliked = (await ShortsCommentLikeService.find_one_by_disliked(comment.id, comment.user_id))['disliked']

    return {'comments': comments}


@router.post('/{shorts_id}/comments')
async def add_comment(shorts_id: int, item: CreateComment, current_user: UserEntity | None = Depends(verify_api_token)):
    await ShortsCommentService.create(
        ShortsCommentEntity(
            content=item.content, shorts_id=shorts_id, user_id=current_user.id, created_at=datetime.now(),
            parent_id=None,
        )
    )
    return {}


@router.post('/{shorts_id}/comments/{comment_id}')
async def add_child_comment(shorts_id: int, comment_id: int, item: CreateComment, current_user: UserEntity | None = Depends(verify_api_token)):
    await ShortsCommentService.create(
        ShortsCommentEntity(
            content=item.content, shorts_id=shorts_id, user_id=current_user.id, created_at=datetime.now(),
            parent_id=comment_id,
        )
    )
    return {}


@router.post('/{shorts_id}/comments/{comment_id}/like')
async def add_comment_like(shorts_id: int, comment_id: int, current_user: UserEntity | None = Depends(verify_api_token)):
    dislike = await ShortsCommentLikeService.find_one_by_disliked(comment_id, current_user.id)
    if dislike['disliked'] is True:
        await ShortsCommentLikeService.delete_by_user_id(comment_id, current_user.id, ShortsCommentLikeEnum.DISLIKE)
        await ShortsCommentService.update_dislike_cnt(comment_id, disliked=True)
        dislike['disliked'] = False
        dislike['cnt'] -= 1

    like = await ShortsCommentLikeService.find_one_by_liked(comment_id, current_user.id)
    if like['liked'] is True:
        await ShortsCommentLikeService.delete_by_user_id(comment_id, current_user.id, ShortsCommentLikeEnum.LIKE)
        await ShortsCommentService.update_like_cnt(comment_id, liked=True)
        like['liked'] = False
        like['cnt'] -= 1
    else:
        await ShortsCommentLikeService.create(
            ShortsCommentLikeEntity(
                kind=ShortsCommentLikeEnum.LIKE, shorts_id=shorts_id, user_id=current_user.id,
                created_at=datetime.now(), comment_id=comment_id,
            )
        )
        await ShortsCommentService.update_like_cnt(comment_id, liked=False)
        like['liked'] = True
        like['cnt'] += 1
    return {'like': like, 'dislike': dislike}


@router.post('/{shorts_id}/comments/{comment_id}/dislike')
async def add_shorts_dislike_cnt(shorts_id: int, comment_id: int, current_user: UserEntity | None = Depends(verify_api_token)):
    like = await ShortsCommentLikeService.find_one_by_liked(comment_id, current_user.id)
    if like['liked'] is True:
        await ShortsCommentLikeService.delete_by_user_id(comment_id, current_user.id, ShortsCommentLikeEnum.LIKE)
        await ShortsCommentService.update_like_cnt(comment_id, liked=True)
        like['liked'] = False
        like['cnt'] -= 1

    dislike = await ShortsCommentLikeService.find_one_by_disliked(comment_id, current_user.id)
    if dislike['disliked'] is True:
        await ShortsCommentLikeService.delete_by_user_id(comment_id, current_user.id, ShortsCommentLikeEnum.DISLIKE)
        await ShortsCommentService.update_dislike_cnt(comment_id, disliked=True)
        dislike['disliked'] = False
        dislike['cnt'] -= 1
    else:
        await ShortsCommentLikeService.create(
            ShortsCommentLikeEntity(
                kind=ShortsCommentLikeEnum.DISLIKE, shorts_id=shorts_id, user_id=current_user.id,
                created_at=datetime.now(), comment_id=comment_id,
            )
        )
        await ShortsCommentService.update_dislike_cnt(comment_id, disliked=False)
        dislike['disliked'] = True
        dislike['cnt'] += 1
    return {'like': like, 'dislike': dislike}
