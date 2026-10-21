import json
from typing import List
from datetime import datetime

from app.database.cache import Cache
from app.database.mysql import ShortsEntity, UserEntity, ShortsLikeEnum, ShortsLikeEntity, ShortsCommentEntity, \
    ShortsCommentLikeEntity, ShortsCommentLikeEnum
from app.repository.shorts import ShortsRepository
from app.repository.shorts_comment import ShortsCommentRepository
from app.repository.shorts_comment_like import ShortsCommentLikeRepository
from app.repository.shorts_like import ShortsLikeRepository


class ShortsService:
    def __init__(self):
        self.shorts_repository = ShortsRepository()
        self.shorts_like_repository = ShortsLikeRepository()

    async def find_shorts_list(self) -> List[ShortsEntity]:
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
            shorts_list: List[ShortsEntity] = await self.shorts_repository.find_all_with_random()
            await Cache.setex('fastapi_get_shorts_list', 60, json.dumps([x.dict() for x in shorts_list], default=custom_serializer))
        return shorts_list

    async def find_shorts(self, shorts_id: int, user: UserEntity) -> dict:
        shorts_list = await self.find_shorts_list()

        current_shorts = {}
        next_shorts = {}
        for idx, shorts in enumerate(shorts_list):
            if shorts.id == shorts_id:
                current_shorts = shorts
                next_shorts = shorts_list[0] if len(shorts_list) == idx + 1 else shorts_list[idx + 1]

        liked: dict = await self.shorts_like_repository.find_one_by_liked(current_shorts.id, user.id)
        disliked: dict = await self.shorts_like_repository.find_one_by_disliked(current_shorts.id, user.id)
        return {
            'current_shorts': current_shorts, 'next_shorts': next_shorts,
            'liked': liked, 'disliked': disliked,
        }

    async def toggle_like(self, shorts_id: int, user: UserEntity) -> dict:
        dislike = await self.shorts_like_repository.find_one_by_disliked(shorts_id, user.id)
        if dislike['disliked'] is True:
            await self.shorts_like_repository.delete_by_user_id(shorts_id, user.id, ShortsLikeEnum.DISLIKE)
            await self.shorts_repository.update_dislike_cnt(shorts_id, disliked=True)
            dislike['disliked'] = False
            dislike['cnt'] -= 1

        like = await self.shorts_like_repository.find_one_by_liked(shorts_id, user.id)
        if like['liked'] is True:
            await self.shorts_like_repository.delete_by_user_id(shorts_id, user.id, ShortsLikeEnum.LIKE)
            await self.shorts_repository.update_like_cnt(shorts_id, liked=True)
            like['liked'] = False
            like['cnt'] -= 1
        else:
            await self.shorts_like_repository.create(
                ShortsLikeEntity(
                    kind=ShortsLikeEnum.LIKE, shorts_id=shorts_id, user_id=user.id,
                    created_at=datetime.now()
                )
            )
            await self.shorts_repository.update_like_cnt(shorts_id, liked=False)
            like['liked'] = True
            like['cnt'] += 1
        return {'like': like, 'dislike': dislike}

    async def toggle_dislike(self, shorts_id: int, user: UserEntity) -> dict:
        like = await self.shorts_like_repository.find_one_by_liked(shorts_id, user.id)
        if like['liked'] is True:
            await self.shorts_like_repository.delete_by_user_id(shorts_id, user.id, ShortsLikeEnum.LIKE)
            await self.shorts_repository.update_like_cnt(shorts_id, liked=True)
            like['liked'] = False
            like['cnt'] -= 1

        dislike = await self.shorts_like_repository.find_one_by_disliked(shorts_id, user.id)
        if dislike['disliked'] is True:
            await self.shorts_like_repository.delete_by_user_id(shorts_id, user.id, ShortsLikeEnum.DISLIKE)
            await self.shorts_repository.update_dislike_cnt(shorts_id, disliked=True)
            dislike['disliked'] = False
            dislike['cnt'] -= 1
        else:
            await self.shorts_like_repository.create(
                ShortsLikeEntity(
                    kind=ShortsLikeEnum.DISLIKE, shorts_id=shorts_id, user_id=user.id,
                    created_at=datetime.now()
                )
            )
            await self.shorts_repository.update_dislike_cnt(shorts_id, disliked=False)
            dislike['disliked'] = True
            dislike['cnt'] += 1
        return {'like': like, 'dislike': dislike}


class ShortsCommentService:
    def __init__(self):
        self.shorts_comment_repository = ShortsCommentRepository()
        self.shorts_comment_like_repository = ShortsCommentLikeRepository()

    async def find_all(self, shorts_id: int, user: UserEntity) -> list:
        comments = await self.shorts_comment_repository.find_all(shorts_id)
        for comment in comments:
            comment.child_comments = await self.shorts_comment_repository.find_all_by_parent_id(shorts_id, comment.id)
            for child_comment in comment.child_comments:
                child_comment.liked = (await self.shorts_comment_like_repository.find_one_by_liked(child_comment.id, user.id))['liked']
                child_comment.disliked = (await self.shorts_comment_like_repository.find_one_by_disliked(child_comment.id, user.id))['disliked']

            comment.liked = (await self.shorts_comment_like_repository.find_one_by_liked(comment.id, user.id))['liked']
            comment.disliked = (await self.shorts_comment_like_repository.find_one_by_disliked(comment.id, user.id))['disliked']
        return comments

    async def create(self, shorts_id: int, content: str, user: UserEntity, parent_id: int | None = None):
        await self.shorts_comment_repository.create(
            ShortsCommentEntity(
                content=content, shorts_id=shorts_id, user_id=user.id, created_at=datetime.now(),
                parent_id=parent_id,
            )
        )

    async def toggle_like(self, shorts_id: int, comment_id: int, user: UserEntity) -> dict:
        dislike = await self.shorts_comment_like_repository.find_one_by_disliked(comment_id, user.id)
        if dislike['disliked'] is True:
            await self.shorts_comment_like_repository.delete_by_user_id(comment_id, user.id, ShortsCommentLikeEnum.DISLIKE)
            await self.shorts_comment_repository.update_dislike_cnt(comment_id, disliked=True)
            dislike['disliked'] = False
            dislike['cnt'] -= 1

        like = await self.shorts_comment_like_repository.find_one_by_liked(comment_id, user.id)
        if like['liked'] is True:
            await self.shorts_comment_like_repository.delete_by_user_id(comment_id, user.id, ShortsCommentLikeEnum.LIKE)
            await self.shorts_comment_repository.update_like_cnt(comment_id, liked=True)
            like['liked'] = False
            like['cnt'] -= 1
        else:
            await self.shorts_comment_like_repository.create(
                ShortsCommentLikeEntity(
                    kind=ShortsCommentLikeEnum.LIKE, shorts_id=shorts_id, user_id=user.id,
                    created_at=datetime.now(), comment_id=comment_id,
                )
            )
            await self.shorts_comment_repository.update_like_cnt(comment_id, liked=False)
            like['liked'] = True
            like['cnt'] += 1
        return {'like': like, 'dislike': dislike}

    async def toggle_dislike(self, shorts_id: int, comment_id: int, user: UserEntity) -> dict:
        like = await self.shorts_comment_like_repository.find_one_by_liked(comment_id, user.id)
        if like['liked'] is True:
            await self.shorts_comment_like_repository.delete_by_user_id(comment_id, user.id, ShortsCommentLikeEnum.LIKE)
            await self.shorts_comment_repository.update_like_cnt(comment_id, liked=True)
            like['liked'] = False
            like['cnt'] -= 1

        dislike = await self.shorts_comment_like_repository.find_one_by_disliked(comment_id, user.id)
        if dislike['disliked'] is True:
            await self.shorts_comment_like_repository.delete_by_user_id(comment_id, user.id, ShortsCommentLikeEnum.DISLIKE)
            await self.shorts_comment_repository.update_dislike_cnt(comment_id, disliked=True)
            dislike['disliked'] = False
            dislike['cnt'] -= 1
        else:
            await self.shorts_comment_like_repository.create(
                ShortsCommentLikeEntity(
                    kind=ShortsCommentLikeEnum.DISLIKE, shorts_id=shorts_id, user_id=user.id,
                    created_at=datetime.now(), comment_id=comment_id,
                )
            )
            await self.shorts_comment_repository.update_dislike_cnt(comment_id, disliked=False)
            dislike['disliked'] = True
            dislike['cnt'] += 1
        return {'like': like, 'dislike': dislike}
