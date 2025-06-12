from app.database.mysql import database, ShortsCommentLikeEntity, shorts_comment_like_table


class ShortsCommentLikeService:
    @staticmethod
    async def create(shorts_comment_like_entity: ShortsCommentLikeEntity) -> ShortsCommentLikeEntity:
        query = shorts_comment_like_table.insert().values(
            kind=shorts_comment_like_entity.kind, shortss_id=shorts_comment_like_entity.shortss_id,
            user_id=shorts_comment_like_entity.user_id, created_at=shorts_comment_like_entity.created_at,
        )
        ai = await database.execute(query)
        shorts_comment_like_entity.id = ai
        return shorts_comment_like_entity

    @staticmethod
    async def find_one_by_id(shorts_comment_like_id: int) -> ShortsCommentLikeEntity:
        query = shorts_comment_like_table.select().where(shorts_comment_like_table.c.id == shorts_comment_like_id)
        row = await database.fetch_one(query)
        return ShortsCommentLikeEntity(**dict(row)) if row else None
