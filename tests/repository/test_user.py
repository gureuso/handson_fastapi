from datetime import datetime

import pytest

from app.repository.user import UserRepository


@pytest.mark.asyncio
async def test_find(user):
    repository = UserRepository()

    assert (await repository.find_one_by_id(user.id)).email == user.email
    assert (await repository.find_one_by_email(user.email)).id == user.id
    assert await repository.find_one_by_email('not-exists@test.com') is None


@pytest.mark.asyncio
async def test_update(user):
    repository = UserRepository()

    user.phone_number = '01012345678'
    user.phone_validation_number = '123456'
    user.phone_send_at = datetime(2025, 5, 1, 11, 11, 11)
    await repository.update_phone(user)

    user.email_validation_number = '654321'
    await repository.update_email(user)

    user.phone_is_validation = 1
    await repository.update_phone_is_validation(user)

    user.email_is_validation = 1
    await repository.update_email_is_validation(user)

    found = await repository.find_one_by_id(user.id)
    assert found.phone_number == '01012345678'
    assert found.phone_validation_number == '123456'
    assert found.phone_send_at == datetime(2025, 5, 1, 11, 11, 11)
    assert found.email_validation_number == '654321'
    assert found.phone_is_validation == 1
    assert found.email_is_validation == 1


@pytest.mark.asyncio
async def test_delete_by_id(user):
    repository = UserRepository()

    await repository.delete_by_id(user.id)
    assert await repository.find_one_by_id(user.id) is None
