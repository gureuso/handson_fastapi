# -*- coding: utf-8 -*-
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import FileResponse
from fastapi.exceptions import HTTPException
from fastapi.websockets import WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

from app.common.register import BlueprintRegister
from app.common.response import PermissionDeniedException, error, NotFoundException, BadRequestException, verify_token
from app.common.websocket import WsConnectionManager
from app.database.cache import Cache
from app.database.mysql import database
from config import Config

@asynccontextmanager
async def lifespan(app: FastAPI):
    await database.connect()
    # scheduler.start()
    yield
    await database.disconnect()
app = FastAPI(docs_url='/A9buAGuA', redoc_url='/AA9Wbe2A', openapi_url='/AAWksi3A', lifespan=lifespan)
BlueprintRegister(app, 'app.router', 'router').register()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount('/static', StaticFiles(directory=Config.STATIC_DIR), name='static')
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="고민들어줌 서버",
        version="1.0.0",
        description="고민들어줌 서버 스웨거 입니다.",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "XAccessTokenAuth": {
            "type": "apiKey",
            "name": "x-access-token",
            "in": "header",
        }
    }
    openapi_schema["security"] = [{"XAccessTokenAuth": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

templates = Jinja2Templates(directory=Config.TEMPLATES_DIR)

manager = WsConnectionManager()

@app.websocket('/ws/chat/{room}')
async def chat_endpoint(websocket: WebSocket, room: str):
    await manager.connect(websocket, room)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(f'{data}', room)
            await Cache.rpush(f'gomin_room_{room}', data)
    except WebSocketDisconnect:
        manager.disconnect(websocket, room)


@app.exception_handler(404)
async def page_not_found_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, content=error(exc.status_code * 100))
    # return templates.TemplateResponse(f'{exc.status_code}.html', {'request': request, 'current_user': current_user})


@app.exception_handler(BadRequestException)
async def bad_request_exception_handler(request: Request, exc: BadRequestException):
    return JSONResponse(status_code=400, content=error(40000))


@app.exception_handler(PermissionDeniedException)
async def permission_denied_exception_handler(request: Request, exc: PermissionDeniedException):
    return JSONResponse(status_code=403, content=error(40300))


@app.exception_handler(NotFoundException)
async def not_found_exception_handler(request: Request, exc: NotFoundException):
    return JSONResponse(status_code=404, content=error(40400))


@app.exception_handler(Exception)
async def exception_handler(request: Request, exc: Exception):
    print(exc)
    return JSONResponse(status_code=500, content=error(50000))


@app.get('/')
async def main():
    return {'ping': 'pong'}


@app.get('/favicon.ico', include_in_schema=False)
async def favicon():
    return FileResponse(f'{Config.STATIC_DIR}/favicon.ico')
