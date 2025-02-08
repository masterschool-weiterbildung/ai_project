from fastapi import HTTPException
from sqlmodel import select

from app.database import get_session
from app.models import User
from app.schemas.user import UserCreate
from passlib.context import CryptContext
from sqlalchemy.exc import IntegrityError

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_user_by_id(user_id: int):
    with get_session() as session:
        statement = select(User).where(User.id == user_id)
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
            user_create.password)  # Hash password

        db_user = User(
            username=user_create.username,
            email=user_create.email,
            password_hash=hashed_password,
            is_active=user_create.is_active
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
