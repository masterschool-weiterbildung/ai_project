from enum import Enum


class PERMISSIONS(Enum):
    API_GENERATE_TOKEN = "api_generate_token"


class ROLES(Enum):
    API_USER = "api_user"


CHAT_GPT = "chatgpt"
GEMINI = "gemini"
GROQ = "groq"
XAI = "xai"
XAI_BASEURL = "https://api.x.ai/v1"

CHAT_GPT_PRICE_PER_TOKEN = 0.00000015
GEMINI_PRICE_PER_TOKEN = 0.0000001
LLAMA_PRICE_PER_TOKEN = 0.00000059
XAI_PRICE_PER_TOKEN = 0.00002

STATUS_DRAFT = "draft"

MAX_MESSAGES = 5

INDEX_NAME = "nursingassistant"
NAMESPACE = "nursing"


