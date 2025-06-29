from app.database.mysql import database, VideoCommentLikeEntity, video_comment_like_table, VideoCommentLikeEnum


class VideoCommentLikeService:
    @staticmethod
    async def create(video_comment_like_entity: VideoCommentLikeEntity) -> VideoCommentLikeEntity:
        query = video_comment_like_table.insert().values(
            kind=video_comment_like_entity.kind.value, video_id=video_comment_like_entity.video_id,
            user_id=video_comment_like_entity.user_id, created_at=video_comment_like_entity.created_at,
            comment_id=video_comment_like_entity.comment_id,
        )
        ai = await database.execute(query)
        video_comment_like_entity.id = ai
        return video_comment_like_entity

    @staticmethod
    async def find_one_by_id(video_comment_like_id: int) -> VideoCommentLikeEntity:
        query = video_comment_like_table.select().where(video_comment_like_table.c.id == video_comment_like_id)
        row = await database.fetch_one(query)
        return VideoCommentLikeEntity(**dict(row)) if row else None

    @staticmethod
    async def delete_by_user_id(comment_id: int, user_id: int, kind: VideoCommentLikeEnum):
        query = """
            DELETE FROM VideoCommentLike WHERE comment_id = :comment_id AND user_id = :user_id AND kind = :kind;
        """
        await database.execute(query, {'comment_id': comment_id, 'user_id': user_id, 'kind': kind.value})
        return {}

    @staticmethod
    async def find_one_by_liked(comment_id: int, user_id: int) -> dict:
        like_cnt_query = """
             SELECT COUNT(VCL.comment_id) AS cnt FROM VideoCommentLike AS VCL 
             WHERE VCL.comment_id = :comment_id AND VCL.kind = :kind 
             GROUP BY VCL.comment_id;
         """
        like_cnt_row = await database.fetch_one(like_cnt_query,
                                                {'comment_id': comment_id, 'kind': VideoCommentLikeEnum.LIKE.value})

        liked_query = """
            SELECT VCL.* FROM VideoCommentLike AS VCL 
            WHERE VCL.comment_id = :comment_id AND VCL.kind = :kind AND VCL.user_id = :user_id;
        """
        liked_row = await database.fetch_one(liked_query, {'comment_id': comment_id, 'kind': VideoCommentLikeEnum.LIKE.value,
                                                           'user_id': user_id})

        return {'cnt': like_cnt_row['cnt'] if like_cnt_row else 0, 'liked': True if liked_row else False}

    @staticmethod
    async def find_one_by_disliked(comment_id: int, user_id: int) -> dict:
        like_cnt_query = """
            SELECT COUNT(VCL.comment_id) AS cnt FROM VideoCommentLike AS VCL 
            WHERE VCL.comment_id = :comment_id AND VCL.kind = :kind 
            GROUP BY VCL.comment_id;
        """
        like_cnt_row = await database.fetch_one(like_cnt_query,
                                                {'comment_id': comment_id, 'kind': VideoCommentLikeEnum.DISLIKE.value})

        liked_query = """
            SELECT VCL.* FROM VideoCommentLike AS VCL 
            WHERE VCL.comment_id = :comment_id AND VCL.kind = :kind AND VCL.user_id = :user_id;
        """
        liked_row = await database.fetch_one(liked_query, {'comment_id': comment_id, 'kind': VideoCommentLikeEnum.DISLIKE.value,
                                                           'user_id': user_id})

        return {'cnt': like_cnt_row['cnt'] if like_cnt_row else 0, 'disliked': True if liked_row else False}
