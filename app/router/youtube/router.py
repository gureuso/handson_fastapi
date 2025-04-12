# -*- coding: utf-8 -*-
from fastapi import APIRouter, Depends, status
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from fastapi.responses import RedirectResponse

from app.common.response import verify_api_token
from app.database.mysql import UserEntity
from config import Config, JsonConfig

router = APIRouter(prefix='/youtube')
templates = Jinja2Templates(directory=Config.TEMPLATES_DIR)


@router.get('')
async def main(request: Request, current_user: UserEntity | None = Depends(verify_api_token)):
    return templates.TemplateResponse('youtube/index.html', {'request': request, 'current_user': current_user})


@router.get('/login')
async def login(request: Request, current_user: UserEntity | None = Depends(verify_api_token)):
    if current_user:
        return RedirectResponse('/youtube')

    return templates.TemplateResponse(
        'youtube/login.html',
        {
            'request': request, 'GOOGLE_CLIENT_ID': JsonConfig.get_data('GOOGLE_CLIENT_ID'),
            'current_user': current_user, 'KAKAO_CLIENT_ID': JsonConfig.get_data('KAKAO_CLIENT_ID'),
            'GITHUB_CLIENT_ID': JsonConfig.get_data('GITHUB_CLIENT_ID'),
        }
    )


@router.get('/logout')
async def logout():
    response = RedirectResponse(url='/youtube', status_code=status.HTTP_302_FOUND)
    response.set_cookie('x-access-token', '', httponly=True)
    return response


@router.get('/shorts')
async def shorts(request: Request, current_user: UserEntity | None = Depends(verify_api_token)):
    return templates.TemplateResponse('youtube/shorts.html', {'request': request, 'current_user': current_user})


@router.get('/subscriptions')
async def subscriptions(request: Request, current_user: UserEntity | None = Depends(verify_api_token)):
    return templates.TemplateResponse('youtube/subscriptions.html', {'request': request, 'current_user': current_user})
