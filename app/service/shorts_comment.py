from typing import List

from app.database.mysql import database, ShortsCommentEntity, shorts_comment_table


class ShortsCommentService:
    @staticmethod
    async def create(shorts_comment_entity: ShortsCommentEntity) -> ShortsCommentEntity:
        query = shorts_comment_table.insert().values(
            parent_id=shorts_comment_entity.parent_id, content=shorts_comment_entity.content,
            shorts_id=shorts_comment_entity.shorts_id, user_id=shorts_comment_entity.user_id,
            created_at=shorts_comment_entity.created_at,
        )
        ai = await database.execute(query)
        shorts_comment_entity.id = ai
        return shorts_comment_entity

    @staticmethod
    async def find_one_by_id(shorts_comment_id: int) -> ShortsCommentEntity:
        query = shorts_comment_table.select().where(shorts_comment_table.c.id == shorts_comment_id)
        row = await database.fetch_one(query)
        return ShortsCommentEntity(**dict(row)) if row else None
