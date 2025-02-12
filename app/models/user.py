from datetime import datetime, timezone
from typing import Optional

from sqlmodel import Field, SQLModel, Relationship


class UserRoles(SQLModel, table=True):
    created_at: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    role_id: int | None = Field(default=None, foreign_key="roles.id",
                                primary_key=True)
    user_id: int | None = Field(default=None, foreign_key="user.id",
                                primary_key=True)


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True)
    email: str = Field(unique=True, index=True)
    password_hash: str
    is_active: bool = Field(default=True)
    is_disabled: bool = Field(default=False)
    created_at: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    updated_at: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column_kwargs={"onupdate": lambda: datetime.now(timezone.utc)},
    )

    roles: list["Roles"] = Relationship(back_populates="users",
                                        link_model=UserRoles)


class Roles(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    role_name: str = Field(unique=True, index=True)
    created_at: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    users: list["User"] = Relationship(back_populates="roles",
                                       link_model=UserRoles)
