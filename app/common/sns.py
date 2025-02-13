import requests
import jwt
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import Literal

from app.common.response import BadRequestException
from config import JsonConfig


class SnsLoginItem(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int | None
    id_token: str | None


class SnsInfoItem(BaseModel):
    username: str
    email: str


class SNSLogin:
    def __init__(self, provider: Literal['google', 'facebook', 'kakao', 'naver', 'github'], code: str):
        self.provider = provider
        self.code = code

    def get_token(self) -> SnsLoginItem:
        if self.provider == 'google':
            login = GoogleLogin(self.code)
        elif self.provider == 'facebook':
            login = FacebookLogin(self.code)
        elif self.provider == 'kakao':
            login = KakaoLogin(self.code)
        elif self.provider == 'naver':
            login = NaverLogin(self.code)
        elif self.provider == 'github':
            login = GithubLogin(self.code)
        else:
            raise BadRequestException()

        return login.get_token()


class GoogleLogin:
    def __init__(self, code: str):
        self.code = code

    def get_token(self) -> SnsLoginItem:
        data = {
            'code': self.code,
            'client_id': JsonConfig.get_data('GOOGLE_CLIENT_ID'),
            'client_secret': JsonConfig.get_data('GOOGLE_SECRET_ID'),
            'redirect_uri': 'http://localhost:8082/users/callback/google',
            'grant_type': 'authorization_code'
        }
        res = requests.post('https://www.googleapis.com/oauth2/v4/token', data=data)
        res = res.json()
        return SnsLoginItem(
            access_token=res['access_token'],
            refresh_token=res['refresh_token'],
            token_type=res['token_type'],
            expires_in=res.get('expires_in'),
            id_token=res.get('id_token'),
        )


class KakaoLogin:
    def __init__(self, code: str):
        self.code = code

    def get_token(self) -> SnsLoginItem:
        data = {
            'grant_type': 'authorization_code',
            'client_id': JsonConfig.get_data('KAKAO_REST_KEY'),
            'redirect_uri': 'http://org.devmaker.kr/users/callback/kakao',
            # 'redirect_uri': 'http://localhost:8082/users/callback/kakao',
            'code': self.code,
        }
        res = requests.post('https://kauth.kakao.com/oauth/token', data=data)
        res = res.json()
        return SnsLoginItem(
            access_token=res['access_token'],
            refresh_token=res['refresh_token'],
            token_type=res['token_type'],
            expires_in=res.get('expires_in'),
            id_token=res.get('id_token'),
        )

class FacebookLogin:
    def __init__(self, code: str):
        self.code = code

    def get_token(self) -> SnsLoginItem:
        params = {
            'client_id': JsonConfig.get_data('FB_CLIENT_ID'),
            'client_secret': JsonConfig.get_data('FB_SECRET_ID'),
            'code': self.code,
            'redirect_uri': 'http://localhost:8082/users/callback/kakao',
        }
        res = requests.get('https://graph.facebook.com/oauth/access_token', params=params)
        res = res.json()
        return SnsLoginItem(
            access_token=res['access_token'],
            refresh_token=res['refresh_token'],
            token_type=res['token_type'],
            expires_in=res.get('expires_in'),
            id_token=res.get('id_token'),
        )


class NaverLogin:
    def __init__(self, code: str):
        self.code = code

    def get_token(self) -> SnsLoginItem:
        params = {
            'grant_type': 'authorization_code',
            'client_id': JsonConfig.get_data('NAVER_CLIENT_ID'),
            'client_secret': JsonConfig.get_data('NAVER_SECRET_ID'),
            'code': self.code,
            'state': self.code,
            'redirect_uri': 'http://localhost:8082/users/callback/kakao',
        }
        res = requests.get('https://nid.naver.com/oauth2.0/token', params=params)
        res = res.json()
        return SnsLoginItem(
            access_token=res['access_token'],
            refresh_token=res['refresh_token'],
            token_type=res['token_type'],
            expires_in=res.get('expires_in'),
            id_token=res.get('id_token'),
        )


class GithubLogin:
    def __init__(self, code: str):
        self.code = code

    def get_token(self) -> SnsLoginItem:
        params = {
            'client_id': JsonConfig.get_data('GITHUB_CLIENT_ID'),
            'client_secret': JsonConfig.get_data('GITHUB_SECRET_ID'),
            'code': self.code,
            'redirect_uri': 'http://localhost:8082/users/callback/kakao',
        }
        res = requests.post('https://github.com/login/oauth/access_token', headers={'Accept': 'application/json'},
                            data=params)
        res = res.json()
        return SnsLoginItem(
            access_token=res['access_token'],
            refresh_token=res['refresh_token'],
            token_type=res['token_type'],
            expires_in=res.get('expires_in'),
            id_token=res.get('id_token'),
        )


class SNSInfo:
    def __init__(self, provider: Literal['google', 'facebook', 'kakao', 'naver', 'github'], code: str):
        self.provider = provider
        self.token_data = SNSLogin(provider, code).get_token()

    def __post_init__(self):
        if not self.token_data.access_token:
            raise BadRequestException()

    def get_info(self) -> SnsInfoItem:
        if self.provider == 'google':
            info = GoogleInfo(self.token_data)
        elif self.provider == 'facebook':
            info = FacebookInfo(self.token_data)
        elif self.provider == 'kakao':
            info = KakaoInfo(self.token_data)
        elif self.provider == 'naver':
            info = NaverInfo(self.token_data)
        elif self.provider == 'github':
            info = GithubInfo(self.token_data)
        elif self.provider == 'apple':
            info = AppleInfo(self.token_data)
        else:
            raise BadRequestException()

        return info.get_info()


class GoogleInfo:
    def __init__(self, token_data):
        self.token_data = token_data

    def get_info(self) -> SnsInfoItem:
        res = requests.get('https://oauth2.googleapis.com/tokeninfo', {'access_token': self.token_data.access_token})
        data = res.json()
        email = data['email']
        username = email.split('@')[0] if email else None
        if not email:
            raise BadRequestException()
        return SnsInfoItem(username=username, email=email)


class KakaoInfo:
    def __init__(self, token_data):
        self.token_data = token_data

    def get_info(self) -> SnsInfoItem:
        res = requests.post('https://kapi.kakao.com/v2/user/me',
                            headers={'Authorization': 'Bearer {}'.format(self.token_data.access_token)})
        data = res.json()
        email = data['kakao_account'].get('email')
        username = email.split('@')[0] if email else None
        if not email:
            raise BadRequestException()
        return SnsInfoItem(username=username, email=email)


class FacebookInfo:
    def __init__(self, token_data):
        self.token_data = token_data

    def get_info(self) -> SnsInfoItem:
        params = {'access_token': self.token_data.access_token, 'fields': 'email'}
        res = requests.get('https://graph.facebook.com/v4.0/me', params=params)
        data = res.json()
        email = data['email']
        username = email.split('@')[0] if email else None
        if not email:
            raise BadRequestException()
        return SnsInfoItem(username=username, email=email)


class NaverInfo:
    def __init__(self, token_data):
        self.token_data = token_data

    def get_info(self) -> SnsInfoItem:
        res = requests.post('https://openapi.naver.com/v1/nid/me',
                            headers={'Authorization': 'Bearer {}'.format(self.token_data.access_token)})
        data = res.json()
        email = data['response']['email']
        username = email.split('@')[0] if email else None
        if not email:
            raise BadRequestException()
        return SnsInfoItem(username=username, email=email)


class GithubInfo:
    def __init__(self, token_data):
        self.token_data = token_data

    def get_info(self) -> SnsInfoItem:
        res = requests.get('https://api.github.com/user',
                           headers={'Authorization': 'token {}'.format(self.token_data.access_token)})
        data = res.json()
        email = data['email']
        username = email.split('@')[0] if email else None
        if not email:
            raise BadRequestException()
        return SnsInfoItem(username=username, email=email)


class AppleInfo:
    def __init__(self, token_data):
        self.token_data = token_data

    def get_info(self) -> SnsInfoItem:
        content = {'iss': '59N7LBG42C', 'iat': datetime.now(), 'exp': datetime.now() + timedelta(days=180),
                   'aud': 'https://appleid.apple.com', 'sub': 'kr.devmaker.diary.colorDiary'}
        header = {'kid': 'P24BZ42QS9'}

        client_id = 'kr.devmaker.diary.colorDiary'
        client_secret = jwt.encode(
            payload=content,
            key='''-----BEGIN PRIVATE KEY-----
MIGTAgEAMBMGByqGSM49AgEGCCqGSM49AwEHBHkwdwIBAQQgyhGwkyAjQIX7k35n
0s7h5fhvosxxtTFaEFAU3HlUZKmgCgYIKoZIzj0DAQehRANCAAR0h4kEUJhKtv1y
HwBNmUdph8vXfYdl9pef26aY3KhJGbg0/YXoohh9Ykp+dEFs8bdrtxq7cfv35xwn
0o7vZdWS
-----END PRIVATE KEY-----''',
            algorithm='ES256',
            headers=header
        )

        headers = {'content-type': 'application/x-www-form-urlencoded'}
        data = {
            'client_id': client_id,
            'client_secret': client_secret,
            'code': self.token_data.access_token,
            'grant_type': 'authorization_code',
            'redirect_uri': 'https://example-app.com/redirect'
        }
        res = requests.post('https://appleid.apple.com/auth/token', data=data, headers=headers)
        data = res.json()
        if data.get('error'):
            raise BadRequestException()

        data = jwt.decode(data.get('id_token'), algorithms=['ES256'], options={'verify_signature': False})
        email = data['email']
        username = email.split('@')[0] if email else None
        if not email:
            raise BadRequestException()
        return SnsInfoItem(username=username, email=email)
