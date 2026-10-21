# -*- coding: utf-8 -*-
import jwt
from typing import Literal
from datetime import datetime, timedelta
from fastapi import APIRouter, status, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from pydantic import BaseModel

from app.common.response import verify_api_token
from app.common.sns import SNSInfo
from app.database.mysql import UserEntity
from app.service.user import UserService
from config import Config, JsonConfig

router = APIRouter(prefix='/youtube/api')
templates = Jinja2Templates(directory=Config.TEMPLATES_DIR)


class SMSItem(BaseModel):
    phone: str


class TokenItem(BaseModel):
    token: str


@router.get('/auth/sms')
async def auth_sms(code: str, current_user: UserEntity | None = Depends(verify_api_token), user_service: UserService = Depends()):
    await user_service.verify_phone(current_user, code)
    return {}


@router.post('/auth/sms')
async def auth_sms_send(item: SMSItem, current_user: UserEntity | None = Depends(verify_api_token), user_service: UserService = Depends()):
    await user_service.send_phone_code(current_user, item.phone)
    return {}


@router.get('/auth/email')
async def auth_email(code: str, current_user: UserEntity | None = Depends(verify_api_token), user_service: UserService = Depends()):
    await user_service.verify_email(current_user, code)
    return {}


@router.post('/auth/email')
async def auth_email_send(current_user: UserEntity | None = Depends(verify_api_token), user_service: UserService = Depends()):
    await user_service.send_email_code(current_user)
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
            domain='youtube.devmaker.kr',
            secure=True,
        )
    return response


@router.get('/callback/{provider}')
async def callback(provider: Literal['google', 'facebook', 'kakao', 'naver', 'github'], code: str, user_service: UserService = Depends()):
    sns_info = SNSInfo(provider, code)
    email = sns_info.get_info().email

    user = await user_service.find_or_create_by_email(email, provider)

    response = RedirectResponse(
        url='http://localhost:3000' if Config.APP_MODE == Config.APP_MODE_DEVELOPMENT else 'https://youtube.devmaker.kr',
        status_code=status.HTTP_302_FOUND
    )
    new_token = jwt.encode({'id': user.id, 'exp': datetime.utcnow() + timedelta(hours=1)}, JsonConfig.get_data('SECRET'), algorithm='HS256')
    if Config.APP_MODE == Config.APP_MODE_DEVELOPMENT:
        response.set_cookie('x-access-token', new_token, httponly=True)
    else:
        response.set_cookie('x-access-token', new_token, domain='youtube.devmaker.kr', httponly=True, secure=True)
    return response
