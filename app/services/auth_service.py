from fastapi import HTTPException
from app.database import get_session
from app.models import User, APIKeys
from app.schemas.apikeys import ApiKeysBase
from sqlalchemy.exc import IntegrityError

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
