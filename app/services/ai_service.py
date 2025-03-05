import openai
import json
from google import genai
from groq import Groq

from pydantic import BaseModel
from fastapi import HTTPException

from app.database import get_session
from app.models.nurses import Handoffs
from app.schemas.nurses import GenerateSbarBase
from app.services.nurse_services import service_get_patient_data, \
    get_latest_handoff, get_nurse_by_id, \
    get_nurse_notes_by_patient_id_by_shift
from app.utility.constant import CHAT_GPT, STATUS_DRAFT, \
    GEMINI, GROQ
from app.utility.env import get_open_ai_key, get_gemini_key, get_groq_key, \
    get_groq_model, get_gemini_model, get_open_ai_model
from app.utility.others import construct_sbar_report
from sqlalchemy.exc import IntegrityError

from app.utility.prompt import system_prompt, \
    system_prompt_regeneration_sbar_main, system_prompt_regeneration_sbar_body
from ratelimit import limits, sleep_and_retry


class Situation(BaseModel):
    patient_name: str
    mrn: str
    age: int
    gender: str
    room_number: int
    admission_date: str
    list_situations_feedback: list[str]


class Background(BaseModel):
    list_backgrounds: list[str]


class Assessment(BaseModel):
    list_assessments: list[str]


class Recommendation(BaseModel):
    list_recommendations: list[str]


class ReportedBy(BaseModel):
    nurse: str
    license_number: str


class HandoffReport(BaseModel):
    situation: Situation
    background: Background
    assessment: Assessment
    recommendation: Recommendation
    reported_by: ReportedBy


@sleep_and_retry
@limits(calls=1, period=1)
def generate_sbar(patient_id: int, nurse_id: int, model: str,
                  is_regenerate_sbar: bool):
    patient, vital_sign, medical_data = service_get_patient_data(patient_id)

    nurse = get_nurse_by_id(nurse_id)

    nurse_notes = get_nurse_notes_by_patient_id_by_shift(patient_id, nurse_id)

    if is_regenerate_sbar:

        hand_off = get_latest_handoff(patient_id, nurse_id)

        user_prompt = (
            f"Regenerate SBAR using the following:\n Patient Data : {patient},"
            f"\nVital Signs : {vital_sign}, \nMedical Data : {medical_data}, \nNurse Notes : {nurse_notes} , "
            f"Nurse Data : {nurse} ")

        system_prompt = system_prompt_regeneration_sbar_main + str(
            hand_off.report_text) + system_prompt_regeneration_sbar_body

    else:
        user_prompt = (
            f"Generate a SBAR using the following:\n Patient Data : {patient},"
            f"\nVital Signs : {vital_sign}, \nMedical Data : {medical_data}, \nNurse Notes : {nurse_notes} , "
            f"Nurse Data : {nurse} ")

    if model == CHAT_GPT:
        client = openai.OpenAI(api_key=get_open_ai_key())
        response = client.beta.chat.completions.parse(
            model=get_open_ai_model(),
            messages=[
                {"role": "system",
                 "content": f"{system_prompt}"},
                {"role": "user", "content": f"{user_prompt}"}
            ],
            temperature=0,
            response_format=HandoffReport,
        )

        return response.choices[0].message.parsed

    elif model == GEMINI:
        prompt = system_prompt + "\n\n" + user_prompt + "\n\n"

        client = genai.Client(api_key=get_gemini_key())

        response = client.models.generate_content(
            model=get_gemini_model(),
            contents=prompt,
            config={
                'response_mime_type': 'application/json',
                'response_schema': HandoffReport,
            },
        )

        return response.parsed

    elif model == GROQ:
        client = Groq(api_key=get_groq_key())

        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": f"{system_prompt} "
                               f"The JSON object must use the schema: {json.dumps(HandoffReport.model_json_schema(), indent=2)}",
                },
                {
                    "role": "user",
                    "content": f"{user_prompt}",
                },
            ],
            model=get_groq_model(),
            temperature=0,
            stream=False,
            response_format={"type": "json_object"},
        )
        return HandoffReport.model_validate_json(
            chat_completion.choices[0].message.content)


def service_generate_sbar(sbar: GenerateSbarBase, is_regenerated: bool):
    try:
        situation, background, assessment, recommendation, reported_by = generate_sbar(
            sbar.patient_id, sbar.outgoing_nurse_id, sbar.model.value,
            is_regenerated)

        json_result = construct_sbar_report(situation[1], background[1],
                                            assessment[1],
                                            recommendation[1],
                                            reported_by[1])
        db_hand_offs = Handoffs(
            report_text=json_result,
            status=STATUS_DRAFT,
            model=sbar.model.value,
            patient_id=sbar.patient_id,
            outgoing_nurse_id=sbar.outgoing_nurse_id,
            incoming_nurse_id=sbar.incoming_nurse_id
        )

        with get_session() as session:
            session.add(db_hand_offs)
            session.commit()
            session.refresh(db_hand_offs)
        return db_hand_offs

    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=400,
                            detail="Error adding handoffs")


def main():
    situation, background, assessment, recommendation, reported_by = generate_sbar(
        1, 1, GEMINI, True)

    json_result = construct_sbar_report(situation[1], background[1],
                                        assessment[1],
                                        recommendation[1],
                                        reported_by[1])

    print(json_result)


if __name__ == '__main__':
    main()
