from fastapi import APIRouter, HTTPException, Depends, status

from app.models import Nurses
from app.models.nurses import Patients, VitalSigns, VitalMedicalData, \
    NurseNotes
from app.schemas.nurses import NursesBase, PatientsBase, VitalSignsBase, \
    VitalMedicalDataBase, NurseNotesBase
from app.services.nurse_services import get_nurse_by_id, get_patient_by_id, \
    service_create_nurse, service_create_patient, service_create_vital_signs, \
    service_create_vital_medical, service_create_nurse_note
from dependencies import get_current_active_user

router = APIRouter()


@router.get("/nurses/{nurse_id}", response_model=Nurses)
async def get_nurse(nurse_id: int,
                    current_user: dict = Depends(get_current_active_user)):
    db_nurse = get_nurse_by_id(nurse_id)
    if db_nurse is None:
        raise HTTPException(status_code=404, detail="Nurse not found")

    return db_nurse


@router.get("/patient/{patient_id}", response_model=Patients)
async def create_patient(patient_id: int,
                         current_user: dict = Depends(
                             get_current_active_user)):
    db_patient = get_patient_by_id(patient_id)
    if db_patient is None:
        raise HTTPException(status_code=404, detail="Patient not found")

    return db_patient


@router.post("/nurses/", response_model=Nurses,
             status_code=status.HTTP_201_CREATED, )
async def create_nurse(nurse: NursesBase,
                       current_user: dict = Depends(get_current_active_user)):
    db_nurse = service_create_nurse(nurse)
    return db_nurse


@router.post("/patients/", response_model=Patients,
             status_code=status.HTTP_201_CREATED)
async def create_patient(patient: PatientsBase,
                         current_user: dict = Depends(
                             get_current_active_user)):
    db_patient = service_create_patient(patient)
    return db_patient


@router.post("/vital_signs/", response_model=VitalSigns,
             status_code=status.HTTP_201_CREATED)
async def create_vital_signs(vital_signs: VitalSignsBase,
                             current_user: dict = Depends(
                                 get_current_active_user)):
    db_vital_signs = service_create_vital_signs(vital_signs)
    return db_vital_signs


@router.post("/vital_medical/", response_model=VitalMedicalData,
             status_code=status.HTTP_201_CREATED)
async def create_medical_data(vital_medical: VitalMedicalDataBase,
                              current_user: dict = Depends(
                                  get_current_active_user)):
    db_vital_medical = service_create_vital_medical(vital_medical)
    return db_vital_medical


@router.post("/nurse_notes/", response_model=NurseNotes,
             status_code=status.HTTP_201_CREATED)
async def create_nurse_notes(nurse_notes: NurseNotesBase,
                             current_user: dict = Depends(
                                 get_current_active_user)):
    db_nurse_notes = service_create_nurse_note(nurse_notes)
    return db_nurse_notes
