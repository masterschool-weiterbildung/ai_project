from fastapi import APIRouter, HTTPException, Depends, status

from app.utility.jwt import get_current_user

router = APIRouter()


@router.get("/welcome", status_code=status.HTTP_200_OK)
async def welcome_message(current_user: dict = Depends(get_current_user)):
    return {"message": "This is a welcome message from AI Backend"}
