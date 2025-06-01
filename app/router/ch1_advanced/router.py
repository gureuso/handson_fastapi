# -*- coding: utf-8 -*-
from fastapi import APIRouter
from fastapi.templating import Jinja2Templates

from config import Config

router = APIRouter(prefix='/ch1/advanced')
templates = Jinja2Templates(directory=Config.TEMPLATES_DIR)


@router.get('')
async def main():
    return {'ping': 'pong'}
