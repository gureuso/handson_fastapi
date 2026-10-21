from typing import List

from app.database.mysql import database, ShortsCommentEntity, shorts_comment_table


class ShortsCommentRepository:
    async def create(self, shorts_comment_entity: ShortsCommentEntity) -> ShortsCommentEntity:
        query = shorts_comment_table.insert().values(
            parent_id=shorts_comment_entity.parent_id, content=shorts_comment_entity.content,
            shorts_id=shorts_comment_entity.shorts_id, user_id=shorts_comment_entity.user_id,
            created_at=shorts_comment_entity.created_at,
        )
        ai = await database.execute(query)
        shorts_comment_entity.id = ai
        return shorts_comment_entity

    async def find_one_by_id(self, shorts_comment_id: int) -> ShortsCommentEntity:
        query = shorts_comment_table.select().where(shorts_comment_table.c.id == shorts_comment_id)
        row = await database.fetch_one(query)
        return ShortsCommentEntity(**dict(row)) if row else None

    async def find_all(self, shorts_id: int) -> List[ShortsCommentEntity]:
        query = """
            SELECT U.nickname, U.profile_image, SC.* FROM ShortsComment AS SC 
                JOIN User AS U ON SC.user_id = U.id 
            WHERE SC.parent_id IS NULL AND SC.shorts_id = :shorts_id
            ORDER BY SC.created_at DESC;
        """
        rows = await database.fetch_all(query, {'shorts_id': shorts_id})
        return [ShortsCommentEntity(**dict(row)) for row in rows]

    async def find_all_by_parent_id(self, shorts_id: int, comment_id: int) -> List[ShortsCommentEntity]:
        query = """
            SELECT U.nickname, U.profile_image, SC.* FROM ShortsComment AS SC 
                JOIN User AS U ON SC.user_id = U.id 
            WHERE SC.parent_id = :comment_id AND SC.shorts_id = :shorts_id 
            ORDER BY SC.created_at ASC;
        """
        rows = await database.fetch_all(query, {'comment_id': comment_id, 'shorts_id': shorts_id})
        return [ShortsCommentEntity(**dict(row)) for row in rows]

    async def update_like_cnt(self, comment_id: int, liked: bool):
        if liked:
            query = """
                UPDATE ShortsComment SET like_cnt = like_cnt - 1 WHERE id = :comment_id;
            """
        else:
            query = """
                UPDATE ShortsComment SET like_cnt = like_cnt + 1 WHERE id = :comment_id;
            """
        await database.execute(query, {'comment_id': comment_id})
        return {}

    async def update_dislike_cnt(self, comment_id: int, disliked: bool):
        if disliked:
            query = """
                UPDATE ShortsComment SET dislike_cnt = dislike_cnt - 1 WHERE id = :comment_id;
            """
        else:
            query = """
                UPDATE ShortsComment SET dislike_cnt = dislike_cnt + 1 WHERE id = :comment_id;
            """
        await database.execute(query, {'comment_id': comment_id})
        return {}