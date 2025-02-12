from datetime import datetime, timezone, date
from typing import Optional

from sqlmodel import Field, SQLModel


class UserProfile(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    first_name: str = Field(nullable=False, index=True)
    last_name: str = Field(nullable=False)
    phone_number: str | None = None
    address: str | None = None
    birth_date: date
    bio: str | None = None
    created_at: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    updated_at: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column_kwargs={"onupdate": lambda: datetime.now(timezone.utc)},
    )

    user_id: int = Field(default=None, foreign_key="user.id")
