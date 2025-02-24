from datetime import datetime
from fastapi import HTTPException
from app.database import get_session
from app.models import User, APIKeys
from app.schemas.apikeys import ApiKeysBase, ApiKeysVerify
from sqlalchemy.exc import IntegrityError
from sqlmodel import select

from app.services.user_service import get_user_by_id


def service_create_api_key(api_key: ApiKeysBase) -> APIKeys:
    try:

        user = get_user_by_id(api_key.user_id)

        if user is None:
            raise HTTPException(status_code=404,
                                detail="Username does not exists")
        db_api_key = APIKeys(
            api_key=api_key.api_key,
            user_id=api_key.user_id,
            expires_at=api_key.expires_at,
            is_active=api_key.is_active
        )

        with get_session() as session:
            session.add(db_api_key)
            session.commit()
            session.refresh(db_api_key)
            return db_api_key
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=409,
                            detail="Error in generating api key")


def is_api_key_expired_set_inactive(api_key: str) -> bool:
    with get_session() as session:
        statement = select(APIKeys).where(
            APIKeys.api_key == api_key).where(
            APIKeys.is_active == True).where(
            APIKeys.expires_at < datetime.now())

        results = session.exec(statement).first()

        if results:
            key = session.get(APIKeys, results.id)
            key.is_active = False
            session.add(key)
            session.commit()
            session.refresh(key)
            return True
        return False


def is_api_key_active(api_key: ApiKeysVerify):
    with get_session() as session:
        statement = select(APIKeys).join(User).where(
            APIKeys.api_key == api_key.api_key).where(
            APIKeys.is_active == True).where(
            APIKeys.expires_at > datetime.now()).where(
            User.is_active == True)

        results = session.exec(statement).first()

        if not results:
            return False
        return True


def main():
    api_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJKZXJvbWUiLCJleHAiOjE3Mzk1NjQwODB9.JqQGqD225PkN38hReTGu37Xgf7umstIzn-b9Yjl-LWg"
    print(is_api_key_expired_set_inactive(api_key))


if __name__ == '__main__':
    main()
