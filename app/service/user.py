from app.database.mysql import database, UserEntity, user_table


class UserService:
    @staticmethod
    async def create(user_entity: UserEntity) -> UserEntity:
        query = user_table.insert().values(email=user_entity.email, provider=user_entity.provider,
                                           created_at=user_entity.created_at, phone_number=user_entity.phone_number,
                                           phone_validation_number=user_entity.phone_validation_number,
                                           phone_send_at=user_entity.phone_send_at)
        ai = await database.execute(query)
        user_entity.id = ai
        return user_entity

    @staticmethod
    async def find_one_by_id(user_id: int):
        query = user_table.select().where(user_table.c.id == user_id)
        row = await database.fetch_one(query)
        return UserEntity(**dict(row)) if row else None

    @staticmethod
    async def find_one_by_email(email: str):
        query = user_table.select().where(user_table.c.email == email)
        row = await database.fetch_one(query)
        return UserEntity(**dict(row)) if row else None

    @staticmethod
    async def delete_by_id(user_id: int):
        query = """
            DELETE FROM User WHERE id = :user_id
        """
        await database.execute(query, {'user_id': user_id})
        return {}
