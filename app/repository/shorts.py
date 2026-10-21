from typing import List

from app.database.mysql import database, ShortsEntity, shorts_table


class ShortsRepository:
    async def create(self, shorts_entity: ShortsEntity) -> ShortsEntity:
        query = shorts_table.insert().values(
            channel_id=shorts_entity.channel_id, title=shorts_entity.title,
            thumbnail=shorts_entity.thumbnail, content=shorts_entity.content,
            view_cnt=shorts_entity.view_cnt, created_at=shorts_entity.created_at,
        )
        ai = await database.execute(query)
        shorts_entity.id = ai
        return shorts_entity

    async def find_one_by_id(self, shorts_id: int) -> ShortsEntity:
        query = shorts_table.select().where(shorts_table.c.id == shorts_id)
        row = await database.fetch_one(query)
        return ShortsEntity(**dict(row)) if row else None

    async def find_all(self) -> List[ShortsEntity]:
        query = """
            SELECT S.* FROM Shorts AS S ORDER BY S.view_cnt DESC;
        """
        rows = await database.fetch_all(query)
        return [ShortsEntity(**dict(row)) for row in rows]

    async def find_all_with_random(self) -> List[ShortsEntity]:
        query = """
            SELECT S.* FROM Shorts AS S ORDER BY RAND();
        """
        rows = await database.fetch_all(query)
        return [ShortsEntity(**dict(row)) for row in rows]

    async def update_like_cnt(self, shorts_id: int, liked: bool):
        if liked:
            query = """
                UPDATE Shorts SET like_cnt = like_cnt - 1 WHERE id = :shorts_id;
            """
        else:
            query = """
                UPDATE Shorts SET like_cnt = like_cnt + 1 WHERE id = :shorts_id;
            """
        await database.execute(query, {'shorts_id': shorts_id})
        return {}

    async def update_dislike_cnt(self, shorts_id: int, disliked: bool):
        if disliked:
            query = """
                UPDATE Shorts SET dislike_cnt = dislike_cnt - 1 WHERE id = :shorts_id;
            """
        else:
            query = """
                UPDATE Shorts SET dislike_cnt = dislike_cnt + 1 WHERE id = :shorts_id;
            """
        await database.execute(query, {'shorts_id': shorts_id})
        return {}
