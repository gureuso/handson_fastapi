from datetime import datetime, timedelta

import requests
import jwt


from config import JsonConfig


class SNSLogin:
    def __init__(self, provider, code):
        self.provider = provider
        self.code = code

    def get_token(self):
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
            login = None

        token_data = login.get_token() if login else {}
        result = {
            'access_token': token_data.get('access_token'),
            'refresh_token': token_data.get('refresh_token'),
            'token_type': token_data.get('token_type'),
            'expires_in': token_data.get('expires_in'),
            'id_token': token_data.get('id_token'),
        }
        return result


class GoogleLogin:
    def __init__(self, code):
        self.code = code

    def get_token(self):
        data = {
            'code': self.code,
            'client_id': JsonConfig.get_data('GOOGLE_CLIENT_ID'),
            'client_secret': JsonConfig.get_data('GOOGLE_SECRET_ID'),
            'redirect_uri': 'http://localhost:8082/users/callback/google',
            'grant_type': 'authorization_code'
        }
        res = requests.post('https://www.googleapis.com/oauth2/v4/token', data=data)
        return res.json()


class KakaoLogin:
    def __init__(self, code):
        self.code = code

    def get_token(self):
        data = {
            'grant_type': 'authorization_code',
            'client_id': JsonConfig.get_data('KAKAO_REST_KEY'),
            'redirect_uri': 'http://org.devmaker.kr/users/callback/kakao',
            # 'redirect_uri': 'http://localhost:8082/users/callback/kakao',
            'code': self.code,
        }
        res = requests.post('https://kauth.kakao.com/oauth/token', data=data)
        return res.json()


class FacebookLogin:
    def __init__(self, code):
        self.code = code

    def get_token(self):
        params = {
            'client_id': JsonConfig.get_data('FB_CLIENT_ID'),
            'client_secret': JsonConfig.get_data('FB_SECRET_ID'),
            'code': self.code,
            'redirect_uri': 'http://localhost:8082/users/callback/kakao',
        }
        res = requests.get('https://graph.facebook.com/oauth/access_token', params=params)
        return res.json()


class NaverLogin:
    def __init__(self, code):
        self.code = code

    def get_token(self):
        params = {
            'grant_type': 'authorization_code',
            'client_id': JsonConfig.get_data('NAVER_CLIENT_ID'),
            'client_secret': JsonConfig.get_data('NAVER_SECRET_ID'),
            'code': self.code,
            'state': self.code,
            'redirect_uri': 'http://localhost:8082/users/callback/kakao',
        }
        res = requests.get('https://nid.naver.com/oauth2.0/token', params=params)
        return res.json()


class GithubLogin:
    def __init__(self, code):
        self.code = code

    def get_token(self):
        params = {
            'client_id': JsonConfig.get_data('GITHUB_CLIENT_ID'),
            'client_secret': JsonConfig.get_data('GITHUB_SECRET_ID'),
            'code': self.code,
            'redirect_uri': 'http://localhost:8082/users/callback/kakao',
        }
        res = requests.post('https://github.com/login/oauth/access_token', headers={'Accept': 'application/json'},
                            data=params)
        return res.json()


class SNSInfo:
    def __init__(self, provider, token_data):
        self.provider = provider
        self.token_data = token_data

    def get_info(self):
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
            info = None
        return info.get_info() if info else None


class GoogleInfo:
    def __init__(self, token_data):
        self.token_data = token_data

    def get_info(self):
        access_token = self.token_data['access_token']
        if not access_token:
            return None

        res = requests.get('https://oauth2.googleapis.com/tokeninfo', {'access_token': access_token})
        data = res.json()
        email = data['email']
        username = email.split('@')[0] if email else None
        if not email:
            return None
        return {'email': email, 'username': username}


class KakaoInfo:
    def __init__(self, token_data):
        self.token_data = token_data

    def get_info(self):
        access_token = self.token_data['access_token']
        if not access_token:
            return None

        res = requests.post('https://kapi.kakao.com/v2/user/me',
                            headers={'Authorization': 'Bearer {}'.format(access_token)})
        data = res.json()
        email = data['kakao_account'].get('email')
        username = email.split('@')[0] if email else None
        if not email:
            return None
        return {'email': email, 'username': username}


class FacebookInfo:
    def __init__(self, token_data):
        self.token_data = token_data

    def get_info(self):
        access_token = self.token_data['access_token']
        if not access_token:
            return None

        params = {'access_token': access_token, 'fields': 'email'}
        res = requests.get('https://graph.facebook.com/v4.0/me', params=params)
        data = res.json()
        email = data['email']
        username = email.split('@')[0] if email else None
        if not email:
            return None
        return {'email': email, 'username': username}


class NaverInfo:
    def __init__(self, token_data):
        self.token_data = token_data

    def get_info(self):
        access_token = self.token_data['access_token']
        if not access_token:
            return None

        res = requests.post('https://openapi.naver.com/v1/nid/me',
                            headers={'Authorization': 'Bearer {}'.format(access_token)})
        data = res.json()
        email = data['response']['email']
        username = email.split('@')[0] if email else None
        if not email:
            return None
        return {'email': email, 'username': username}


class GithubInfo:
    def __init__(self, token_data):
        self.token_data = token_data

    def get_info(self):
        access_token = self.token_data['access_token']
        if not access_token:
            return None

        res = requests.get('https://api.github.com/user',
                           headers={'Authorization': 'token {}'.format(access_token)})
        data = res.json()
        email = data['email']
        username = email.split('@')[0] if email else None
        if not email:
            return None
        return {'email': email, 'username': username}


class AppleInfo:
    def __init__(self, token_data):
        self.token_data = token_data

    def get_info(self):
        access_token = self.token_data['access_token']
        if not access_token:
            return None

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
0o7vZdWs
-----END PRIVATE KEY-----''',
            algorithm='ES256',
            headers=header
        )

        headers = {'content-type': 'application/x-www-form-urlencoded'}
        data = {
            'client_id': client_id,
            'client_secret': client_secret,
            'code': access_token,
            'grant_type': 'authorization_code',
            'redirect_uri': 'https://example-app.com/redirect'
        }
        res = requests.post('https://appleid.apple.com/auth/token', data=data, headers=headers)
        data = res.json()
        if data.get('error'):
            return None

        data = jwt.decode(data.get('id_token'), algorithms=['ES256'], options={'verify_signature': False})
        email = data['email']
        username = email.split('@')[0] if email else None
        if not email:
            return None
        return {'email': email, 'username': username}
