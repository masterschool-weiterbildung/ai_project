from pydantic import BaseModel


class UserRoles(BaseModel):
    role_id: int
    user_id: int

    class Config:
        from_attributes = True
