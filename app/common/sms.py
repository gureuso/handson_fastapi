from twilio.rest import Client
from enum import Enum
from abc import ABCMeta, abstractmethod
import json
import requests
import twilio


class SmsEnum(Enum):
    """
        sms enum
    """
    ALIGO = 'ALIGO'
    TWILIO = 'TWILIO'


class SmsFactory:
    """
        sms factory
    """
    def __init__(self, kind: SmsEnum, phone_number: str) -> None:
        """
        :param kind:
        :param phone_number:
        """
        self.kind = kind
        self.phone_number = phone_number

    def send(self, message: str):
        """
            send factory version
        """
        klass = None
        if self.kind.value == SmsEnum.ALIGO.value:
            klass = AligoSMS(self.phone_number)
        elif self.kind.value == SmsEnum.TWILIO.value:
            klass = TwilioSMS(self.phone_number)

        return klass.send(message) if klass else False


class SMS(metaclass=ABCMeta):
    @abstractmethod
    def send(self, phone_number: str) -> bool:
        """
        :param phone_number:
        :return:
        """
        pass


class AligoSMS(SMS):
    def __init__(self, phone_number: str) -> None:
        """
        :param phone_number:
        """
        self.phone_number = phone_number

    def send(self, message) -> bool:
        """
            send aligo
        """
        api_key = '50uf4d6nw1pjmwvpdiuhruhuq7ota7o4'

        data = {
            'key': api_key,
            'user_id': 'wyun13043',
            'sender': '01084173012',
            'receiver': self.phone_number,
            'msg': message,
        }
        result = requests.post('https://apis.aligo.in/send/', data=data, timeout=5)
        result = json.loads(result.content)
        if result['result_code'] == -101:
            return False
        return True


class TwilioSMS(SMS):
    def __init__(self, phone_number: str) -> None:
        """
        :param phone_number:
        """
        self.phone_number = phone_number

    def send(self, message) -> bool:
        """
            send twilio
        """
        accounts_sid = ''
        auth_token = ''

        try:
            client = Client(accounts_sid, auth_token)
            client.messages.create(body=message, from_='+16183681494', to=self.phone_number)
        except twilio.base.exceptions.TwilioRestException as e:
            print(e)
            return False
        return True
