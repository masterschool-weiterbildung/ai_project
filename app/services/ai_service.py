import openai

from pydantic import BaseModel
from fastapi import HTTPException

from app.database import get_session
from app.models.nurses import Handoffs
from app.schemas.nurses import GenerateSbarBase
from app.services.nurse_services import service_get_patient_data
from app.utility.constant import CHAT_GPT, CHAT_GPT_MODEL, STATUS_DRAFT
from app.utility.env import get_open_ai_key
from app.utility.others import construct_sbar_report
from sqlalchemy.exc import IntegrityError

from app.utility.prompt import system_prompt
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
def generate_sbar(patient_id: int, nurse_id: int, model: str):
    if model == CHAT_GPT:
        client = openai.OpenAI(api_key=get_open_ai_key())

        patient, vital_sign, medical_data, nurse_notes, nurses = service_get_patient_data(
            patient_id, nurse_id)

        user_prompt = (
            f"Generate a handoff report using the following: Patient Data : {patient},"
            f"Vital Signs : {vital_sign}, Medical Data : {medical_data}, Medical Data : {nurse_notes} , "
            f"Nurse Data : {nurses} ")

        response = client.beta.chat.completions.parse(
            model=CHAT_GPT_MODEL,
            messages=[
                {"role": "system",
                 "content": f"{system_prompt}"},
                {"role": "user", "content": f"{user_prompt}"}
            ],
            temperature=0,
            response_format=HandoffReport,
        )

        return response.choices[0].message.parsed


def service_generate_sbar(sbar: GenerateSbarBase):
    try:
        situation, background, assessment, recommendation, reported_by = generate_sbar(
            sbar.patient_id, sbar.outgoing_nurse_id, sbar.model)

        json_result = construct_sbar_report(situation[1], background[1],
                                            assessment[1],
                                            recommendation[1],
                                            reported_by[1])
        db_hand_offs = Handoffs(
            report_text=json_result,
            status=STATUS_DRAFT,
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
        1, 1)

    print(construct_sbar_report(situation[1], background[1], assessment[1],
                                recommendation[1], reported_by[1]))


if __name__ == '__main__':
    main()
