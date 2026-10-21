import json
from datetime import datetime

from app.common.response import NotFoundException, BadRequestException, PermissionDeniedException
from app.database.cache import Cache
from app.database.mysql import UserEntity, VideoLikeEnum, VideoLikeEntity, VideoCommentEntity, VideoCommentLikeEnum, \
    VideoCommentLikeEntity
from app.repository.channel import ChannelRepository
from app.repository.channel_subscription import ChannelSubscriptionRepository
from app.repository.shorts import ShortsRepository
from app.repository.tag import TagRepository
from app.repository.user import UserRepository
from app.repository.video import VideoRepository
from app.repository.video_comment import VideoCommentRepository
from app.repository.video_comment_like import VideoCommentLikeRepository
from app.repository.video_like import VideoLikeRepository


class VideoService:
    def __init__(self):
        self.tag_repository = TagRepository()
        self.video_repository = VideoRepository()
        self.shorts_repository = ShortsRepository()
        self.channel_repository = ChannelRepository()
        self.video_like_repository = VideoLikeRepository()
        self.channel_subscription_repository = ChannelSubscriptionRepository()
        self.user_repository = UserRepository()

    async def find_video_list(self) -> dict:
        tags = await self.tag_repository.find_unique_tag()
        videos = await self.video_repository.find_all()
        shorts = await self.shorts_repository.find_all()
        return {'tags': tags, 'videos': videos, 'shorts': shorts}

    async def find_video(self, video_id: int, user: UserEntity) -> dict:
        video = await self.video_repository.find_one_by_id(video_id)
        if not video:
            raise NotFoundException()

        channel = await self.channel_repository.find_one_by_id(video.channel_id)
        if not channel:
            raise NotFoundException()

        liked: dict = await self.video_like_repository.find_one_by_liked(video_id, user.id)
        disliked: dict = await self.video_like_repository.find_one_by_disliked(video_id, user.id)

        messages = await Cache.lrange(f'fastapi_room_{video_id}', 0, 100)
        messages.reverse()
        for idx, message in enumerate(messages):
            messages[idx] = json.loads(message)

        sub = await self.channel_subscription_repository.find_one_by_id(channel.id, user.id)
        video_user = await self.user_repository.find_one_by_id(video.user_id)

        return {
            'video': video, 'channel': channel, 'liked': liked, 'disliked': disliked, 'messages': messages,
            'subscription': True if sub else False, 'video_user': video_user,
        }

    async def toggle_like(self, video_id: int, user: UserEntity) -> dict:
        dislike = await self.video_like_repository.find_one_by_disliked(video_id, user.id)
        if dislike['disliked'] is True:
            await self.video_like_repository.delete_by_user_id(video_id, user.id, VideoLikeEnum.DISLIKE)
            await self.video_repository.update_dislike_cnt(video_id, disliked=True)
            dislike['disliked'] = False
            dislike['cnt'] -= 1

        like = await self.video_like_repository.find_one_by_liked(video_id, user.id)
        if like['liked'] is True:
            await self.video_like_repository.delete_by_user_id(video_id, user.id, VideoLikeEnum.LIKE)
            await self.video_repository.update_like_cnt(video_id, liked=True)
            like['liked'] = False
            like['cnt'] -= 1
        else:
            await self.video_like_repository.create(
                VideoLikeEntity(
                    kind=VideoLikeEnum.LIKE, video_id=video_id, user_id=user.id,
                    created_at=datetime.now()
                )
            )
            await self.video_repository.update_like_cnt(video_id, liked=False)
            like['liked'] = True
            like['cnt'] += 1
        return {'like': like, 'dislike': dislike}

    async def toggle_dislike(self, video_id: int, user: UserEntity) -> dict:
        like = await self.video_like_repository.find_one_by_liked(video_id, user.id)
        if like['liked'] is True:
            await self.video_like_repository.delete_by_user_id(video_id, user.id, VideoLikeEnum.LIKE)
            await self.video_repository.update_like_cnt(video_id, liked=True)
            like['liked'] = False
            like['cnt'] -= 1

        dislike = await self.video_like_repository.find_one_by_disliked(video_id, user.id)
        if dislike['disliked'] is True:
            await self.video_like_repository.delete_by_user_id(video_id, user.id, VideoLikeEnum.DISLIKE)
            await self.video_repository.update_dislike_cnt(video_id, disliked=True)
            dislike['disliked'] = False
            dislike['cnt'] -= 1
        else:
            await self.video_like_repository.create(
                VideoLikeEntity(
                    kind=VideoLikeEnum.DISLIKE, video_id=video_id, user_id=user.id,
                    created_at=datetime.now()
                )
            )
            await self.video_repository.update_dislike_cnt(video_id, disliked=False)
            dislike['disliked'] = True
            dislike['cnt'] += 1
        return {'like': like, 'dislike': dislike}


class VideoCommentService:
    def __init__(self):
        self.video_comment_repository = VideoCommentRepository()
        self.video_comment_like_repository = VideoCommentLikeRepository()

    async def find_all(self, video_id: int, user: UserEntity) -> list:
        comments = await self.video_comment_repository.find_all(video_id)
        for comment in comments:
            comment.child_comments = await self.video_comment_repository.find_all_by_parent_id(video_id, comment.id)
            for child_comment in comment.child_comments:
                child_comment.liked = (await self.video_comment_like_repository.find_one_by_liked(child_comment.id, user.id))['liked']
                child_comment.disliked = (await self.video_comment_like_repository.find_one_by_disliked(child_comment.id, user.id))['disliked']

            comment.liked = (await self.video_comment_like_repository.find_one_by_liked(comment.id, user.id))['liked']
            comment.disliked = (await self.video_comment_like_repository.find_one_by_disliked(comment.id, user.id))['disliked']
        return comments

    async def create(self, video_id: int, content: str, user: UserEntity, parent_id: int | None = None):
        await self.video_comment_repository.create(
            VideoCommentEntity(
                content=content, video_id=video_id, user_id=user.id, created_at=datetime.now(),
                parent_id=parent_id,
            )
        )

    async def toggle_like(self, video_id: int, comment_id: int, user: UserEntity) -> dict:
        dislike = await self.video_comment_like_repository.find_one_by_disliked(comment_id, user.id)
        if dislike['disliked'] is True:
            await self.video_comment_like_repository.delete_by_user_id(comment_id, user.id, VideoCommentLikeEnum.DISLIKE)
            await self.video_comment_repository.update_dislike_cnt(comment_id, disliked=True)
            dislike['disliked'] = False
            dislike['cnt'] -= 1

        like = await self.video_comment_like_repository.find_one_by_liked(comment_id, user.id)
        if like['liked'] is True:
            await self.video_comment_like_repository.delete_by_user_id(comment_id, user.id, VideoCommentLikeEnum.LIKE)
            await self.video_comment_repository.update_like_cnt(comment_id, liked=True)
            like['liked'] = False
            like['cnt'] -= 1
        else:
            await self.video_comment_like_repository.create(
                VideoCommentLikeEntity(
                    kind=VideoCommentLikeEnum.LIKE, video_id=video_id, user_id=user.id,
                    created_at=datetime.now(), comment_id=comment_id,
                )
            )
            await self.video_comment_repository.update_like_cnt(comment_id, liked=False)
            like['liked'] = True
            like['cnt'] += 1
        return {'like': like, 'dislike': dislike}

    async def toggle_dislike(self, video_id: int, comment_id: int, user: UserEntity) -> dict:
        like = await self.video_comment_like_repository.find_one_by_liked(comment_id, user.id)
        if like['liked'] is True:
            await self.video_comment_like_repository.delete_by_user_id(comment_id, user.id, VideoCommentLikeEnum.LIKE)
            await self.video_comment_repository.update_like_cnt(comment_id, liked=True)
            like['liked'] = False
            like['cnt'] -= 1

        dislike = await self.video_comment_like_repository.find_one_by_disliked(comment_id, user.id)
        if dislike['disliked'] is True:
            await self.video_comment_like_repository.delete_by_user_id(comment_id, user.id, VideoCommentLikeEnum.DISLIKE)
            await self.video_comment_repository.update_dislike_cnt(comment_id, disliked=True)
            dislike['disliked'] = False
            dislike['cnt'] -= 1
        else:
            await self.video_comment_like_repository.create(
                VideoCommentLikeEntity(
                    kind=VideoCommentLikeEnum.DISLIKE, video_id=video_id, user_id=user.id,
                    created_at=datetime.now(), comment_id=comment_id,
                )
            )
            await self.video_comment_repository.update_dislike_cnt(comment_id, disliked=False)
            dislike['disliked'] = True
            dislike['cnt'] += 1
        return {'like': like, 'dislike': dislike}

    async def toggle_fixed(self, video_id: int, comment_id: int, user: UserEntity):
        comment = await self.video_comment_repository.find_one_by_id(comment_id)
        if not comment:
            raise BadRequestException()
        video = await self.video_comment_repository.find_one_by_id(video_id)
        if not video:
            raise BadRequestException()

        if video.user_id != user.id:
            raise PermissionDeniedException()

        is_fixed = False if comment.is_fixed else True
        await self.video_comment_repository.update_is_fixed(comment_id, is_fixed)
