# -*- coding: utf-8 -*-
from fastapi import APIRouter
from fastapi.templating import Jinja2Templates

from app.common.response import NotFoundException, BadRequestException, PermissionDeniedException
from config import Config

router = APIRouter(prefix='/ch4')
templates = Jinja2Templates(directory=Config.TEMPLATES_DIR)


@router.get('/404')
async def ch4_404():
    raise NotFoundException()


@router.get('/403')
async def ch4_403():
    raise PermissionDeniedException()


@router.get('/400')
async def ch4_400():
    raise BadRequestException()
