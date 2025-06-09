from typing import List

from app.database.mysql import database, ShortsEntity, shorts_table


class ShortsService:
    @staticmethod
    async def create(shorts_entity: ShortsEntity) -> ShortsEntity:
        query = shorts_table.insert().values(
            channel_id=shorts_entity.channel_id, title=shorts_entity.title,
            thumbnail=shorts_entity.thumbnail, content=shorts_entity.content,
            view_cnt=shorts_entity.view_cnt, created_at=shorts_entity.created_at,
        )
        ai = await database.execute(query)
        shorts_entity.id = ai
        return shorts_entity

    @staticmethod
    async def find_one_by_id(shorts_id: int) -> ShortsEntity:
        query = shorts_table.select().where(shorts_table.c.id == shorts_id)
        row = await database.fetch_one(query)
        return ShortsEntity(**dict(row)) if row else None

    @staticmethod
    async def find_all() -> List[ShortsEntity]:
        query = """
            SELECT S.* FROM Shorts AS S ORDER BY S.view_cnt DESC;
        """
        rows = await database.fetch_all(query)
        return [ShortsEntity(**dict(row)) for row in rows]

    @staticmethod
    async def find_all_with_random() -> List[ShortsEntity]:
        query = """
            SELECT S.* FROM Shorts AS S ORDER BY RAND();
        """
        rows = await database.fetch_all(query)
        return [ShortsEntity(**dict(row)) for row in rows]

    @staticmethod
    async def update_like_cnt(shorts_id: int):
        query = """
            UPDATE Shorts SET like_cnt = like_cnt + 1 WHERE id = :shorts_id;
        """
        await database.execute(query, {'shorts_id': shorts_id})
        return {}

    @staticmethod
    async def update_dislike_cnt(shorts_id: int):
        query = """
            UPDATE Shorts SET dislike_cnt = dislike_cnt + 1 WHERE id = :shorts_id;
        """
        await database.execute(query, {'shorts_id': shorts_id})
        return {}
