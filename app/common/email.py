import requests

from app.database.mysql import UserEntity


class EmailSender:
    def __init__(self, user_entity: UserEntity):
        self.user_entity = user_entity

    def send(self, title: str, body: str) -> bool:
        data = {
            'senderAddress': 'youtube@devmaker.kr',
            'title': title,
            'body': body,
            'receiverList': [
                {
                    'receiveMailAddr': self.user_entity.email,
                },
            ]
        }
        res = requests.post(
            'https://api-mail.cloud.toast.com/email/v2.0/appKeys/C2yuVilGsblg9Z8A/sender/eachMail',
            json=data,
            headers={'X-Secret-Key': '5Ks2kQvA'},
        )
        return res.json()['header']['isSuccessful']
