import os

from dotenv import load_dotenv


def get_key() -> str:
    load_dotenv()

    # openssl rand -hex 32
    return os.getenv('SECRET_KEY')


def get_token_expire_minutes() -> str | None:
    load_dotenv()

    return os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES')


def get_logfire_key() -> str:
    load_dotenv()

    return os.getenv('LOGFIRE_TOKEN')


def get_open_ai_key() -> str:
    load_dotenv()

    return os.getenv('OPEN_AI_KEY')
