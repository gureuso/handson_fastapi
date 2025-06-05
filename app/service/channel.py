from app.database.mysql import database, ChannelEntity, channel_table


class ChannelService:
    @staticmethod
    async def create(channel_entity: ChannelEntity) -> ChannelEntity:
        query = channel_table.insert().values(
            name=channel_entity.name, image=channel_entity.image,
            created_at=channel_entity.created_at,
        )
        ai = await database.execute(query)
        channel_entity.id = ai
        return channel_entity

    @staticmethod
    async def find_one_by_id(channel_id: int):
        query = channel_table.select().where(channel_table.c.id == channel_id)
        row = await database.fetch_one(query)
        return ChannelEntity(**dict(row)) if row else None
