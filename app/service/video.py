from app.database.mysql import database, VideoEntity, video_table


class VideoService:
    @staticmethod
    async def create(video_entity: VideoEntity) -> VideoEntity:
        query = video_table.insert().values(
            channel_id=video_entity.channel_id, title=video_entity.title,
            thumbnail=video_entity.thumbnail, content=video_entity.content,
            view_cnt=video_entity.view_cnt, created_at=video_entity.created_at,
        )
        ai = await database.execute(query)
        video_entity.id = ai
        return video_entity

    @staticmethod
    async def find_one_by_id(video_id: int):
        query = video_table.select().where(video_table.c.id == video_id)
        row = await database.fetch_one(query)
        return VideoEntity(**dict(row)) if row else None

    @staticmethod
    async def find_all():
        query = """
            SELECT V.*, C.name, C.image FROM Video AS V 
            JOIN Channel AS C ON V.channel_id = C.id 
            ORDER BY V.view_cnt DESC;
        """
        rows = await database.fetch_all(query)
        return [VideoEntity(**dict(row)) for row in rows]

    @staticmethod
    async def update_like_cnt(video_id: int, liked: bool):
        if liked:
            query = """
                UPDATE Video SET like_cnt = like_cnt - 1 WHERE id = :video_id; \
            """
        else:
            query = """
                UPDATE Video SET like_cnt = like_cnt + 1 WHERE id = :video_id;
            """
        await database.execute(query, {'video_id': video_id})
        return {}

    @staticmethod
    async def update_dislike_cnt(video_id: int, disliked: bool):
        if disliked:
            query = """
                UPDATE Video SET dislike_cnt = dislike_cnt - 1 WHERE id = :video_id;
            """
        else:
            query = """
                UPDATE Video SET dislike_cnt = dislike_cnt + 1 WHERE id = :video_id;
            """
        await database.execute(query, {'video_id': video_id})
        return {}
