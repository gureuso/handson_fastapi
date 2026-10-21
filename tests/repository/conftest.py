import os
from datetime import datetime

import pytest
import pytest_asyncio

from app.database.mysql import database, UserEntity
from app.repository.user import UserRepository
from config import Config
from tests.repository.utils import random_name


class Cleanup:
    # 테스트가 만든 행만 기록해 두었다가 테스트가 끝나면 역순으로 삭제
    def __init__(self):
        self.rows: list[tuple[str, int]] = []

    def add(self, table: str, row_id: int):
        self.rows.append((table, row_id))
        return row_id

    async def run(self):
        for table, row_id in reversed(self.rows):
            await database.execute(f'DELETE FROM {table} WHERE id = :id', {'id': row_id})


@pytest_asyncio.fixture
async def cleanup():
    # 실제 DB에 쓰는 테스트라 운영 모드에서는 RUN_DB_TESTS=1 일 때만 실행
    if Config.APP_MODE == Config.APP_MODE_PRODUCTION and os.environ.get('RUN_DB_TESTS') != '1':
        pytest.skip('APP_MODE가 production이면 RUN_DB_TESTS=1 일 때만 repository 테스트를 실행합니다')

    await database.connect()
    c = Cleanup()
    try:
        yield c
    finally:
        await c.run()
        await database.disconnect()


@pytest_asyncio.fixture
async def user(cleanup) -> UserEntity:
    user = await UserRepository().create(UserEntity(
        email=f'{random_name()}@test.com', provider='google', phone_number=None, phone_validation_number=None,
        phone_send_at=None, phone_is_validation=0, email_validation_number=None, email_is_validation=0,
        nickname=random_name(), profile_image='https://example.com/profile.png', created_at=datetime.now(),
    ))
    cleanup.add('User', user.id)
    return user
