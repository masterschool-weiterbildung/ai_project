from fastapi import HTTPException
from sqlmodel import select

from app.database import get_session
from app.models.user import Roles

from app.schemas.roles import RoleBase
from sqlalchemy.exc import IntegrityError


def service_get_role_by_id(role_id: int):
    with get_session() as session:
        statement = select(Roles).where(Roles.id == role_id)
        results = session.exec(statement)
        return results.first()


def service_get_role_by_name(role_name: str):
    with get_session() as session:
        statement = select(Roles).where(Roles.role_name == role_name)
        results = session.exec(statement)
        return results.first()


def service_create_role(role: RoleBase) -> Roles:
    try:
        db_roles = Roles(
            role_name=role.role_name,
        )

        with get_session() as session:
            session.add(db_roles)
            session.commit()
            session.refresh(db_roles)
            return db_roles
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=409,
                            detail="Role already exists")


def service_delete_role(role_id: int):
    with get_session() as session:
        role = session.get(Roles, role_id)
        session.delete(role)
        session.commit()
        return role


def service_update_role(role_id: int, role: RoleBase) -> Roles:
    try:
        with get_session() as session:
            db_role = session.get(Roles, role_id)
        if db_role is None:
            raise HTTPException(status_code=404, detail="Role not found")

        user_data = role.model_dump(exclude_unset=True)
        for key, value in user_data.items():
            setattr(db_role, key, value)

        with get_session() as session:
            session.add(db_role)
            session.commit()
            session.refresh(db_role)

        return db_role
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=409,
                            detail="Role already exists")


def main():
    r = RoleBase(
        role_name="admin"
    )
    print(service_create_role(r))


if __name__ == '__main__':
    main()
