from app.database.mysql import database, ShortsLikeEntity, shorts_like_table, ShortsLikeEnum


class ShortsLikeService:
    @staticmethod
    async def create(shorts_like_entity: ShortsLikeEntity) -> ShortsLikeEntity:
        query = shorts_like_table.insert().values(
            kind=shorts_like_entity.kind.value, shorts_id=shorts_like_entity.shorts_id,
            user_id=shorts_like_entity.user_id, created_at=shorts_like_entity.created_at,
        )
        ai = await database.execute(query)
        shorts_like_entity.id = ai
        return shorts_like_entity

    @staticmethod
    async def find_one_by_liked(shorts_id: int, user_id: int) -> dict:
        like_cnt_query = """
            SELECT COUNT(SL.shorts_id) AS cnt FROM ShortsLike AS SL WHERE shorts_id = :shorts_id AND kind = :kind GROUP BY SL.shorts_id
        """
        like_cnt_row = await database.fetch_one(like_cnt_query, {'shorts_id': shorts_id, 'kind': ShortsLikeEnum.LIKE.value})

        liked_query = """
            SELECT SL.* FROM ShortsLike AS SL WHERE shorts_id = :shorts_id AND kind = :kind AND user_id = :user_id
        """
        liked_row = await database.fetch_one(liked_query, {'shorts_id': shorts_id, 'kind': ShortsLikeEnum.LIKE.value,
                                                         'user_id': user_id})

        return {'cnt': like_cnt_row['cnt'] if like_cnt_row else 0, 'liked': True if liked_row else False}

    @staticmethod
    async def find_one_by_disliked(shorts_id: int, user_id: int) -> dict:
        like_cnt_query = """
            SELECT COUNT(SL.shorts_id) AS cnt FROM ShortsLike AS SL WHERE shorts_id = :shorts_id AND kind = :kind GROUP BY SL.shorts_id
        """
        like_cnt_row = await database.fetch_one(like_cnt_query, {'shorts_id': shorts_id, 'kind': ShortsLikeEnum.DISLIKE.value})

        liked_query = """
            SELECT SL.* FROM ShortsLike AS SL WHERE shorts_id = :shorts_id AND kind = :kind AND user_id = :user_id
        """
        liked_row = await database.fetch_one(liked_query, {'shorts_id': shorts_id, 'kind': ShortsLikeEnum.DISLIKE.value,
                                                           'user_id': user_id})

        return {'cnt': like_cnt_row['cnt'] if like_cnt_row else 0, 'disliked': True if liked_row else False}
