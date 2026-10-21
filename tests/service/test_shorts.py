import json
from datetime import datetime
from unittest.mock import AsyncMock

import pytest

from app.database.mysql import ShortsEntity, ShortsLikeEnum, ShortsCommentLikeEnum, ShortsCommentEntity
from app.service import shorts as shorts_module
from app.service.shorts import ShortsService, ShortsCommentService
from tests.service.utils import mock_repositories, like_state, dislike_state


@pytest.fixture
def service() -> ShortsService:
    return mock_repositories(ShortsService())


@pytest.fixture
def comment_service() -> ShortsCommentService:
    return mock_repositories(ShortsCommentService())


@pytest.fixture
def cache(monkeypatch) -> AsyncMock:
    cache = AsyncMock()
    monkeypatch.setattr(shorts_module, 'Cache', cache)
    return cache


def make_shorts(shorts_id: int) -> ShortsEntity:
    return ShortsEntity(
        id=shorts_id, channel_id=1, tag='tag', title=f'title{shorts_id}', thumbnail='thumb', content='content',
        view_cnt=0, created_at=datetime(2025, 5, 1, 11, 11, 11),
    )


def make_comment(comment_id: int, **kwargs) -> ShortsCommentEntity:
    data = dict(id=comment_id, content='comment', shorts_id=1, user_id=1, created_at=datetime.now())
    data.update(kwargs)
    return ShortsCommentEntity(**data)


@pytest.mark.asyncio
async def test_find_shorts_list_cache_miss(service, cache):
    shorts_list = [make_shorts(1), make_shorts(2)]
    cache.get.return_value = None
    service.shorts_repository.find_all_with_random.return_value = shorts_list

    assert await service.find_shorts_list() == shorts_list

    key, ttl, payload = cache.setex.call_args.args
    assert (key, ttl) == ('fastapi_get_shorts_list', 60)
    assert [x['id'] for x in json.loads(payload)] == [1, 2]
    assert json.loads(payload)[0]['created_at'] == '2025-05-01 11:11:11'


@pytest.mark.asyncio
async def test_find_shorts_list_cache_hit(service, cache):
    shorts_list = [make_shorts(1), make_shorts(2)]
    cache.get.return_value = json.dumps(
        [x.model_dump() for x in shorts_list], default=lambda o: o.strftime('%Y-%m-%d %H:%M:%S'))

    assert await service.find_shorts_list() == shorts_list

    service.shorts_repository.find_all_with_random.assert_not_awaited()
    cache.setex.assert_not_awaited()


@pytest.mark.asyncio
async def test_find_shorts(service, user, cache):
    cache.get.return_value = None
    service.shorts_repository.find_all_with_random.return_value = [make_shorts(1), make_shorts(2), make_shorts(3)]
    service.shorts_like_repository.find_one_by_liked.return_value = like_state(1, True)
    service.shorts_like_repository.find_one_by_disliked.return_value = dislike_state(0, False)

    result = await service.find_shorts(2, user)
    assert result['current_shorts'].id == 2
    assert result['next_shorts'].id == 3
    assert result['liked'] == like_state(1, True)
    assert result['disliked'] == dislike_state(0, False)
    service.shorts_like_repository.find_one_by_liked.assert_awaited_once_with(2, user.id)

    # 마지막 shorts의 다음은 첫 번째 shorts
    result = await service.find_shorts(3, user)
    assert result['next_shorts'].id == 1


@pytest.mark.asyncio
async def test_toggle_like(service, user):
    service.shorts_like_repository.find_one_by_disliked.return_value = dislike_state(1, True)
    service.shorts_like_repository.find_one_by_liked.return_value = like_state(0, False)

    result = await service.toggle_like(1, user)

    assert result == {'like': like_state(1, True), 'dislike': dislike_state(0, False)}
    service.shorts_like_repository.delete_by_user_id.assert_awaited_once_with(1, user.id, ShortsLikeEnum.DISLIKE)
    entity = service.shorts_like_repository.create.call_args.args[0]
    assert (entity.kind, entity.shorts_id, entity.user_id) == (ShortsLikeEnum.LIKE, 1, user.id)
    service.shorts_repository.update_dislike_cnt.assert_awaited_once_with(1, disliked=True)
    service.shorts_repository.update_like_cnt.assert_awaited_once_with(1, liked=False)


@pytest.mark.asyncio
async def test_toggle_like_cancel(service, user):
    service.shorts_like_repository.find_one_by_disliked.return_value = dislike_state(0, False)
    service.shorts_like_repository.find_one_by_liked.return_value = like_state(1, True)

    result = await service.toggle_like(1, user)

    assert result == {'like': like_state(0, False), 'dislike': dislike_state(0, False)}
    service.shorts_like_repository.delete_by_user_id.assert_awaited_once_with(1, user.id, ShortsLikeEnum.LIKE)
    service.shorts_repository.update_like_cnt.assert_awaited_once_with(1, liked=True)
    service.shorts_like_repository.create.assert_not_awaited()


@pytest.mark.asyncio
async def test_toggle_dislike(service, user):
    service.shorts_like_repository.find_one_by_liked.return_value = like_state(1, True)
    service.shorts_like_repository.find_one_by_disliked.return_value = dislike_state(0, False)

    result = await service.toggle_dislike(1, user)

    assert result == {'like': like_state(0, False), 'dislike': dislike_state(1, True)}
    service.shorts_like_repository.delete_by_user_id.assert_awaited_once_with(1, user.id, ShortsLikeEnum.LIKE)
    assert service.shorts_like_repository.create.call_args.args[0].kind == ShortsLikeEnum.DISLIKE
    service.shorts_repository.update_like_cnt.assert_awaited_once_with(1, liked=True)
    service.shorts_repository.update_dislike_cnt.assert_awaited_once_with(1, disliked=False)


@pytest.mark.asyncio
async def test_toggle_dislike_cancel(service, user):
    service.shorts_like_repository.find_one_by_liked.return_value = like_state(0, False)
    service.shorts_like_repository.find_one_by_disliked.return_value = dislike_state(1, True)

    result = await service.toggle_dislike(1, user)

    assert result == {'like': like_state(0, False), 'dislike': dislike_state(0, False)}
    service.shorts_like_repository.delete_by_user_id.assert_awaited_once_with(1, user.id, ShortsLikeEnum.DISLIKE)
    service.shorts_repository.update_dislike_cnt.assert_awaited_once_with(1, disliked=True)
    service.shorts_like_repository.create.assert_not_awaited()


@pytest.mark.asyncio
async def test_comment_find_all(comment_service, user):
    parent, child = make_comment(10), make_comment(11, parent_id=10)
    comment_service.shorts_comment_repository.find_all.return_value = [parent]
    comment_service.shorts_comment_repository.find_all_by_parent_id.return_value = [child]
    comment_service.shorts_comment_like_repository.find_one_by_liked.side_effect = \
        lambda comment_id, user_id: like_state(1, comment_id == 11)
    comment_service.shorts_comment_like_repository.find_one_by_disliked.side_effect = \
        lambda comment_id, user_id: dislike_state(1, comment_id == 10)

    comments = await comment_service.find_all(1, user)

    assert comments == [parent]
    assert parent.child_comments == [child]
    assert (parent.liked, parent.disliked) == (False, True)
    assert (child.liked, child.disliked) == (True, False)


@pytest.mark.asyncio
async def test_comment_create(comment_service, user):
    await comment_service.create(1, 'hello', user)
    entity = comment_service.shorts_comment_repository.create.call_args.args[0]
    assert (entity.shorts_id, entity.content, entity.user_id, entity.parent_id) == (1, 'hello', user.id, None)

    await comment_service.create(1, 'reply', user, parent_id=10)
    assert comment_service.shorts_comment_repository.create.call_args.args[0].parent_id == 10


@pytest.mark.asyncio
async def test_comment_toggle_like(comment_service, user):
    comment_service.shorts_comment_like_repository.find_one_by_disliked.return_value = dislike_state(0, False)
    comment_service.shorts_comment_like_repository.find_one_by_liked.return_value = like_state(2, True)

    result = await comment_service.toggle_like(1, 10, user)

    assert result == {'like': like_state(1, False), 'dislike': dislike_state(0, False)}
    comment_service.shorts_comment_like_repository.delete_by_user_id.assert_awaited_once_with(
        10, user.id, ShortsCommentLikeEnum.LIKE)
    comment_service.shorts_comment_repository.update_like_cnt.assert_awaited_once_with(10, liked=True)
    comment_service.shorts_comment_like_repository.create.assert_not_awaited()


@pytest.mark.asyncio
async def test_comment_toggle_dislike(comment_service, user):
    comment_service.shorts_comment_like_repository.find_one_by_liked.return_value = like_state(0, False)
    comment_service.shorts_comment_like_repository.find_one_by_disliked.return_value = dislike_state(0, False)

    result = await comment_service.toggle_dislike(1, 10, user)

    assert result == {'like': like_state(0, False), 'dislike': dislike_state(1, True)}
    entity = comment_service.shorts_comment_like_repository.create.call_args.args[0]
    assert (entity.kind, entity.shorts_id, entity.comment_id) == (ShortsCommentLikeEnum.DISLIKE, 1, 10)
    comment_service.shorts_comment_repository.update_dislike_cnt.assert_awaited_once_with(10, disliked=False)
