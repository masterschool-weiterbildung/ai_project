from typing import Annotated
from datetime import timedelta, datetime

from fastapi import Depends, HTTPException, status, APIRouter
from fastapi.security import OAuth2PasswordRequestForm

from app.schemas.apikeys import ApiKeysBase
from app.services.auth_service import service_create_api_key
from app.services.user_service import get_role_permission, get_user_role
from app.utility.constant import ROLES, PERMISSIONS
from app.utility.env import get_token_expire_minutes
from app.utility.jwt import authenticate_user, Token, create_access_token

router = APIRouter()


@router.post("/token")
async def login_for_access_token(
        form_data: Annotated[OAuth2PasswordRequestForm,
        Depends()], ) -> Token:
    user = authenticate_user(form_data.username,
                             form_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    await is_allowed_to_generate_token(user)

    access_token_expires = timedelta(minutes=int(get_token_expire_minutes()))

    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    now = datetime.now()

    db_api_key = ApiKeysBase(
        api_key=access_token,
        user_id=user.id,
        expires_at=now + access_token_expires,
        is_active=True
    )

    service_create_api_key(db_api_key)

    return Token(access_token=access_token, token_type="bearer")


async def is_allowed_to_generate_token(user):
    role = next(
        (r for r in get_user_role(user.id)
         if r.role_name == ROLES.API_USER.value),
        None
    )
    if not role or role is None:
        raise HTTPException(status_code=404,
                            detail="The username is not allowed to generate a token.")
    permission = next(
        (p for p in get_role_permission(ROLES.API_USER.value)
         if p.permission_name == PERMISSIONS.API_GENERATE_TOKEN.value),
        None
    )
    if not permission or permission is None:
        raise HTTPException(status_code=404,
                            detail="The username is not allowed to generate a token.")
