from pydantic import BaseModel


class RoleBase(BaseModel):
    role_name: str = 'nurse'


class Roles(RoleBase):
    role_id: int

    class Config:
        from_attributes = True
