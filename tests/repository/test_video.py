from datetime import datetime

import pytest
import pytest_asyncio

from app.database.mysql import ChannelEntity, VideoEntity, TagEntity, VideoLikeEntity, VideoLikeEnum, \
    VideoCommentEntity, VideoCommentLikeEntity, VideoCommentLikeEnum
from app.repository.channel import ChannelRepository
from app.repository.tag import TagRepository
from app.repository.video import VideoRepository
from app.repository.video_comment import VideoCommentRepository
from app.repository.video_comment_like import VideoCommentLikeRepository
from app.repository.video_like import VideoLikeRepository
from tests.repository.utils import random_name


@pytest_asyncio.fixture
async def channel(cleanup) -> ChannelEntity:
    channel = await ChannelRepository().create(
        ChannelEntity(name=f'test_{random_name()}', image='image', created_at=datetime.now()))
    cleanup.add('Channel', channel.id)
    return channel


@pytest_asyncio.fixture
async def video(cleanup, channel) -> VideoEntity:
    video = await VideoRepository().create(VideoEntity(
        channel_id=channel.id, tag='test', title=f'test_{random_name()}', thumbnail='thumb', content='content',
        view_cnt=0, created_at=datetime.now(),
    ))
    cleanup.add('Video', video.id)
    return video


async def create_comment(cleanup, video, user, parent_id=None) -> VideoCommentEntity:
    comment = await VideoCommentRepository().create(VideoCommentEntity(
        content='comment', video_id=video.id, user_id=user.id, parent_id=parent_id, created_at=datetime.now(),
    ))
    cleanup.add('VideoComment', comment.id)
    return comment


@pytest.mark.asyncio
async def test_video(channel, video):
    repository = VideoRepository()

    found = await repository.find_one_by_id(video.id)
    assert (found.title, found.channel_id, found.like_cnt, found.dislike_cnt) == (video.title, channel.id, 0, 0)

    videos = {x.id: x for x in await repository.find_all()}
    assert videos[video.id].name == channel.name
    assert videos[video.id].image == channel.image

    await repository.update_like_cnt(video.id, liked=False)
    await repository.update_like_cnt(video.id, liked=False)
    await repository.update_like_cnt(video.id, liked=True)
    await repository.update_dislike_cnt(video.id, disliked=False)
    found = await repository.find_one_by_id(video.id)
    assert (found.like_cnt, found.dislike_cnt) == (1, 1)

    await repository.update_dislike_cnt(video.id, disliked=True)
    assert (await repository.find_one_by_id(video.id)).dislike_cnt == 0


@pytest.mark.asyncio
async def test_tag(cleanup, video):
    repository = TagRepository()
    name = random_name(10)

    tag = await repository.create(TagEntity(video_id=video.id, name=name))
    cleanup.add('Tag', tag.id)

    assert (await repository.find_one_by_id(tag.id)).name == name
    assert name in [x.name for x in await repository.find_unique_tag()]


@pytest.mark.asyncio
async def test_video_like(cleanup, video, user):
    repository = VideoLikeRepository()
    assert await repository.find_one_by_liked(video.id, user.id) == {'cnt': 0, 'liked': False}

    like = await repository.create(VideoLikeEntity(
        kind=VideoLikeEnum.LIKE, video_id=video.id, user_id=user.id, created_at=datetime.now()))
    cleanup.add('VideoLike', like.id)
    dislike = await repository.create(VideoLikeEntity(
        kind=VideoLikeEnum.DISLIKE, video_id=video.id, user_id=user.id + 1, created_at=datetime.now()))
    cleanup.add('VideoLike', dislike.id)

    assert await repository.find_one_by_liked(video.id, user.id) == {'cnt': 1, 'liked': True}
    assert await repository.find_one_by_disliked(video.id, user.id) == {'cnt': 1, 'disliked': False}
    assert await repository.find_one_by_disliked(video.id, user.id + 1) == {'cnt': 1, 'disliked': True}

    await repository.delete_by_user_id(video.id, user.id, VideoLikeEnum.LIKE)
    assert await repository.find_one_by_liked(video.id, user.id) == {'cnt': 0, 'liked': False}
    assert (await repository.find_one_by_disliked(video.id, user.id + 1))['cnt'] == 1


@pytest.mark.asyncio
async def test_video_comment(cleanup, video, user):
    repository = VideoCommentRepository()
    parent = await create_comment(cleanup, video, user)
    fixed = await create_comment(cleanup, video, user)
    child = await create_comment(cleanup, video, user, parent_id=parent.id)

    assert (await repository.find_one_by_id(parent.id)).content == 'comment'

    await repository.update_is_fixed(fixed.id, True)
    comments = await repository.find_all(video.id)
    # 고정 댓글이 먼저, 대댓글은 제외
    assert [x.id for x in comments] == [fixed.id, parent.id]
    assert comments[0].nickname == user.nickname
    assert comments[0].profile_image == user.profile_image

    assert [x.id for x in await repository.find_all_by_parent_id(video.id, parent.id)] == [child.id]

    await repository.update_like_cnt(parent.id, liked=False)
    await repository.update_dislike_cnt(parent.id, disliked=False)
    await repository.update_dislike_cnt(parent.id, disliked=True)
    found = await repository.find_one_by_id(parent.id)
    assert (found.like_cnt, found.dislike_cnt) == (1, 0)


@pytest.mark.asyncio
async def test_video_comment_like(cleanup, video, user):
    repository = VideoCommentLikeRepository()
    comment = await create_comment(cleanup, video, user)
    assert await repository.find_one_by_liked(comment.id, user.id) == {'cnt': 0, 'liked': False}

    like = await repository.create(VideoCommentLikeEntity(
        kind=VideoCommentLikeEnum.LIKE, video_id=video.id, comment_id=comment.id, user_id=user.id,
        created_at=datetime.now()))
    cleanup.add('VideoCommentLike', like.id)

    assert (await repository.find_one_by_id(like.id)).kind == VideoCommentLikeEnum.LIKE
    assert await repository.find_one_by_liked(comment.id, user.id) == {'cnt': 1, 'liked': True}
    assert await repository.find_one_by_disliked(comment.id, user.id) == {'cnt': 0, 'disliked': False}

    await repository.delete_by_user_id(comment.id, user.id, VideoCommentLikeEnum.DISLIKE)
    assert (await repository.find_one_by_liked(comment.id, user.id))['liked'] is True

    await repository.delete_by_user_id(comment.id, user.id, VideoCommentLikeEnum.LIKE)
    assert await repository.find_one_by_liked(comment.id, user.id) == {'cnt': 0, 'liked': False}
