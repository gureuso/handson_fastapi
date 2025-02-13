# -*- coding: utf-8 -*-
from fastapi import APIRouter
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request

from config import Config

router = APIRouter(prefix='/youtube')
templates = Jinja2Templates(directory=Config.TEMPLATES_DIR)


@router.get('')
async def main(request: Request):
    return templates.TemplateResponse('youtube/index.html', {'request': request})


@router.get('/login')
async def login(request: Request):
    return templates.TemplateResponse('youtube/login.html', {'request': request})


@router.get('/shorts')
async def shorts(request: Request):
    return templates.TemplateResponse('youtube/shorts.html', {'request': request})


@router.get('/subscriptions')
async def subscriptions(request: Request):
    return templates.TemplateResponse('youtube/subscriptions.html', {'request': request})


