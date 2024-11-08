import requests

from app.database.mysql import UserEmailEntity


class EmailSender:
    def __init__(self, user_email_entity: UserEmailEntity):
        self.user_email_entity = user_email_entity

    def send(self, code: str) -> bool:
        data = {
            'senderAddress': 'gomin@devmaker.kr',
            'title': f'[고민들어줌] 이메일 인증',
            'body': f'[고민들어줌]\n<h1>{code}</h1>',
            'receiverList': [
                {
                    'receiveMailAddr': self.user_email_entity.email,
                },
            ]
        }
        res = requests.post(
            'https://api-mail.cloud.toast.com/email/v2.0/appKeys/C2yuVilGsblg9Z8D/sender/eachMail',
            json=data,
            headers={'X-Secret-Key': '5Ks2kQvi'},
        )
        return res.json()['header']['isSuccessful']
