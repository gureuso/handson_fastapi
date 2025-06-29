from app.database.mysql import database, VideoLikeEntity, video_like_table, VideoLikeEnum


class VideoLikeService:
    @staticmethod
    async def create(video_like_entity: VideoLikeEntity) -> VideoLikeEntity:
        query = video_like_table.insert().values(
            kind=video_like_entity.kind.value, video_id=video_like_entity.video_id,
            user_id=video_like_entity.user_id, created_at=video_like_entity.created_at,
        )
        ai = await database.execute(query)
        video_like_entity.id = ai
        return video_like_entity

    @staticmethod
    async def delete_by_user_id(video_id: int, user_id: int, kind: VideoLikeEnum):
        query = """
            DELETE FROM VideoLike WHERE video_id = :video_id AND user_id = :user_id AND kind = :kind;
        """
        await database.execute(query, {'video_id': video_id, 'user_id': user_id, 'kind': kind.value})
        return {}

    @staticmethod
    async def find_one_by_liked(video_id: int, user_id: int) -> dict:
        like_cnt_query = """
            SELECT COUNT(VL.video_id) AS cnt FROM VideoLike AS VL WHERE video_id = :video_id AND kind = :kind GROUP BY VL.video_id
        """
        like_cnt_row = await database.fetch_one(like_cnt_query, {'video_id': video_id, 'kind': VideoLikeEnum.LIKE.value})

        liked_query = """
            SELECT VL.* FROM VideoLike AS VL WHERE video_id = :video_id AND kind = :kind AND user_id = :user_id
        """
        liked_row = await database.fetch_one(liked_query, {'video_id': video_id, 'kind': VideoLikeEnum.LIKE.value,
                                                         'user_id': user_id})

        return {'cnt': like_cnt_row['cnt'] if like_cnt_row else 0, 'liked': True if liked_row else False}

    @staticmethod
    async def find_one_by_disliked(video_id: int, user_id: int) -> dict:
        like_cnt_query = """
            SELECT COUNT(VL.video_id) AS cnt FROM VideoLike AS VL WHERE video_id = :video_id AND kind = :kind GROUP BY VL.video_id
        """
        like_cnt_row = await database.fetch_one(like_cnt_query, {'video_id': video_id, 'kind': VideoLikeEnum.DISLIKE.value})

        liked_query = """
            SELECT VL.* FROM VideoLike AS VL WHERE video_id = :video_id AND kind = :kind AND user_id = :user_id
        """
        liked_row = await database.fetch_one(liked_query, {'video_id': video_id, 'kind': VideoLikeEnum.DISLIKE.value,
                                                           'user_id': user_id})

        return {'cnt': like_cnt_row['cnt'] if like_cnt_row else 0, 'disliked': True if liked_row else False}
