from fastapi import HTTPException
from sqlmodel import select

from app.database import get_session
from app.models.user import Roles, Permissions
from app.schemas.permissions import PermissionBase
from passlib.context import CryptContext
from sqlalchemy.exc import IntegrityError

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def service_get_permission_by_id(permission_id: int):
    with get_session() as session:
        statement = select(Permissions).where(Permissions.id == permission_id)
        results = session.exec(statement)
        return results.first()


def service_get_permission_by_name(permission_name: str):
    with get_session() as session:
        statement = select(Permissions).where(
            Permissions.permission_name == permission_name)
        results = session.exec(statement)
        return results.first()


def service_create_permission(permission: PermissionBase) -> Permissions:
    try:
        db_permission = Permissions(
            permission_name=permission.permission_name,
            descriptions=permission.descriptions
        )

        with get_session() as session:
            session.add(db_permission)
            session.commit()
            session.refresh(db_permission)
            return db_permission
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=409,
                            detail="Permission already exists")


def service_delete_permission(permission_id: int):
    with get_session() as session:
        permission = session.get(Permissions, permission_id)
        session.delete(permission)
        session.commit()
        return permission


def service_update_permission(permission_id: int,
                              permission: PermissionBase) -> Permissions:
    try:
        with get_session() as session:
            db_permission = session.get(Roles, permission_id)
        if db_permission is None:
            raise HTTPException(status_code=404,
                                detail="Permission not found")

        user_data = permission.model_dump(exclude_unset=True)
        for key, value in user_data.items():
            setattr(db_permission, key, value)

        with get_session() as session:
            session.add(db_permission)
            session.commit()
            session.refresh(db_permission)

        return db_permission
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=409,
                            detail="Permission already exists")


def main():
    p = PermissionBase(
        permission_name="api_manage_users",
        descriptions="Grants the ability to create, update, or delete user accounts via the API"
    )
    print(service_create_permission(p))


if __name__ == '__main__':
    main()
