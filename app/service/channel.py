from datetime import datetime

from app.database.mysql import UserEntity, ChannelSubscriptionEntity
from app.repository.channel import ChannelRepository
from app.repository.channel_subscription import ChannelSubscriptionRepository


class ChannelService:
    def __init__(self):
        self.channel_subscription_repository = ChannelSubscriptionRepository()
        self.channel_repository = ChannelRepository()

    async def get_channel(self, channel_id: int, user: UserEntity) -> dict:
        sub = await self.channel_subscription_repository.find_one_by_id(channel_id, user.id)
        channel = await self.channel_repository.find_one_by_id(channel_id)
        return {'subscription': sub, 'channel': channel}

    async def toggle_subscription(self, channel_id: int, user: UserEntity) -> bool:
        sub = await self.channel_subscription_repository.find_one_by_id(channel_id, user.id)
        if sub:
            await self.channel_subscription_repository.delete(channel_id, user.id)
            return False

        await self.channel_subscription_repository.create(ChannelSubscriptionEntity(
            channel_id=channel_id, user_id=user.id,
            created_at=datetime.now(),
        ))
        return True
