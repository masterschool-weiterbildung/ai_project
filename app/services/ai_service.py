from datetime import datetime
from pydantic import BaseModel

import openai

from app.services.nurse_services import service_get_patient_data
from app.utility.env import get_open_ai_key


def generate_sbar(patient_id: int, nurse_id: int):
    # if model
    client = openai.OpenAI(api_key=get_open_ai_key())

    model = "gpt-4o-mini"

    patient, vital_sign, medical_data, nurse_notes, nurses = service_get_patient_data(
        patient_id, nurse_id);

    user_prompt = (
        f"Generate a handoff report using the following: Patient Data : {patient},"
        f"Vital Signs : {vital_sign}, Medical Data : {medical_data}, Medical Data : {nurse_notes} , "
        f"Nurse Data : {nurses} ")

    system_prompt = """"
        You are a nurse preparing a handoff report for the incoming shift. 
        Your task is to generate a structured SBAR report based on patient data.
        
        SBAR stands for Situation, Background, Assessment, and Recommendation. 
        It’s a standardized communication framework used in healthcare to organize and deliver critical 
        patient information, especially during handoffs. It ensures that essential details are conveyed clearly, 
        reducing the risk of miscommunication and improving patient safety. Here’s a detailed breakdown of each component:
        
        Situation
        
        - Patient identifiers (name, age, room number).
        - Current vital signs (e.g., blood pressure, heart rate, oxygen levels).
        - Any urgent issues or changes (e.g., "Patient is experiencing chest pain").
        
        Background
        
        - Primary diagnosis and reason for admission.
        - Key medical history (e.g., chronic conditions, allergies).
        - Recent treatments or interventions (e.g., medications given, procedures done).
        
        Assessment
        
        - Changes or trends in the patient’s status (e.g., "Symptoms are improving").
        - Interpretation of data (e.g., "Vital signs are stable but pain persists").
        - Any concerns or uncertainties (e.g., "Not sure if nausea is medication-related").
        
        Recommendation
        
        - Monitoring instructions (e.g., "Check vitals every 4 hours").
        - Alerts (e.g., "Patient is a fall risk").
        - Follow-up actions (e.g., "Give pain medication at 8 PM").
        
        ReportedBy
        
        - Nurse Name
        - License Number
        - Data and Time
    """

    class Situation(BaseModel):
        patient_name: str
        mrn: str
        age: int
        gender: str
        room_number: int
        date_time: str
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
        date_time: str

    class HandoffReport(BaseModel):
        situation: Situation
        background: Background
        assessment: Assessment
        recommendation: Recommendation
        reported_by: ReportedBy

    response = client.beta.chat.completions.parse(
        model=model,

        ### SBAR explain in details more data
        messages=[
            {"role": "system",
             "content": f"{system_prompt}"},
            {"role": "user", "content": f"{user_prompt}"}
        ],
        temperature=0,
        response_format=HandoffReport,
    )

    print("Generated text:\n", response.choices[0].message.content)

    return response.choices[0].message.content


def main():
    print(generate_sbar(1, 1))


if __name__ == '__main__':
    main()
