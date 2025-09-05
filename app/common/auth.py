import base64
import hashlib
from Cryptodome import Random
from Cryptodome.Cipher import AES
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization, hashes

from config import JsonConfig, Config


def encrypt_with_public_key(message: bytes) -> bytes:
    public_key = serialization.load_pem_public_key("""""".encode('utf-8'))
    return public_key.encrypt(
        message,
        padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None)
    )

def decrypt_with_private_key(ciphertext: bytes) -> bytes:
    private_key = serialization.load_pem_private_key("""""".encode('utf-8'), password=None)
    return private_key.decrypt(
        ciphertext,
        padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None)
    )


class AESCipher:
    def __init__(self, key=JsonConfig.get_data('AES256_KEY')):
        self.bs = AES.block_size
        self.key = hashlib.sha256(key.encode()).digest()

    def encrypt(self, raw):
        raw = self._pad(raw)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return base64.b64encode(iv + cipher.encrypt(raw.encode()))

    def decrypt(self, enc):
        enc = base64.b64decode(enc)
        iv = enc[:AES.block_size]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return self._unpad(cipher.decrypt(enc[AES.block_size:])).decode('utf-8')

    def _pad(self, s):
        return s + (self.bs - len(s) % self.bs) * chr(self.bs - len(s) % self.bs)

    @staticmethod
    def _unpad(s):
        return s[:-ord(s[len(s)-1:])]


aes = AESCipher()


def resident_encrypt(data: str):
    return aes.encrypt(data).decode('utf-8')


def resident_decrypt(data: str):
    return aes.decrypt(data)


def sha256_encrypt(data: str):
    sha256 = hashlib.sha256()
    sha256.update(data.encode() + Config.SECRET.encode())
    return sha256.hexdigest()
