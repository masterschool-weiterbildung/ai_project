from pydantic import BaseModel


class UserRolesBase(BaseModel):
    role_id: int


class UserRole(UserRolesBase):
    user_id: int

    class Config:
        from_attributes = True
