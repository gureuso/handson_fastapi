from datetime import datetime

import pytest

from app.database.mysql import database, ChannelEntity, ChannelSubscriptionEntity
from app.repository.channel import ChannelRepository
from app.repository.channel_subscription import ChannelSubscriptionRepository
from tests.repository.utils import random_name


@pytest.mark.asyncio
async def test_channel(cleanup, user):
    repository = ChannelRepository()
    name = f'test_{random_name()}'

    channel = await repository.create(ChannelEntity(name=name, image='image', created_at=datetime.now()))
    cleanup.add('Channel', channel.id)

    assert (await repository.find_one_by_id(channel.id)).name == name
    assert await repository.find_one_by_user_id(user.id) is None

    # create는 user_id를 저장하지 않으므로 직접 연결
    await database.execute('UPDATE Channel SET user_id = :user_id WHERE id = :id', {'user_id': user.id, 'id': channel.id})
    assert (await repository.find_one_by_user_id(user.id)).id == channel.id


@pytest.mark.asyncio
async def test_channel_subscription(cleanup, user):
    repository = ChannelSubscriptionRepository()
    channel = await ChannelRepository().create(
        ChannelEntity(name=f'test_{random_name()}', image='image', created_at=datetime.now()))
    cleanup.add('Channel', channel.id)

    assert await repository.find_one_by_id(channel.id, user.id) is None

    sub = await repository.create(ChannelSubscriptionEntity(channel_id=channel.id, user_id=user.id, created_at=datetime.now()))
    cleanup.add('ChannelSubscription', sub.id)
    assert (await repository.find_one_by_id(channel.id, user.id)).id == sub.id

    await repository.delete(channel.id, user.id)
    assert await repository.find_one_by_id(channel.id, user.id) is None
