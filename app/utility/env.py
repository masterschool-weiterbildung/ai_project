import os

from dotenv import load_dotenv


def get_key() -> str:
    load_dotenv()

    return os.getenv('SECRET_KEY')


def get_token_expire_minutes() -> int:
    load_dotenv()

    return os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES')
