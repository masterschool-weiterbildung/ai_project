from fastapi import APIRouter, Depends, status

from app.utility.logger import get_logger
from dependencies import get_current_user

router = APIRouter()
logger = get_logger()


@router.get("/welcome", status_code=status.HTTP_200_OK)
async def welcome_message(current_user: dict = Depends(get_current_user)):
    logger.info({"event": "Welcome Message"})
    return {"message": "This is a welcome message from AI Backend"}
