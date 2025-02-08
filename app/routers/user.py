from fastapi import APIRouter, HTTPException, status
from app.database import get_session
from app.models import User
from app.schemas.user import UserCreate, UserUpdate
from app.services.user_service import get_user_by_id, service_create_user, \
    service_delete_user, service_update_user

router = APIRouter()


@router.post("/users/", response_model=User,
             status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate):
    db_user = service_create_user(user)
    return db_user


@router.get("/users/{user_id}", response_model=User)
async def read_user(user_id: int):
    db_user = get_user_by_id(user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return db_user


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int):
    db_user = get_user_by_id(user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    db_deleted = service_delete_user(user_id)
    if db_deleted is None:
        raise HTTPException(status_code=409,
                            detail="User logical constraints")
    return


@router.put("/users/{user_id}", response_model=User)
async def update_user(user_id: int, user: UserUpdate):
    return service_update_user(user_id, user)
