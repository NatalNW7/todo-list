from datetime import datetime, timedelta

from jwt import encode
from pwdlib import PasswordHash
from zoneinfo import ZoneInfo

SECRET_KEY = 'TESTE'
ALGORIHTM = 'HS256'
EXPIRATION_TIME = 30
pwd_context = PasswordHash.recommended()


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(tz=ZoneInfo('UTC')) + timedelta(
        minutes=EXPIRATION_TIME
    )

    to_encode.update({'exp': expire})
    encode_jwt = encode(to_encode, SECRET_KEY, algorithm=ALGORIHTM)

    return encode_jwt


def get_password_hash(password: str):
    return pwd_context.hash(password)


def check_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)
