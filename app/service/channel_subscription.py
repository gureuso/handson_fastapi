from app.database.mysql import database, ChannelSubscriptionEntity, channel_subscription_table


class ChannelSubscriptionService:
    @staticmethod
    async def create(channel_subscription_entity: ChannelSubscriptionEntity) -> ChannelSubscriptionEntity:
        query = channel_subscription_table.insert().values(
            user_id=channel_subscription_entity.user_id, created_at=channel_subscription_entity.created_at,
            channel_id=channel_subscription_entity.channel_id,
        )
        ai = await database.execute(query)
        channel_subscription_entity.id = ai
        return channel_subscription_entity

    @staticmethod
    async def find_one_by_id(channel_id: int, user_id: int):
        query = channel_subscription_table.select().where(channel_subscription_table.c.channel_id == channel_id).where(channel_subscription_table.c.user_id == user_id)
        row = await database.fetch_one(query)
        return ChannelSubscriptionEntity(**dict(row)) if row else None

    @staticmethod
    async def delete(channel_id: int, user_id: int):
        query = """
            DELETE FROM ChannelSubscription WHERE channel_id = :channel_id AND user_id = :user_id;
        """
        await database.execute(query, {'channel_id': channel_id, 'user_id': user_id})
        return {}
