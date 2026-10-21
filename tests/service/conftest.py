from datetime import datetime

import pytest

from app.database.mysql import UserEntity


@pytest.fixture
def user() -> UserEntity:
    return UserEntity(
        id=1, email='test@gmail.com', provider='google', phone_number=None, phone_validation_number=None,
        phone_send_at=None, phone_is_validation=0, email_validation_number=None, email_is_validation=0,
        nickname='TESTER', profile_image='https://example.com/profile.png', created_at=datetime.now(),
    )
