from datetime import date, datetime
from pydantic import BaseModel, Field
from enum import Enum

from app.utility import constant


class PatientsBase(BaseModel):
    first_name: str
    last_name: str
    sex: str
    birth_date: date = None
    medical_record_number: str
    room_number: str
    admission_date: datetime = None

    class Config:
        from_attributes = True


class Patients(PatientsBase):
    id: int

    class Config:
        from_attributes = True


class VitalSignsBase(BaseModel):
    time_stamp: datetime = None
    blood_pressure_systolic: int
    blood_pressure_diastolic: int
    heart_rate: int
    respiratory_rate: int
    oxygen_saturation: int
    temperature: float
    source: str
    patient_id: int

    class Config:
        from_attributes = True


class VitalSigns(VitalSignsBase):
    id: int

    class Config:
        from_attributes = True


class VitalMedicalDataBase(BaseModel):
    time_stamp: datetime = None
    data_type: str
    data_value: dict
    source: str
    patient_id: int

    class Config:
        from_attributes = True


class VitalMedicalData(VitalMedicalDataBase):
    id: int

    class Config:
        from_attributes = True


class NurseNotesBase(BaseModel):
    time_stamp: datetime = None
    note_text: str
    category: str
    patient_id: int
    nurse_id: int

    class Config:
        from_attributes = True


class NurseNotes(NurseNotesBase):
    id: int

    class Config:
        from_attributes = True


class NursesBase(BaseModel):
    first_name: str
    last_name: str
    license_number: str

    class Config:
        from_attributes = True


class Nurses(NursesBase):
    id: int

    class Config:
        from_attributes = True


class HandoffsBase(BaseModel):
    report_text: str
    status: str
    model: str
    patient_id: int
    outgoing_nurse_id: int
    incoming_nurse_id: int

    class Config:
        from_attributes = True


class Handoffs(HandoffsBase):
    id: int

    class Config:
        from_attributes = True


class CLIENTS(Enum):
    CHAT_GPT = constant.CHAT_GPT
    GEMINI = constant.GEMINI
    GROQ = constant.GROQ
    XAI = constant.XAI


class GenerateSbarBase(BaseModel):
    patient_id: int
    outgoing_nurse_id: int
    incoming_nurse_id: int
    model: CLIENTS

    class Config:
        from_attributes = True


class GenerateSbar(BaseModel):
    patient_id: int
    nurse_id: int
    model: str = Field(default="chatgpt")

    class Config:
        from_attributes = True


class ChatBot(BaseModel):
    message: str
    thread_id: str

    class Config:
        from_attributes = True
