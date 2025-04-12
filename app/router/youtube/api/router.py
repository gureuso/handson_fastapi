# -*- coding: utf-8 -*-
import jwt
from typing import Literal
from datetime import datetime
from fastapi import APIRouter, status
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse

from app.common.sns import SNSInfo
from app.database.mysql import UserEntity
from app.service.user import UserService
from config import Config, JsonConfig

router = APIRouter(prefix='/youtube/api')
templates = Jinja2Templates(directory=Config.TEMPLATES_DIR)


@router.get('/callback/{provider}')
async def login_callback(provider: Literal['google', 'facebook', 'kakao', 'naver', 'github'], code: str):
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


    response = RedirectResponse(url='/youtube', status_code=status.HTTP_302_FOUND)

    response.set_cookie('x-access-token',
                        jwt.encode({'id': user.id}, JsonConfig.get_data('SECRET'), algorithm='HS256'),
                        httponly=True)
    return response
