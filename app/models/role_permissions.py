from datetime import datetime, timezone, date
from typing import Optional

from sqlmodel import Field, SQLModel


class RolePermissions(SQLModel, table=True):
    granted_at: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


    role_id: int | None = Field(default=None, foreign_key="roles.id",
                                primary_key=True)
    permission_id: int | None = Field(default=None,
                                      foreign_key="permissions.id",
                                      primary_key=True)
