from datetime import datetime

import pytest
import pytest_asyncio

from app.database.mysql import ShortsEntity, ShortsLikeEntity, ShortsLikeEnum, ShortsCommentEntity, \
    ShortsCommentLikeEntity, ShortsCommentLikeEnum
from app.repository.shorts import ShortsRepository
from app.repository.shorts_comment import ShortsCommentRepository
from app.repository.shorts_comment_like import ShortsCommentLikeRepository
from app.repository.shorts_like import ShortsLikeRepository
from tests.repository.utils import random_name


@pytest_asyncio.fixture
async def shorts(cleanup) -> ShortsEntity:
    shorts = await ShortsRepository().create(ShortsEntity(
        channel_id=None, tag='test', title=f'test_{random_name()}', thumbnail='thumb', content='content',
        view_cnt=0, created_at=datetime.now(),
    ))
    cleanup.add('Shorts', shorts.id)
    return shorts


async def create_comment(cleanup, shorts, user, parent_id=None) -> ShortsCommentEntity:
    comment = await ShortsCommentRepository().create(ShortsCommentEntity(
        content='comment', shorts_id=shorts.id, user_id=user.id, parent_id=parent_id, created_at=datetime.now(),
    ))
    cleanup.add('ShortsComment', comment.id)
    return comment


@pytest.mark.asyncio
async def test_shorts(shorts):
    repository = ShortsRepository()

    found = await repository.find_one_by_id(shorts.id)
    assert (found.title, found.like_cnt, found.dislike_cnt) == (shorts.title, 0, 0)

    assert shorts.id in [x.id for x in await repository.find_all()]
    assert shorts.id in [x.id for x in await repository.find_all_with_random()]

    await repository.update_like_cnt(shorts.id, liked=False)
    await repository.update_dislike_cnt(shorts.id, disliked=False)
    await repository.update_dislike_cnt(shorts.id, disliked=False)
    await repository.update_dislike_cnt(shorts.id, disliked=True)
    found = await repository.find_one_by_id(shorts.id)
    assert (found.like_cnt, found.dislike_cnt) == (1, 1)

    await repository.update_like_cnt(shorts.id, liked=True)
    assert (await repository.find_one_by_id(shorts.id)).like_cnt == 0


@pytest.mark.asyncio
async def test_shorts_like(cleanup, shorts, user):
    repository = ShortsLikeRepository()
    assert await repository.find_one_by_disliked(shorts.id, user.id) == {'cnt': 0, 'disliked': False}

    dislike = await repository.create(ShortsLikeEntity(
        kind=ShortsLikeEnum.DISLIKE, shorts_id=shorts.id, user_id=user.id, created_at=datetime.now()))
    cleanup.add('ShortsLike', dislike.id)

    assert await repository.find_one_by_disliked(shorts.id, user.id) == {'cnt': 1, 'disliked': True}
    assert await repository.find_one_by_liked(shorts.id, user.id) == {'cnt': 0, 'liked': False}

    await repository.delete_by_user_id(shorts.id, user.id, ShortsLikeEnum.DISLIKE)
    assert await repository.find_one_by_disliked(shorts.id, user.id) == {'cnt': 0, 'disliked': False}


@pytest.mark.asyncio
async def test_shorts_comment(cleanup, shorts, user):
    repository = ShortsCommentRepository()
    first = await create_comment(cleanup, shorts, user)
    second = await create_comment(cleanup, shorts, user)
    child = await create_comment(cleanup, shorts, user, parent_id=first.id)

    assert (await repository.find_one_by_id(first.id)).content == 'comment'

    comments = await repository.find_all(shorts.id)
    assert sorted(x.id for x in comments) == sorted([first.id, second.id])
    assert comments[0].nickname == user.nickname

    assert [x.id for x in await repository.find_all_by_parent_id(shorts.id, first.id)] == [child.id]

    await repository.update_like_cnt(first.id, liked=False)
    await repository.update_like_cnt(first.id, liked=False)
    await repository.update_dislike_cnt(first.id, disliked=False)
    found = await repository.find_one_by_id(first.id)
    assert (found.like_cnt, found.dislike_cnt) == (2, 1)


@pytest.mark.asyncio
async def test_shorts_comment_like(cleanup, shorts, user):
    repository = ShortsCommentLikeRepository()
    comment = await create_comment(cleanup, shorts, user)

    dislike = await repository.create(ShortsCommentLikeEntity(
        kind=ShortsCommentLikeEnum.DISLIKE, shorts_id=shorts.id, comment_id=comment.id, user_id=user.id,
        created_at=datetime.now()))
    cleanup.add('ShortsCommentLike', dislike.id)

    assert (await repository.find_one_by_id(dislike.id)).kind == ShortsCommentLikeEnum.DISLIKE
    assert await repository.find_one_by_disliked(comment.id, user.id) == {'cnt': 1, 'disliked': True}
    assert await repository.find_one_by_liked(comment.id, user.id) == {'cnt': 0, 'liked': False}

    await repository.delete_by_user_id(comment.id, user.id, ShortsCommentLikeEnum.DISLIKE)
    assert await repository.find_one_by_disliked(comment.id, user.id) == {'cnt': 0, 'disliked': False}
