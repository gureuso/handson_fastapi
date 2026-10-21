from app.database.mysql import database, UserEntity, user_table


class UserRepository:
    async def create(self, user_entity: UserEntity) -> UserEntity:
        query = user_table.insert().values(
            email=user_entity.email, provider=user_entity.provider,
            created_at=user_entity.created_at, phone_number=user_entity.phone_number,
            phone_validation_number=user_entity.phone_validation_number,
            phone_send_at=user_entity.phone_send_at,
            email_validation_number=user_entity.email_validation_number,
            profile_image=user_entity.profile_image,
            nickname=user_entity.nickname,
            email_is_validation=user_entity.email_is_validation,
        )
        ai = await database.execute(query)
        user_entity.id = ai
        return user_entity

    async def find_one_by_id(self, user_id: int):
        query = user_table.select().where(user_table.c.id == user_id)
        row = await database.fetch_one(query)
        return UserEntity(**dict(row)) if row else None

    async def find_one_by_email(self, email: str):
        query = user_table.select().where(user_table.c.email == email)
        row = await database.fetch_one(query)
        return UserEntity(**dict(row)) if row else None

    async def delete_by_id(self, user_id: int):
        query = """
                DELETE FROM User WHERE id = :user_id
            """
        await database.execute(query, {'user_id': user_id})
        return {}

    async def update_phone(self, user: UserEntity):
        query = """
            UPDATE User 
            SET phone_number = :phone_number, phone_validation_number = :phone_validation_number, 
                phone_send_at = :phone_send_at 
            WHERE id = :user_id
        """
        await database.execute(query, {
            'phone_number': user.phone_number, 'phone_validation_number': user.phone_validation_number,
            'phone_send_at': user.phone_send_at, 'user_id': user.id
        })
        return {}

    async def update_email(self, user: UserEntity):
        query = """
            UPDATE User 
            SET email_validation_number = :email_validation_number 
            WHERE id = :user_id
        """
        await database.execute(query, {'email_validation_number': user.email_validation_number, 'user_id': user.id})
        return {}

    async def update_email_is_validation(self, user: UserEntity):
        query = """
            UPDATE User 
            SET email_is_validation = :email_is_validation 
            WHERE id = :user_id
        """
        await database.execute(query, {'email_is_validation': user.email_is_validation, 'user_id': user.id})
        return {}

    async def update_phone_is_validation(self, user: UserEntity):
        query = """
                UPDATE User 
                SET phone_is_validation = :phone_is_validation 
                WHERE id = :user_id
            """
        await database.execute(query, {'phone_is_validation': user.phone_is_validation, 'user_id': user.id})
        return {}
