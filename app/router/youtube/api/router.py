# -*- coding: utf-8 -*-
import jwt
import random
from typing import Literal
from datetime import datetime
from fastapi import APIRouter, status, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from pydantic import BaseModel

from app.common.email import EmailSender
from app.common.response import verify_api_token, BadRequestException
from app.common.sms import SmsFactory, SmsEnum
from app.common.sns import SNSInfo
from app.database.mysql import UserEntity
from app.service.user import UserService
from config import Config, JsonConfig

router = APIRouter(prefix='/youtube/api')
templates = Jinja2Templates(directory=Config.TEMPLATES_DIR)


class SMSItem(BaseModel):
    phone: str


@router.get('/auth/sms')
async def auth_sms(code: str, current_user: UserEntity | None = Depends(verify_api_token)):
    if code != current_user.phone_validation_number:
        raise BadRequestException()

    current_user.phone_is_validation = 1
    await UserService.update_phone_is_validation(current_user)
    return {}


@router.post('/auth/sms')
async def auth_sms_send(item: SMSItem, current_user: UserEntity | None = Depends(verify_api_token)):
    code = int(random.random() * 1000000)

    sms_sender = SmsFactory(SmsEnum.TWILIO, item.phone)
    sms_sender.send(f'인증번호는 [{code}]입니다.')

    current_user.phone_number = item.phone
    current_user.phone_validation_number = str(code)
    current_user.phone_send_at = datetime.now()
    await UserService.update_phone(current_user)
    return {}


@router.get('/auth/email')
async def auth_email(code: str, current_user: UserEntity | None = Depends(verify_api_token)):
    if code != current_user.email_validation_number:
        raise BadRequestException()

    current_user.email_is_validation = 1
    await UserService.update_email_is_validation(current_user)
    return {}


@router.post('/auth/email')
async def auth_email_send(current_user: UserEntity | None = Depends(verify_api_token)):
    code = int(random.random() * 1000000)

    email_sender = EmailSender(current_user)
    email_sender.send('youtube', f'인증번호는 [{code}]입니다.')

    current_user.email_validation_number = str(code)
    await UserService.update_email(current_user)
    return {}


@router.get('/signout')
async def signout():
    if Config.APP_MODE == Config.APP_MODE_DEVELOPMENT:
        response = RedirectResponse(
            url='http://localhost:3000', status_code=status.HTTP_302_FOUND)
        response.delete_cookie('x-access-token')
    else:
        response = RedirectResponse(
            url='https://youtube.devmaker.kr', status_code=status.HTTP_302_FOUND)
        response.delete_cookie(
            key='x-access-token',
            domain='.devmaker.kr',
            path='/',
            secure=True,
            samesite='lax'
        )
    return response


@router.get('/callback/{provider}')
async def callback(provider: Literal['google', 'facebook', 'kakao', 'naver', 'github'], code: str):
    sns_info = SNSInfo(provider, code)
    email = sns_info.get_info().email

    user = await UserService.find_one_by_email(email)
    if not user:
        user = await UserService.create(UserEntity(
            email=email,
            provider=provider,
            created_at=datetime.now(),
            phone_number=None,
            phone_send_at=None,
            phone_validation_number=None,
        ))


    response = RedirectResponse(url='http://localhost:3000' if Config.APP_MODE == Config.APP_MODE_DEVELOPMENT else 'https://youtube.devmaker.kr', status_code=status.HTTP_302_FOUND)

    if Config.APP_MODE == Config.APP_MODE_DEVELOPMENT:
        response.set_cookie('x-access-token',
                            jwt.encode({'id': user.id}, JsonConfig.get_data('SECRET'), algorithm='HS256'),
                            httponly=True)
    else:
        response.set_cookie('x-access-token',
                            jwt.encode({'id': user.id}, JsonConfig.get_data('SECRET'), algorithm='HS256'),
                            domain='.devmaker.kr',
                            httponly=True,
                            secure=True)
    return response
