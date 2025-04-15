import requests
from pydantic import BaseModel
from typing import Literal

from app.common.response import BadRequestException
from config import JsonConfig, Config


class SnsLoginItem(BaseModel):
    access_token: str
    refresh_token: str | None
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
            'redirect_uri': 'http://localhost:8888/youtube/api/callback/google' if JsonConfig.get_data('APP_MODE') == Config.APP_MODE_DEVELOPMENT else 'https://youtube.devmaker.kr/youtube/api/callback/google',
            'grant_type': 'authorization_code'
        }
        res = requests.post('https://www.googleapis.com/oauth2/v4/token', data=data)
        res = res.json()
        return SnsLoginItem(
            access_token=res['access_token'],
            refresh_token=res.get('refresh_token'),
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
            'client_id': JsonConfig.get_data('KAKAO_CLIENT_ID'),
            'redirect_uri': 'http://localhost:8888/youtube/api/callback/kakao' if JsonConfig.get_data('APP_MODE') == Config.APP_MODE_DEVELOPMENT else 'https://youtube.devmaker.kr/youtube/api/callback/kakao',
            'code': self.code,
        }
        res = requests.post('https://kauth.kakao.com/oauth/token', data=data)
        res = res.json()
        return SnsLoginItem(
            access_token=res['access_token'],
            refresh_token=res.get('refresh_token'),
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
            'redirect_uri': 'http://localhost:8888/youtube/api/callback/facebook' if JsonConfig.get_data('APP_MODE') == Config.APP_MODE_DEVELOPMENT else 'https://youtube.devmaker.kr/youtube/api/callback/facebook',
        }
        res = requests.get('https://graph.facebook.com/oauth/access_token', params=params)
        res = res.json()
        return SnsLoginItem(
            access_token=res['access_token'],
            refresh_token=res.get('refresh_token'),
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
            'redirect_uri': 'http://localhost:8888/youtube/api/callback/naver' if JsonConfig.get_data('APP_MODE') == Config.APP_MODE_DEVELOPMENT else 'https://youtube.devmaker.kr/youtube/api/callback/naver',
        }
        res = requests.get('https://nid.naver.com/oauth2.0/token', params=params)
        res = res.json()
        return SnsLoginItem(
            access_token=res['access_token'],
            refresh_token=res.get('refresh_token'),
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
            'redirect_uri': 'http://localhost:8888/youtube/api/callback/github' if JsonConfig.get_data('APP_MODE') == Config.APP_MODE_DEVELOPMENT else 'https://youtube.devmaker.kr/youtube/api/callback/github',
        }
        res = requests.post('https://github.com/login/oauth/access_token', headers={'Accept': 'application/json'},
                            data=params)
        res = res.json()
        return SnsLoginItem(
            access_token=res['access_token'],
            refresh_token=res.get('refresh_token'),
            token_type=res['token_type'],
            expires_in=res.get('expires_in'),
            id_token=res.get('id_token'),
        )


class SNSInfo:
    def __init__(self, provider: Literal['google', 'facebook', 'kakao', 'naver', 'github'], code: str):
        self.provider = provider
        self.token_data = SNSLogin(provider, code).get_token()

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
