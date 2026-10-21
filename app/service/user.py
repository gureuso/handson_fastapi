import random
import string
from datetime import datetime

from app.common.email import EmailSender
from app.common.response import BadRequestException
from app.common.sms import SmsFactory, SmsEnum
from app.database.mysql import UserEntity
from app.repository.user import UserRepository

PROFILE_IMAGES = [
    'https://gureuso.s3.ap-northeast-2.amazonaws.com/gomin/gomin_profile_02.png',
    'https://gureuso.s3.ap-northeast-2.amazonaws.com/gomin/gomin_profile_03.png',
    'https://gureuso.s3.ap-northeast-2.amazonaws.com/gomin/gomin_profile_04.png',
    'https://gureuso.s3.ap-northeast-2.amazonaws.com/gomin/gomin_profile_05.png',
    'https://gureuso.s3.ap-northeast-2.amazonaws.com/gomin/gomin_profile_06.png',
]


class UserService:
    def __init__(self):
        self.user_repository = UserRepository()

    async def verify_phone(self, user: UserEntity, code: str):
        if code != user.phone_validation_number:
            raise BadRequestException()

        user.phone_is_validation = 1
        await self.user_repository.update_phone_is_validation(user)

    async def send_phone_code(self, user: UserEntity, phone: str):
        code = int(random.random() * 1000000)

        sms_sender = SmsFactory(SmsEnum.TWILIO, phone)
        sms_sender.send(f'인증번호는 [{code}]입니다.')

        user.phone_number = phone
        user.phone_validation_number = str(code)
        user.phone_send_at = datetime.now()
        await self.user_repository.update_phone(user)

    async def verify_email(self, user: UserEntity, code: str):
        if code != user.email_validation_number:
            raise BadRequestException()

        user.email_is_validation = 1
        await self.user_repository.update_email_is_validation(user)

    async def send_email_code(self, user: UserEntity):
        code = int(random.random() * 1000000)

        email_sender = EmailSender(user)
        email_sender.send('youtube', f'인증번호는 [{code}]입니다.')

        user.email_validation_number = str(code)
        await self.user_repository.update_email(user)

    async def find_or_create_by_email(self, email: str, provider: str) -> UserEntity:
        user = await self.user_repository.find_one_by_email(email)
        if user:
            return user

        nickname = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))
        return await self.user_repository.create(UserEntity(
            email=email,
            provider=provider,
            created_at=datetime.now(),
            phone_number=None,
            phone_send_at=None,
            phone_validation_number=None,
            phone_is_validation=0,
            email_validation_number=None,
            email_is_validation=0,
            profile_image=PROFILE_IMAGES[random.randint(0, len(PROFILE_IMAGES) - 1)],
            nickname=nickname,
        ))
