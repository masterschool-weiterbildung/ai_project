from datetime import date
from pydantic import BaseModel
from typing import Optional


class UserProfileBase(BaseModel):
    first_name: str
    last_name: str
    sex: Optional[str] = None
    phone_number: Optional[str] = None
    address: Optional[str] = None
    birth_date: date = None
    bio: Optional[str] = None
    user_id: int

    class Config:
        from_attributes = True


class UserProfile(UserProfileBase):
    id: int

    class Config:
        from_attributes = True
