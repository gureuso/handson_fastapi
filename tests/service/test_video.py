import json
from datetime import datetime
from unittest.mock import AsyncMock

import pytest

from app.common.response import NotFoundException, BadRequestException, PermissionDeniedException
from app.database.mysql import VideoLikeEnum, VideoCommentLikeEnum, VideoEntity, ChannelEntity, VideoCommentEntity
from app.service import video as video_module
from app.service.video import VideoService, VideoCommentService
from tests.service.utils import mock_repositories, like_state, dislike_state


@pytest.fixture
def service() -> VideoService:
    return mock_repositories(VideoService())


@pytest.fixture
def comment_service() -> VideoCommentService:
    return mock_repositories(VideoCommentService())


def make_video(**kwargs) -> VideoEntity:
    data = dict(id=1, channel_id=2, user_id=3, tag='tag', title='title', thumbnail='thumb', content='content',
                view_cnt=0, created_at=datetime.now())
    data.update(kwargs)
    return VideoEntity(**data)


def make_comment(comment_id: int, **kwargs) -> VideoCommentEntity:
    data = dict(id=comment_id, content='comment', video_id=1, user_id=1, created_at=datetime.now())
    data.update(kwargs)
    return VideoCommentEntity(**data)


@pytest.mark.asyncio
async def test_find_video_list(service):
    service.tag_repository.find_unique_tag.return_value = ['tag']
    service.video_repository.find_all.return_value = ['video']
    service.shorts_repository.find_all.return_value = ['shorts']

    assert await service.find_video_list() == {'tags': ['tag'], 'videos': ['video'], 'shorts': ['shorts']}


@pytest.mark.asyncio
async def test_find_video_not_found(service, user):
    service.video_repository.find_one_by_id.return_value = None
    with pytest.raises(NotFoundException):
        await service.find_video(1, user)

    service.video_repository.find_one_by_id.return_value = make_video()
    service.channel_repository.find_one_by_id.return_value = None
    with pytest.raises(NotFoundException):
        await service.find_video(1, user)


@pytest.mark.asyncio
async def test_find_video(service, user, monkeypatch):
    video = make_video()
    channel = ChannelEntity(id=2, name='channel', image='image', created_at=datetime.now())
    service.video_repository.find_one_by_id.return_value = video
    service.channel_repository.find_one_by_id.return_value = channel
    service.video_like_repository.find_one_by_liked.return_value = like_state(5, True)
    service.video_like_repository.find_one_by_disliked.return_value = dislike_state(1, False)
    service.channel_subscription_repository.find_one_by_id.return_value = None
    service.user_repository.find_one_by_id.return_value = user

    # Redis에는 최신 메시지가 앞에 쌓여 있으므로 응답에서는 역순(오래된 순)이어야 한다
    cache = AsyncMock()
    cache.lrange.return_value = [json.dumps({'msg': 'new'}), json.dumps({'msg': 'old'})]
    monkeypatch.setattr(video_module, 'Cache', cache)

    result = await service.find_video(1, user)

    cache.lrange.assert_awaited_once_with('fastapi_room_1', 0, 100)
    assert result == {
        'video': video, 'channel': channel, 'liked': like_state(5, True), 'disliked': dislike_state(1, False),
        'messages': [{'msg': 'old'}, {'msg': 'new'}], 'subscription': False, 'video_user': user,
    }
    service.user_repository.find_one_by_id.assert_awaited_once_with(video.user_id)


@pytest.mark.asyncio
async def test_toggle_like_add(service, user):
    service.video_like_repository.find_one_by_disliked.return_value = dislike_state(0, False)
    service.video_like_repository.find_one_by_liked.return_value = like_state(3, False)

    result = await service.toggle_like(1, user)

    assert result == {'like': like_state(4, True), 'dislike': dislike_state(0, False)}
    entity = service.video_like_repository.create.call_args.args[0]
    assert entity.kind == VideoLikeEnum.LIKE and entity.video_id == 1 and entity.user_id == user.id
    service.video_repository.update_like_cnt.assert_awaited_once_with(1, liked=False)
    service.video_like_repository.delete_by_user_id.assert_not_awaited()


@pytest.mark.asyncio
async def test_toggle_like_cancel(service, user):
    service.video_like_repository.find_one_by_disliked.return_value = dislike_state(0, False)
    service.video_like_repository.find_one_by_liked.return_value = like_state(3, True)

    result = await service.toggle_like(1, user)

    assert result == {'like': like_state(2, False), 'dislike': dislike_state(0, False)}
    service.video_like_repository.delete_by_user_id.assert_awaited_once_with(1, user.id, VideoLikeEnum.LIKE)
    service.video_repository.update_like_cnt.assert_awaited_once_with(1, liked=True)
    service.video_like_repository.create.assert_not_awaited()


@pytest.mark.asyncio
async def test_toggle_like_removes_dislike(service, user):
    service.video_like_repository.find_one_by_disliked.return_value = dislike_state(2, True)
    service.video_like_repository.find_one_by_liked.return_value = like_state(3, False)

    result = await service.toggle_like(1, user)

    assert result == {'like': like_state(4, True), 'dislike': dislike_state(1, False)}
    service.video_like_repository.delete_by_user_id.assert_awaited_once_with(1, user.id, VideoLikeEnum.DISLIKE)
    service.video_repository.update_dislike_cnt.assert_awaited_once_with(1, disliked=True)
    service.video_repository.update_like_cnt.assert_awaited_once_with(1, liked=False)


@pytest.mark.asyncio
async def test_toggle_dislike_add(service, user):
    service.video_like_repository.find_one_by_liked.return_value = like_state(0, False)
    service.video_like_repository.find_one_by_disliked.return_value = dislike_state(3, False)

    result = await service.toggle_dislike(1, user)

    assert result == {'like': like_state(0, False), 'dislike': dislike_state(4, True)}
    assert service.video_like_repository.create.call_args.args[0].kind == VideoLikeEnum.DISLIKE
    service.video_repository.update_dislike_cnt.assert_awaited_once_with(1, disliked=False)


@pytest.mark.asyncio
async def test_toggle_dislike_cancel_and_removes_like(service, user):
    service.video_like_repository.find_one_by_liked.return_value = like_state(5, True)
    service.video_like_repository.find_one_by_disliked.return_value = dislike_state(3, True)

    result = await service.toggle_dislike(1, user)

    assert result == {'like': like_state(4, False), 'dislike': dislike_state(2, False)}
    service.video_repository.update_like_cnt.assert_awaited_once_with(1, liked=True)
    service.video_repository.update_dislike_cnt.assert_awaited_once_with(1, disliked=True)
    service.video_like_repository.create.assert_not_awaited()


@pytest.mark.asyncio
async def test_comment_find_all(comment_service, user):
    parent, child = make_comment(10), make_comment(11, parent_id=10)
    comment_service.video_comment_repository.find_all.return_value = [parent]
    comment_service.video_comment_repository.find_all_by_parent_id.return_value = [child]
    comment_service.video_comment_like_repository.find_one_by_liked.side_effect = \
        lambda comment_id, user_id: like_state(1, comment_id == 10)
    comment_service.video_comment_like_repository.find_one_by_disliked.side_effect = \
        lambda comment_id, user_id: dislike_state(1, comment_id == 11)

    comments = await comment_service.find_all(1, user)

    assert comments == [parent]
    comment_service.video_comment_repository.find_all_by_parent_id.assert_awaited_once_with(1, 10)
    assert parent.child_comments == [child]
    assert (parent.liked, parent.disliked) == (True, False)
    assert (child.liked, child.disliked) == (False, True)


@pytest.mark.asyncio
async def test_comment_create(comment_service, user):
    await comment_service.create(1, 'hello', user)
    entity = comment_service.video_comment_repository.create.call_args.args[0]
    assert (entity.video_id, entity.content, entity.user_id, entity.parent_id) == (1, 'hello', user.id, None)

    await comment_service.create(1, 'reply', user, parent_id=10)
    assert comment_service.video_comment_repository.create.call_args.args[0].parent_id == 10


@pytest.mark.asyncio
async def test_comment_toggle_like(comment_service, user):
    comment_service.video_comment_like_repository.find_one_by_disliked.return_value = dislike_state(1, True)
    comment_service.video_comment_like_repository.find_one_by_liked.return_value = like_state(0, False)

    result = await comment_service.toggle_like(1, 10, user)

    assert result == {'like': like_state(1, True), 'dislike': dislike_state(0, False)}
    comment_service.video_comment_like_repository.delete_by_user_id.assert_awaited_once_with(
        10, user.id, VideoCommentLikeEnum.DISLIKE)
    entity = comment_service.video_comment_like_repository.create.call_args.args[0]
    assert (entity.kind, entity.video_id, entity.comment_id) == (VideoCommentLikeEnum.LIKE, 1, 10)
    comment_service.video_comment_repository.update_dislike_cnt.assert_awaited_once_with(10, disliked=True)
    comment_service.video_comment_repository.update_like_cnt.assert_awaited_once_with(10, liked=False)


@pytest.mark.asyncio
async def test_comment_toggle_dislike(comment_service, user):
    comment_service.video_comment_like_repository.find_one_by_liked.return_value = like_state(1, True)
    comment_service.video_comment_like_repository.find_one_by_disliked.return_value = dislike_state(0, False)

    result = await comment_service.toggle_dislike(1, 10, user)

    assert result == {'like': like_state(0, False), 'dislike': dislike_state(1, True)}
    comment_service.video_comment_like_repository.delete_by_user_id.assert_awaited_once_with(
        10, user.id, VideoCommentLikeEnum.LIKE)
    assert comment_service.video_comment_like_repository.create.call_args.args[0].kind == VideoCommentLikeEnum.DISLIKE
    comment_service.video_comment_repository.update_like_cnt.assert_awaited_once_with(10, liked=True)
    comment_service.video_comment_repository.update_dislike_cnt.assert_awaited_once_with(10, disliked=False)


@pytest.mark.asyncio
async def test_comment_toggle_fixed(comment_service, user):
    comment = make_comment(10, is_fixed=False)
    owner_item = make_comment(1, user_id=user.id)
    # 현재 구현은 video_id도 VideoCommentRepository.find_one_by_id로 조회한다
    comment_service.video_comment_repository.find_one_by_id.side_effect = \
        lambda item_id: {10: comment, 1: owner_item}.get(item_id)

    await comment_service.toggle_fixed(1, 10, user)
    comment_service.video_comment_repository.update_is_fixed.assert_awaited_once_with(10, True)

    comment.is_fixed = True
    await comment_service.toggle_fixed(1, 10, user)
    comment_service.video_comment_repository.update_is_fixed.assert_awaited_with(10, False)


@pytest.mark.asyncio
async def test_comment_toggle_fixed_errors(comment_service, user):
    repo = comment_service.video_comment_repository

    repo.find_one_by_id.side_effect = lambda item_id: None
    with pytest.raises(BadRequestException):
        await comment_service.toggle_fixed(1, 10, user)

    repo.find_one_by_id.side_effect = lambda item_id: make_comment(10) if item_id == 10 else None
    with pytest.raises(BadRequestException):
        await comment_service.toggle_fixed(1, 10, user)

    repo.find_one_by_id.side_effect = lambda item_id: make_comment(item_id, user_id=user.id + 1)
    with pytest.raises(PermissionDeniedException):
        await comment_service.toggle_fixed(1, 10, user)

    repo.update_is_fixed.assert_not_awaited()
