import json
import requests
import twilio
from twilio.rest import Client
from enum import Enum
from abc import ABCMeta, abstractmethod

from app.common.response import BadRequestException


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

    def send(self, message: str) -> bool:
        """
            send factory version
        """
        if self.kind.value == SmsEnum.ALIGO.value:
            klass = AligoSMS(self.phone_number)
        elif self.kind.value == SmsEnum.TWILIO.value:
            klass = TwilioSMS(self.phone_number)
        else:
            raise BadRequestException()

        return klass.send(message)


class SMS(metaclass=ABCMeta):
    @abstractmethod
    def send(self, message: str) -> bool:
        """
        :param message:
        :return:
        """
        pass


class AligoSMS(SMS):
    def __init__(self, phone_number: str) -> None:
        """
        :param phone_number:
        """
        self.api_key = ''
        self.phone_number = phone_number

    def send(self, message: str) -> bool:
        """
            send aligo
        """

        data = {
            'key': self.api_key,
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
        self.accounts_sid = ''
        self.auth_token = ''
        self.phone_number = phone_number

    def send(self, message: str) -> bool:
        """
            send twilio
        """

        try:
            client = Client(self.accounts_sid, self.auth_token)
            client.messages.create(body=message, from_='+18482929136', to=self.phone_number)
        except twilio.base.exceptions.TwilioRestException as e:
            print(e)
            return False
        return True
