from datetime import datetime
from fastapi import APIRouter, Depends
from fastapi.templating import Jinja2Templates

from app.common.response import verify_api_token
from app.database.mysql import UserEntity, ChannelSubscriptionEntity
from app.service.channel import ChannelService
from app.service.channel_subscription import ChannelSubscriptionService
from config import Config

router = APIRouter(prefix='/youtube/api/channel')
templates = Jinja2Templates(directory=Config.TEMPLATES_DIR)


@router.get('/{channel_id}')
async def get_channel(channel_id: int, current_user: UserEntity | None = Depends(verify_api_token)):
    sub = await ChannelSubscriptionService.find_one_by_id(channel_id, current_user.id)
    channel = await ChannelService.find_one_by_id(channel_id)
    return {'subscription': sub, 'channel': channel}


@router.post('/{channel_id}/subscription')
async def subscription(channel_id: int, current_user: UserEntity | None = Depends(verify_api_token)):
    sub = await ChannelSubscriptionService.find_one_by_id(channel_id, current_user.id)
    if sub:
        await ChannelSubscriptionService.delete(channel_id, current_user.id)
        return {'subscription': False}
    else:
        await ChannelSubscriptionService.create(ChannelSubscriptionEntity(
            channel_id=channel_id, user_id=current_user.id,
            created_at=datetime.now(),
        ))
        return {'subscription': True}
