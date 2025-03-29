from fastapi import APIRouter, Depends, status

from app.schemas.nurses import GenerateSbarBase
from app.services.ai_service import service_generate_sbar
from dependencies import get_current_active_user

router = APIRouter()


@router.post("/generate_sbar/", status_code=status.HTTP_201_CREATED)
async def generate_sbar(generate_sbar: GenerateSbarBase = Depends(),
                        current_user: dict = Depends(
                            get_current_active_user)):
    return_generate_sbar = service_generate_sbar(generate_sbar, False)
    return return_generate_sbar


@router.post("/re_generate_sbar/", status_code=status.HTTP_201_CREATED)
async def re_generate_sbar(generate_sbar: GenerateSbarBase = Depends(),
                           current_user: dict = Depends(
                               get_current_active_user)):
    return_generate_sbar = service_generate_sbar(generate_sbar, True)
    return return_generate_sbar


""""
@router.post("/generate_draft_reponses_for_patient_messages/",
             status_code=status.HTTP_201_CREATED)
async def generate_draft_reponses_for_patient_messages(question: str):
    return service_generate_draft_message_to_patient(question)
"""
