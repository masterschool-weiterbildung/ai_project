from pydantic import BaseModel, Field


class UserBase(BaseModel):
    username: str
    email: str
    is_active: bool = Field(default=True)
    is_disabled: bool = Field(default=False)


class UserUpdate(BaseModel):
    is_active: bool = Field(default=False)
    email: str = None

    class Config:
        from_attributes = True


class UserCreate(UserBase):
    password_hash: str

class UserCreateRole(UserBase):
    password_hash: str
    role: str


class User(UserBase):
    user_id: int
    password_hash: str

    class Config:
        from_attributes = True
