# -*- coding: utf-8 -*-
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import FileResponse
from fastapi.exceptions import HTTPException, ResponseValidationError, RequestValidationError
from fastapi.websockets import WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

from app.common.register import APIRouterRegister
from app.common.response import PermissionDeniedException, error, NotFoundException, BadRequestException
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


security = HTTPBasic()
def doc_auth(credentials: HTTPBasicCredentials = Depends(security)):
    if credentials.username != 'admin' or credentials.password != '1234':
        raise HTTPException(
            status_code=401,
            detail='Incorrect username or password',
            headers={'WWW-Authenticate': 'Basic'},
        )

app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None, lifespan=lifespan)
APIRouterRegister(app, 'app.router', 'router').register()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)
app.mount('/static', StaticFiles(directory=Config.STATIC_DIR), name='static')
templates = Jinja2Templates(directory=Config.TEMPLATES_DIR)
manager = WsConnectionManager()


@app.websocket('/ws/chat/{room}')
async def chat_endpoint(websocket: WebSocket, room: str):
    await manager.connect(websocket, room)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(f'{data}', room)
            await Cache.rpush(f'fastapi_room_{room}', data)
    except WebSocketDisconnect:
        manager.disconnect(websocket, room)


@app.exception_handler(RequestValidationError)
async def request_validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(status_code=422, content=error(422 * 100))


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


@app.get('/AAA', include_in_schema=False)
async def get_docs(credentials: HTTPBasicCredentials = Depends(doc_auth)):
    return get_swagger_ui_html(openapi_url='/CCC', title='핸즈온 문서')


@app.get('/BBB', include_in_schema=False)
async def get_redocs(credentials: HTTPBasicCredentials = Depends(doc_auth)):
    return get_redoc_html(openapi_url='/CCC', title='핸즈온 문서')


@app.get('/CCC', include_in_schema=False)
async def get_openapi_info(credentials: HTTPBasicCredentials = Depends(doc_auth)):
    openapi_schema = get_openapi(
        title='핸즈온',
        version='1.0.0',
        description='핸즈온 문서입니다.',
        routes=app.routes,
    )

    if 'components' not in openapi_schema:
        openapi_schema['components'] = {}
    if 'securitySchemes' not in openapi_schema['components']:
        openapi_schema['components']['securitySchemes'] = {}

    openapi_schema['components']['securitySchemes'] = {
        'XAccessTokenAuth': {
            'type': 'apiKey',
            'name': 'x-access-token',
            'in': 'header',
        }
    }
    openapi_schema['security'] = [{'XAccessTokenAuth': []}]
    return openapi_schema
