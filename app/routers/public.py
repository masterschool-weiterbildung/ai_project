from fastapi import APIRouter, HTTPException, Depends, status

from app.utility.jwt import get_current_user
from app.utility.logger import get_logger

router = APIRouter()
logger = get_logger()

@router.get("/welcome", status_code=status.HTTP_200_OK)
async def welcome_message(current_user: dict = Depends(get_current_user)):
    logger.info({"event": "Welcome Message"})
    return {"message": "This is a welcome message from AI Backend"}
