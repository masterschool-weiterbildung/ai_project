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

def get_pinecone_key() -> str:
    load_dotenv()

    return os.getenv('PINECONE_API_KEY')

def get_gemini_key() -> str:
    load_dotenv()

    return os.getenv('GEMINI_KEY')

def get_groq_key() -> str:
    load_dotenv()

    return os.getenv('GROQ_KEY')


def get_open_ai_model() -> str:
    load_dotenv()

    return os.getenv('OPEN_AI_MODEL')

def get_gemini_model() -> str:
    load_dotenv()

    return os.getenv('GEMINI_MODEL')

def get_groq_model() -> str:
    load_dotenv()

    return os.getenv('GROQ_MODEL')