# -*- coding: utf-8 -*-
import json
from typing import List
from datetime import datetime
from fastapi import APIRouter, BackgroundTasks, Depends
from fastapi.templating import Jinja2Templates

from app.common.response import verify_api_token
from app.database.cache import Cache
from app.database.mysql import ShortsEntity, UserEntity, ShortsLikeEnum, ShortsLikeEntity
from app.service.shorts import ShortsService
from app.service.shorts_like import ShortsLikeService
from config import Config

router = APIRouter(prefix='/youtube/api/shorts')
templates = Jinja2Templates(directory=Config.TEMPLATES_DIR)


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
        'liked': liked, 'disliked': disliked, 'comment_cnt': 0,
    }


@router.post('/{shorts_id}/like')
async def add_shorts_like_cnt(shorts_id: int, current_user: UserEntity | None = Depends(verify_api_token)):
    await ShortsLikeService.create(
        ShortsLikeEntity(
            kind=ShortsLikeEnum.LIKE, shorts_id=shorts_id, user_id=current_user.id,
            created_at=datetime.now()
        )
    )
    await ShortsService.update_like_cnt(shorts_id)
    return await ShortsLikeService.find_one_by_liked(shorts_id, current_user.id)


@router.post('/{shorts_id}/dislike')
async def add_shorts_dislike_cnt(shorts_id: int, current_user: UserEntity | None = Depends(verify_api_token)):
    await ShortsLikeService.create(
        ShortsLikeEntity(
            kind=ShortsLikeEnum.DISLIKE, shorts_id=shorts_id, user_id=current_user.id,
            created_at=datetime.now()
        )
    )
    await ShortsService.update_dislike_cnt(shorts_id)
    return await ShortsLikeService.find_one_by_disliked(shorts_id, current_user.id)
