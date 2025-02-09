from fastapi import APIRouter, HTTPException, Depends
from app.models import User
from app.services.user_service import get_user_by_id
from app.utility.jwt import get_current_user

router = APIRouter()


@router.get("/users/{user_id}", response_model=User)
async def read_user(user_id: int , current_user: dict = Depends(get_current_user)):
    db_user = get_user_by_id(user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return db_user
