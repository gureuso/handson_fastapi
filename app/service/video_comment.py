from typing import List

from app.database.mysql import database, VideoCommentEntity, video_comment_table


class VideoCommentService:
    @staticmethod
    async def create(video_comment_entity: VideoCommentEntity) -> VideoCommentEntity:
        query = video_comment_table.insert().values(
            parent_id=video_comment_entity.parent_id, content=video_comment_entity.content,
            video_id=video_comment_entity.video_id, user_id=video_comment_entity.user_id,
            created_at=video_comment_entity.created_at,
        )
        ai = await database.execute(query)
        video_comment_entity.id = ai
        return video_comment_entity

    @staticmethod
    async def find_one_by_id(video_comment_id: int) -> VideoCommentEntity:
        query = video_comment_table.select().where(video_comment_table.c.id == video_comment_id)
        row = await database.fetch_one(query)
        return VideoCommentEntity(**dict(row)) if row else None

    @staticmethod
    async def find_all(video_id: int) -> List[VideoCommentEntity]:
        query = """
            SELECT U.nickname, U.profile_image, VC.* FROM VideoComment AS VC 
                JOIN User AS U ON VC.user_id = U.id 
            WHERE VC.parent_id IS NULL AND VC.video_id = :video_id
            ORDER BY VC.is_fixed DESC, VC.created_at DESC;
        """
        rows = await database.fetch_all(query, {'video_id': video_id})
        return [VideoCommentEntity(**dict(row)) for row in rows]

    @staticmethod
    async def find_all_by_parent_id(video_id: int, comment_id: int) -> List[VideoCommentEntity]:
        query = """
            SELECT U.nickname, U.profile_image, VC.* FROM VideoComment AS VC 
                JOIN User AS U ON VC.user_id = U.id 
            WHERE VC.parent_id = :comment_id AND VC.video_id = :video_id 
            ORDER BY VC.created_at ASC;
        """
        rows = await database.fetch_all(query, {'comment_id': comment_id, 'video_id': video_id})
        return [VideoCommentEntity(**dict(row)) for row in rows]

    @staticmethod
    async def update_like_cnt(comment_id: int, liked: bool):
        if liked:
            query = """
                UPDATE VideoComment SET like_cnt = like_cnt - 1 WHERE id = :comment_id;
            """
        else:
            query = """
                UPDATE VideoComment SET like_cnt = like_cnt + 1 WHERE id = :comment_id;
            """
        await database.execute(query, {'comment_id': comment_id})
        return {}

    @staticmethod
    async def update_dislike_cnt(comment_id: int, disliked: bool):
        if disliked:
            query = """
                UPDATE VideoComment SET dislike_cnt = dislike_cnt - 1 WHERE id = :comment_id;
            """
        else:
            query = """
                UPDATE VideoComment SET dislike_cnt = dislike_cnt + 1 WHERE id = :comment_id;
            """
        await database.execute(query, {'comment_id': comment_id})
        return {}

    @staticmethod
    async def update_is_fixed(comment_id: int, is_fixed: bool):
        query = """
            UPDATE VideoComment SET is_fixed = :is_fixed WHERE id = :comment_id; 
        """
        await database.execute(query, {'comment_id': comment_id, 'is_fixed': is_fixed})
        return {}
