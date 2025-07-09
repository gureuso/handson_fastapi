import re
import jwt
from fastapi.requests import Request

from app.database.mysql import UserEntity
from app.service.todo_user import TodoUserService
from app.service.user import UserService
from config import Config


class BadRequestException(Exception):
    pass


class PermissionDeniedException(Exception):
    pass


class NotFoundException(Exception):
    pass


class InternalServerException(Exception):
    pass


def error(code, message=None):
    if not message:
        message = Config.ERROR_CODE[code]

    result = {
        'code': code,
        'message': message
    }
    return result


async def is_mobile(request: Request) -> bool:
    user_agent = request.headers.get('User-Agent')
    mobile_keywords = [
        'Mobile', 'Android', 'iPhone', 'iPad', 'iPod', 'BlackBerry',
        'IEMobile', 'Opera Mini', 'Mobile Safari', 'webOS', 'Fennec',
        'Windows Phone', 'HTC', 'SonyEricsson', 'Nokia', 'Samsung', 'LG'
    ]
    pattern = re.compile('|'.join(mobile_keywords), re.IGNORECASE)
    return bool(pattern.search(user_agent))


async def verify_token(request: Request) -> None | UserEntity:
    token = request.cookies.get('x-access-token') or request.headers.get('x-access-token')
    if not token:
        return None
    jwt_data = jwt.decode(token, Config.SECRET, algorithms=['HS256'])
    current_user = await UserService.find_one_by_id(jwt_data['id'])
    if not current_user:
        return None

    return current_user


async def verify_api_token(request: Request) -> UserEntity:
    token = request.cookies.get('x-access-token') or request.headers.get('x-access-token')
    if not token:
        raise PermissionDeniedException()

    try:
        jwt.decode(token, Config.SECRET, algorithms=['HS256'])
    except jwt.exceptions.ExpiredSignatureError:
        raise PermissionDeniedException()

    jwt_data = jwt.decode(token, Config.SECRET, algorithms=['HS256'], options={'verify_exp': False})
    current_user = await UserService.find_one_by_id(jwt_data['id'])
    if not current_user:
        raise PermissionDeniedException()

    return current_user


async def verify_todo_api_token(request: Request) -> UserEntity:
    token = request.headers.get('x-access-token')
    if not token:
        raise PermissionDeniedException()
    jwt_data = jwt.decode(token, Config.SECRET, algorithms=['HS256'])
    current_user = await TodoUserService.find_one_by_id(jwt_data['id'])
    if not current_user:
        raise PermissionDeniedException()

    return current_user
