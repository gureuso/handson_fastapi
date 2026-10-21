from unittest.mock import MagicMock

import pytest

from app.common.response import BadRequestException
from app.service import user as user_module
from app.service.user import UserService, PROFILE_IMAGES
from tests.service.utils import mock_repositories


@pytest.fixture
def service() -> UserService:
    return mock_repositories(UserService())


@pytest.mark.asyncio
async def test_verify_phone(service, user):
    user.phone_validation_number = '123456'

    with pytest.raises(BadRequestException):
        await service.verify_phone(user, '000000')
    service.user_repository.update_phone_is_validation.assert_not_awaited()

    await service.verify_phone(user, '123456')
    assert user.phone_is_validation == 1
    service.user_repository.update_phone_is_validation.assert_awaited_once_with(user)


@pytest.mark.asyncio
async def test_send_phone_code(service, user, monkeypatch):
    sms_factory = MagicMock()
    monkeypatch.setattr(user_module, 'SmsFactory', sms_factory)

    await service.send_phone_code(user, '01012345678')

    sms_factory.return_value.send.assert_called_once()
    assert user.phone_validation_number in sms_factory.return_value.send.call_args.args[0]
    assert user.phone_number == '01012345678'
    assert user.phone_send_at is not None
    service.user_repository.update_phone.assert_awaited_once_with(user)


@pytest.mark.asyncio
async def test_verify_email(service, user):
    user.email_validation_number = '654321'

    with pytest.raises(BadRequestException):
        await service.verify_email(user, '000000')
    service.user_repository.update_email_is_validation.assert_not_awaited()

    await service.verify_email(user, '654321')
    assert user.email_is_validation == 1
    service.user_repository.update_email_is_validation.assert_awaited_once_with(user)


@pytest.mark.asyncio
async def test_send_email_code(service, user, monkeypatch):
    email_sender = MagicMock()
    monkeypatch.setattr(user_module, 'EmailSender', email_sender)

    await service.send_email_code(user)

    email_sender.assert_called_once_with(user)
    assert user.email_validation_number in email_sender.return_value.send.call_args.args[1]
    service.user_repository.update_email.assert_awaited_once_with(user)


@pytest.mark.asyncio
async def test_find_or_create_by_email_existing_user(service, user):
    service.user_repository.find_one_by_email.return_value = user

    result = await service.find_or_create_by_email(user.email, 'google')

    assert result is user
    service.user_repository.create.assert_not_awaited()


@pytest.mark.asyncio
async def test_find_or_create_by_email_new_user(service):
    service.user_repository.find_one_by_email.return_value = None
    service.user_repository.create.side_effect = lambda entity: entity

    result = await service.find_or_create_by_email('new@gmail.com', 'kakao')

    service.user_repository.create.assert_awaited_once()
    assert result.email == 'new@gmail.com'
    assert result.provider == 'kakao'
    assert result.profile_image in PROFILE_IMAGES
    assert len(result.nickname) == 8
    assert result.phone_is_validation == 0 and result.email_is_validation == 0
