import datetime

from pydantic import BaseModel, Field
from typing import Optional


class UserProfileBase(BaseModel):
    first_name: str
    last_name: str
    phone_number: Optional[str] = None
    address: Optional[str] = None
    birth_date: datetime | None = None
    bio: Optional[str] = None

    class Config:
        from_attributes = True


class UserProfile(UserProfileBase):
    user_id: int    

    class Config:
        from_attributes = True
