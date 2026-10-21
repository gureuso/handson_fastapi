from fastapi import APIRouter, Depends
from fastapi.templating import Jinja2Templates

from app.common.response import verify_api_token
from app.database.mysql import UserEntity
from app.service.channel import ChannelService
from config import Config

router = APIRouter(prefix='/youtube/api/channel')
templates = Jinja2Templates(directory=Config.TEMPLATES_DIR)


@router.get('/{channel_id}')
async def get_channel(channel_id: int, current_user: UserEntity = Depends(verify_api_token), channel_service: ChannelService = Depends()):
    return await channel_service.get_channel(channel_id, current_user)


@router.post('/{channel_id}/subscription')
async def subscription(channel_id: int, current_user: UserEntity = Depends(verify_api_token), channel_service: ChannelService = Depends()):
    return {'subscription': await channel_service.toggle_subscription(channel_id, current_user)}
