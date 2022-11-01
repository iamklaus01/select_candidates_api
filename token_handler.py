import time
from jose import jwt


ALGORITHM = "HS256"
SECRET_KEY = "fd35e4949b88cb67f1835d7cb91651c6a08a6068c2cfdf6bb03ae3d748fa89f7"
PATH_TO_BLACKLIST_TOKEN = 'blacklist_db.txt'

def init_blacklist_file():
    open(PATH_TO_BLACKLIST_TOKEN, 'a').close()
    return True


def get_token(user_email: str) -> str:
    payload = {
        "user_email": user_email,
        "expires": time.time() + 10800
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    return token


def decode_token(token: str) -> dict:
    try:
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return decoded_token if decoded_token["expires"] >= time.time() else None
    except Exception:
        return {}


def add_blacklist_token(token: str) ->bool:
    with open(PATH_TO_BLACKLIST_TOKEN, 'a') as file:
        file.write(f'{token},')
    return True


def is_token_blacklisted(token: str) ->bool:
    with open(PATH_TO_BLACKLIST_TOKEN) as file:
        content = file.read()
        array = content[:-1].split(',')
        for value in array:
            if value == token:
                return True

    return False