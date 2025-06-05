from app.database.mysql import database, TagEntity, tag_table


class TagService:
    @staticmethod
    async def create(tag_entity: TagEntity) -> TagEntity:
        query = tag_table.insert().values(
            video_id=tag_entity.video_id, name=tag_entity.name,
        )
        ai = await database.execute(query)
        tag_entity.id = ai
        return tag_entity

    @staticmethod
    async def find_one_by_id(tag_id: int):
        query = tag_table.select().where(tag_table.c.id == tag_id)
        row = await database.fetch_one(query)
        return TagEntity(**dict(row)) if row else None

    @staticmethod
    async def find_unique_tag():
        query = """
            SELECT name FROM Tag GROUP BY name;
        """
        rows = await database.fetch_all(query)
        return [TagEntity(**dict(row)) for row in rows]
