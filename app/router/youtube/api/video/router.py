# -*- coding: utf-8 -*-
from fastapi import APIRouter, Depends
from fastapi.templating import Jinja2Templates

from app.common.response import verify_api_token
from app.database.mysql import UserEntity
from app.service.shorts import ShortsService
from app.service.tag import TagService
from app.service.video import VideoService
from config import Config

router = APIRouter(prefix='/youtube/api/videos')
templates = Jinja2Templates(directory=Config.TEMPLATES_DIR)


@router.get('')
async def find_video_list(current_user: UserEntity | None = Depends(verify_api_token)):
    tags = await TagService.find_unique_tag()
    videos = await VideoService.find_all()
    shorts = await ShortsService.find_all()
    return {'tags': tags, 'videos': videos, 'shorts': shorts}
