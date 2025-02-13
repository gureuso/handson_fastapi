# -*- coding: utf-8 -*-
import asyncio
from typing import Union
from fastapi import APIRouter
from fastapi.templating import Jinja2Templates

from config import Config

router = APIRouter(prefix='/ch5')
templates = Jinja2Templates(directory=Config.TEMPLATES_DIR)


def add(x: Union[int, float], y: int) -> float:
    return x + y


@router.get('/list')
async def ch5_list(offset: int = 0, limit: int = 10):
    return {'offset': offset, 'limit': limit}


@router.get('/async_1')
async def ch5_async_1():
    await asyncio.sleep(2)
    print(1)
    return {}


@router.get('/async_2')
async def ch5_async_2():
    await asyncio.sleep(1)
    print(2)
    return {}
