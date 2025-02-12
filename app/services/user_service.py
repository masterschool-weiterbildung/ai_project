from fastapi import HTTPException
from sqlmodel import select

from app.database import get_session
from app.models import User, UserProfile
from app.models.user import Roles
from app.schemas.user import UserCreate, UserUpdate, UserCreateRole
from passlib.context import CryptContext
from sqlalchemy.exc import IntegrityError

from app.schemas.user_profile import UserProfileBase

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


def service_create_user_with_role(user_create: UserCreateRole) -> User:
    try:
        hashed_password = pwd_context.hash(
            user_create.password_hash)  # Hash password

        admin_role = Roles(role_name=user_create.role)

        db_user = User(
            username=user_create.username,
            email=user_create.email,
            password_hash=hashed_password,
            is_active=user_create.is_active,
            is_disabled=user_create.is_disabled,
            roles=[admin_role]
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
                            detail="Username id does not exists")

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
