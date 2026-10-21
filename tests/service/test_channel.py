import pytest

from app.service.channel import ChannelService
from tests.service.utils import mock_repositories


@pytest.fixture
def service() -> ChannelService:
    return mock_repositories(ChannelService())


@pytest.mark.asyncio
async def test_get_channel(service, user):
    service.channel_subscription_repository.find_one_by_id.return_value = 'sub'
    service.channel_repository.find_one_by_id.return_value = 'channel'

    result = await service.get_channel(10, user)

    assert result == {'subscription': 'sub', 'channel': 'channel'}
    service.channel_subscription_repository.find_one_by_id.assert_awaited_once_with(10, user.id)
    service.channel_repository.find_one_by_id.assert_awaited_once_with(10)


@pytest.mark.asyncio
async def test_toggle_subscription_subscribe(service, user):
    service.channel_subscription_repository.find_one_by_id.return_value = None

    assert await service.toggle_subscription(10, user) is True

    entity = service.channel_subscription_repository.create.call_args.args[0]
    assert entity.channel_id == 10 and entity.user_id == user.id
    service.channel_subscription_repository.delete.assert_not_awaited()


@pytest.mark.asyncio
async def test_toggle_subscription_unsubscribe(service, user):
    service.channel_subscription_repository.find_one_by_id.return_value = 'sub'

    assert await service.toggle_subscription(10, user) is False

    service.channel_subscription_repository.delete.assert_awaited_once_with(10, user.id)
    service.channel_subscription_repository.create.assert_not_awaited()
