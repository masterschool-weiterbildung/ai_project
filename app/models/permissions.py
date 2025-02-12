from datetime import datetime, timezone
from typing import Optional

from sqlmodel import Field, SQLModel


class Permissions(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    permission_name: str = Field(unique=True, index=True)
    created_at: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
