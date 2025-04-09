import openai
import json
from google import genai
from groq import Groq

from pydantic import BaseModel
from fastapi import HTTPException
from openai import OpenAI

from app.database import get_session
from app.models.nurses import Handoffs
from app.schemas.nurses import GenerateSbarBase
from app.services.nurse_services import get_latest_handoff, get_nurse_by_id, \
    get_nurse_notes_by_patient_id_by_shift, get_patient_data, \
    get_vital_signs_by_patient_id_by_shift, \
    get_medical_data_by_patient_id_by_shift
from app.utility.constant import CHAT_GPT, STATUS_DRAFT, \
    GEMINI, GROQ, XAI, XAI_BASEURL, CHAT_GPT_PRICE_PER_TOKEN, GEMINI_PRICE_PER_TOKEN, LLAMA_PRICE_PER_TOKEN, \
    XAI_PRICE_PER_TOKEN
from app.utility.env import get_open_ai_key, get_gemini_key, get_groq_key, \
    get_groq_model, get_gemini_model, get_open_ai_model, get_xai_key, \
    get_xai_model
from app.utility.others import construct_sbar_report
from sqlalchemy.exc import IntegrityError

from app.utility.prompt import system_prompt_regeneration_sbar_main, \
    system_prompt_regeneration_sbar_body, system_prompt_generate
from ratelimit import limits, sleep_and_retry

from app.utility.rag_qa import generate_user_message


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
    patient = get_patient_data(patient_id)

    vital_signs = get_vital_signs_by_patient_id_by_shift(patient_id)

    medical_data = get_medical_data_by_patient_id_by_shift(patient_id)

    nurse = get_nurse_by_id(nurse_id)

    nurse_notes = get_nurse_notes_by_patient_id_by_shift(patient_id, nurse_id)

    if is_regenerate_sbar:

        hand_off = get_latest_handoff(patient_id, nurse_id, model)

        user_prompt = (
            f"Regenerate SBAR using the following:\n Patient Data : {patient},"
            f"\nVital Signs : {vital_signs}, \nMedical Data : {medical_data}, \nNurse Notes : {nurse_notes} , "
            f"Nurse Data : {nurse} ")

        system_prompt = system_prompt_regeneration_sbar_main + str(
            hand_off.report_text) + system_prompt_regeneration_sbar_body
    else:
        user_prompt = (
            f"Generate a SBAR using the following:\n Patient Data : {patient},"
            f"\nVital Signs : {vital_signs}, \nMedical Data : {medical_data}, \nNurse Notes : {nurse_notes} , "
            f"Nurse Data : {nurse} ")

        system_prompt = system_prompt_generate

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

        return response.choices[0].message.parsed, response.usage

    # Check for the temperature
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
        return response.parsed, response.usage_metadata

    elif model == GROQ:
        client = Groq(api_key=get_groq_key())

        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": f"{system_prompt}"
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

        return HandoffReport.model_validate_json(chat_completion.choices[0].message.content), chat_completion.usage

    elif model == XAI:
        client = OpenAI(
            api_key=get_xai_key(),
            base_url=XAI_BASEURL,
        )

        completion = client.beta.chat.completions.parse(
            model=get_xai_model(),
            messages=[
                {"role": "system",
                 "content": f"{system_prompt}"},
                {"role": "user",
                 "content": f"{user_prompt}"}
            ],
            response_format=HandoffReport,
        )
        return completion.choices[0].message.parsed, completion.usage


def service_generate_sbar(sbar: GenerateSbarBase, is_regenerated: bool):
    try:
        response_sbar, token_usage = (
            generate_sbar(sbar.patient_id, sbar.outgoing_nurse_id, sbar.model.value, is_regenerated))

        situation = response_sbar.situation
        background = response_sbar.background
        assessment = response_sbar.assessment
        recommendation = response_sbar.recommendation
        reported_by = response_sbar.reported_by

        if sbar.model.value == CHAT_GPT or sbar.model.value == XAI:
            prompt_tokens = token_usage.prompt_tokens
            completion_tokens = token_usage.completion_tokens
            total_tokens = token_usage.total_tokens
            cost_estimate = total_tokens * CHAT_GPT_PRICE_PER_TOKEN

        elif sbar.model.value == GROQ:
            prompt_tokens = token_usage.prompt_tokens
            completion_tokens = token_usage.completion_tokens
            total_tokens = token_usage.total_tokens
            cost_estimate = total_tokens * LLAMA_PRICE_PER_TOKEN

        elif sbar.model.value == XAI:
            prompt_tokens = token_usage.prompt_tokens
            completion_tokens = token_usage.completion_tokens
            total_tokens = token_usage.total_tokens
            cost_estimate = total_tokens * XAI_PRICE_PER_TOKEN

        elif sbar.model.value == GEMINI:
            prompt_tokens = token_usage.total_token_count
            completion_tokens = token_usage.candidates_token_count
            total_tokens = token_usage.total_token_count
            cost_estimate = total_tokens * GEMINI_PRICE_PER_TOKEN

        json_result = construct_sbar_report(situation, background,
                                            assessment,
                                            recommendation,
                                            reported_by,
                                            prompt_tokens,
                                            completion_tokens,
                                            total_tokens,
                                            cost_estimate
                                            )

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
        return json.loads(json_result)

    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=400,
                            detail="Error adding handoffs")


def service_chat_patient(message: str, thread_id: str):
    return generate_user_message(message, thread_id)


def main():
    # situation, background, assessment, recommendation, reported_by = generate_sbar(1, 2, CHAT_GPT, False)

    response_sbar, token_usage = generate_sbar(
        3, 2, XAI, False)

    print("--------------------------------------------------------------------------------------------------")
    print(response_sbar)
    print("--------------------------------------------------------------------------------------------------")
    print(token_usage)
    print("--------------------------------------------------------------------------------------------------")


if __name__ == '__main__':
    main()
