from fastapi import HTTPException
from sqlmodel import select

from app.database import get_session
from app.models import User, UserProfile
from app.models.user import Roles, Permissions, RolePermissions, UserRoles
from app.schemas.role_permission import RolePermission
from app.schemas.user import UserCreate, UserUpdate, \
    UserCreateRolePermission
from passlib.context import CryptContext
from sqlalchemy.exc import IntegrityError

from app.schemas.user_profile import UserProfileBase
from app.schemas.user_roles import UserRole
from app.utility.constant import ROLES, PERMISSIONS

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_user_by_id(user_id: int):
    with get_session() as session:
        statement = select(User).where(User.id == user_id)
        results = session.exec(statement)
        return results.first()


def get_user_by_username(username: str):
    with get_session() as session:
        statement = select(User).where(User.username == username)
        results = session.exec(statement)
        return results.first()


def service_delete_user(user_id: int):
    with get_session() as session:
        user = session.get(User, user_id)
        session.delete(user)
        session.commit()
        return user


def service_create_user(user_create: UserCreate) -> User:
    try:
        hashed_password = pwd_context.hash(
            user_create.password_hash)  # Hash password

        db_user = User(
            username=user_create.username,
            email=user_create.email,
            password_hash=hashed_password,
            is_active=user_create.is_active,
            is_disabled=user_create.is_disabled
        )

        with get_session() as session:
            session.add(db_user)
            session.commit()
            session.refresh(db_user)
            return db_user
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=409,
                            detail="Username or email already exists")


def service_create_user_with_role_permission(
        user_create: UserCreateRolePermission) -> User:
    try:
        hashed_password = pwd_context.hash(
            user_create.password_hash)  # Hash password

        permission = Permissions(
            permission_name=user_create.permission,
            descriptions=user_create.permission_description
        )

        role = Roles(role_name=user_create.role,
                     permissions=[permission])

        db_user = User(
            username=user_create.username,
            email=user_create.email,
            password_hash=hashed_password,
            is_active=user_create.is_active,
            is_disabled=user_create.is_disabled,
            roles=[role]
        )

        with get_session() as session:
            session.add(db_user)
            session.commit()
            session.refresh(db_user)
            return db_user
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=409,
                            detail="Username or email already exists")


def service_update_user(user_id: int, user: UserUpdate) -> User:
    try:
        with get_session() as session:
            db_user = session.get(User, user_id)
        if db_user is None:
            raise HTTPException(status_code=404, detail="User not found")

        user_data = user.model_dump(exclude_unset=True)
        for key, value in user_data.items():
            setattr(db_user, key, value)

        with get_session() as session:
            session.add(db_user)
            session.commit()
            session.refresh(db_user)

        return db_user
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=409,
                            detail="Username or email already exists")


def service_create_user_profile(
        user_create_profile: UserProfileBase):
    user = get_user_by_id(user_create_profile.user_id)

    if user is None:
        raise HTTPException(status_code=404,
                            detail="Username does not exists")

    db_user_profile = UserProfile(
        first_name=user_create_profile.first_name,
        last_name=user_create_profile.last_name,
        phone_number=user_create_profile.phone_number,
        address=user_create_profile.address,
        birth_date=user_create_profile.birth_date,
        bio=user_create_profile.bio,
        user_id=user.id
    )
    try:
        with get_session() as session:
            session.add(db_user_profile)
            session.commit()
            session.refresh(db_user_profile)
            return db_user_profile
    except IntegrityError:
        session.rollback()


def service_assign_permission(
        role_permission: RolePermission) -> RolePermissions:
    try:
        with get_session() as session:
            permission = session.get(Permissions,
                                     role_permission.permission_id)
            role = session.get(Roles, role_permission.role_id)

            if not permission or not role:
                raise HTTPException(status_code=404,
                                    detail="Permission or Role not found")

        role_permission = RolePermissions(
            role_id=role_permission.role_id,
            permission_id=role_permission.permission_id
        )

        with get_session() as session:
            session.add(role_permission)
            session.commit()
            session.refresh(role_permission)
            return role_permission
    except IntegrityError:
        session.rollback()


def service_assign_role(user_roles: UserRole) -> UserRoles:
    try:
        with get_session() as session:
            user = session.get(User,
                               user_roles.user_id)
            role = session.get(Roles, user_roles.role_id)

            if not user or not role:
                raise HTTPException(status_code=404,
                                    detail="User or Role not found")

        user_roles = UserRoles(
            role_id=user_roles.role_id,
            user_id=user_roles.user_id
        )

        with get_session() as session:
            session.add(user_roles)
            session.commit()
            session.refresh(user_roles)
            return user_roles
    except IntegrityError as ex:
        session.rollback()
        raise HTTPException(ex)


def get_user_role(user_id: int):
    with (get_session() as session):
        statement = select(Roles).join(UserRoles).where(
            Roles.id == UserRoles.role_id).where(
            UserRoles.user_id == user_id)

        results = session.exec(statement)
        return results.all()


def get_role_permission(role_name: str):
    with (get_session() as session):
        statement = select(Permissions).join(RolePermissions).join(
            Roles).where(
            Roles.role_name == role_name)

        results = session.exec(statement)
        return results.all()


def main():

    print(get_user_role(1))

    """
    ur = UserRole(
        user_id=1,
        role_id=3
    )
    print(service_assign_role(ur))



    permission = next(
        (p for p in get_role_permission(ROLES.API_USER.value)
         if p.permission_name == PERMISSIONS.API_GENERATE_TOKEN.value),
        None
    )

    print(permission)


        rp = RolePermission(
        role_id=1,
        permission_id=3)
        
    print(service_assign_permission(rp))
    """


if __name__ == '__main__':
    main()
