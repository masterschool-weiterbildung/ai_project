from enum import Enum


class PERMISSIONS(Enum):
    API_GENERATE_TOKEN = "api_generate_token"


class ROLES(Enum):
    API_USER = "api_user"


CHAT_GPT = "chatgpt"
GEMINI = "gemini"
GROQ = "groq"

STATUS_DRAFT = "draft"
