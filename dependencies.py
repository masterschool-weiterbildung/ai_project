from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError

from app.schemas.apikeys import ApiKeysVerify
from app.schemas.user import User
from app.services.auth_service import is_api_key_active, \
    is_api_key_expired_set_inactive
from app.services.user_service import get_user_by_username
from app.utility.env import get_key

import jwt

from app.utility.jwt import get_user, TokenData

ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, get_key(), algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)

        user = get_user_by_username(token_data.username)

        key = ApiKeysVerify(
            api_key=token,
            user_id=user.id
        )
        is_valid = is_api_key_active(key)

        is_api_key_expired_set_inactive(token)

        if not is_valid:
            raise HTTPException(status_code=401,
                                detail="The API key validation was unsuccessful.")
    except InvalidTokenError:
        raise credentials_exception
    user = get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
        current_user: Annotated[User, Depends(get_current_user)],
):
    if current_user.is_disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
