from datetime import datetime

from pydantic import BaseModel


class ApiKeysBase(BaseModel):
    api_key: str
    user_id: int
    expires_at: datetime
    is_active: bool


class ApiKeysVerify(BaseModel):
    api_key: str
    user_id: int


class ApiKeys(ApiKeysBase):
    api_key_id: int

    class Config:
        from_attributes = True
