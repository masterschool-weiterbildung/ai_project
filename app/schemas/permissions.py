from pydantic import BaseModel


class PermissionBase(BaseModel):
    permission_name: str
    descriptions: str


class Permission(PermissionBase):
    permission_id: int

    class Config:
        from_attributes = True
