from app.database.mysql import database, ShortsCommentLikeEntity, shorts_comment_like_table, ShortsCommentLikeEnum


class ShortsCommentLikeService:
    @staticmethod
    async def create(shorts_comment_like_entity: ShortsCommentLikeEntity) -> ShortsCommentLikeEntity:
        query = shorts_comment_like_table.insert().values(
            kind=shorts_comment_like_entity.kind.value, shorts_id=shorts_comment_like_entity.shorts_id,
            user_id=shorts_comment_like_entity.user_id, created_at=shorts_comment_like_entity.created_at,
            comment_id=shorts_comment_like_entity.comment_id,
        )
        ai = await database.execute(query)
        shorts_comment_like_entity.id = ai
        return shorts_comment_like_entity

    @staticmethod
    async def find_one_by_id(shorts_comment_like_id: int) -> ShortsCommentLikeEntity:
        query = shorts_comment_like_table.select().where(shorts_comment_like_table.c.id == shorts_comment_like_id)
        row = await database.fetch_one(query)
        return ShortsCommentLikeEntity(**dict(row)) if row else None

    @staticmethod
    async def delete_by_user_id(comment_id: int, user_id: int, kind: ShortsCommentLikeEnum):
        query = """
            DELETE FROM ShortsCommentLike WHERE comment_id = :comment_id AND user_id = :user_id AND kind = :kind;
        """
        await database.execute(query, {'comment_id': comment_id, 'user_id': user_id, 'kind': kind.value})
        return {}

    @staticmethod
    async def find_one_by_liked(comment_id: int, user_id: int) -> dict:
        like_cnt_query = """
             SELECT COUNT(SCL.comment_id) AS cnt FROM ShortsCommentLike AS SCL 
             WHERE SCL.comment_id = :comment_id AND SCL.kind = :kind 
             GROUP BY SCL.comment_id;
         """
        like_cnt_row = await database.fetch_one(like_cnt_query,
                                                {'comment_id': comment_id, 'kind': ShortsCommentLikeEnum.LIKE.value})

        liked_query = """
            SELECT SCL.* FROM ShortsCommentLike AS SCL 
            WHERE SCL.comment_id = :comment_id AND SCL.kind = :kind AND SCL.user_id = :user_id;
        """
        liked_row = await database.fetch_one(liked_query, {'comment_id': comment_id, 'kind': ShortsCommentLikeEnum.LIKE.value,
                                                           'user_id': user_id})

        return {'cnt': like_cnt_row['cnt'] if like_cnt_row else 0, 'liked': True if liked_row else False}

    @staticmethod
    async def find_one_by_disliked(comment_id: int, user_id: int) -> dict:
        like_cnt_query = """
            SELECT COUNT(SCL.comment_id) AS cnt FROM ShortsCommentLike AS SCL 
            WHERE SCL.comment_id = :comment_id AND SCL.kind = :kind 
            GROUP BY SCL.comment_id;
        """
        like_cnt_row = await database.fetch_one(like_cnt_query,
                                                {'comment_id': comment_id, 'kind': ShortsCommentLikeEnum.DISLIKE.value})

        liked_query = """
            SELECT SCL.* FROM ShortsCommentLike AS SCL 
            WHERE SCL.comment_id = :comment_id AND SCL.kind = :kind AND SCL.user_id = :user_id;
        """
        liked_row = await database.fetch_one(liked_query, {'comment_id': comment_id, 'kind': ShortsCommentLikeEnum.DISLIKE.value,
                                                           'user_id': user_id})

        return {'cnt': like_cnt_row['cnt'] if like_cnt_row else 0, 'disliked': True if liked_row else False}
