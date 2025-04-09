from fastapi import APIRouter, Depends, status

from app.schemas.nurses import GenerateSbarBase, ChatBot
from app.services.ai_service import service_generate_sbar, service_chat_patient
from dependencies import get_current_active_user

router = APIRouter()


@router.post("/generate_sbar/", status_code=status.HTTP_201_CREATED)
async def generate_sbar(generate_sbar: GenerateSbarBase = Depends(),
                        current_user: dict = Depends(
                            get_current_active_user)):
    return_generate_sbar = service_generate_sbar(generate_sbar, False)
    return return_generate_sbar


@router.post("/chatbot/", status_code=status.HTTP_201_CREATED)
async def chatbot(chatbot: ChatBot = Depends(),
                  current_user: dict = Depends(
                      get_current_active_user)):
    return_generate_sbar = service_chat_patient(chatbot.message, chatbot.thread_id)
    return return_generate_sbar


@router.post("/re_generate_sbar/", status_code=status.HTTP_201_CREATED)
async def re_generate_sbar(generate_sbar: GenerateSbarBase = Depends(),
                           current_user: dict = Depends(
                               get_current_active_user)):
    return_generate_sbar = service_generate_sbar(generate_sbar, True)
    return return_generate_sbar