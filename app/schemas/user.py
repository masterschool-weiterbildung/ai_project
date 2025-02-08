from pydantic import BaseModel, Field

class UserBase(BaseModel):
    username: str
    email: str
    is_active: bool = Field(default=False)

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int

    class Config:
        from_attributes = True