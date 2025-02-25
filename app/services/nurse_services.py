from app.database import get_session
from app.models.nurses import Patients, VitalSigns, VitalMedicalData, \
    NurseNotes, Nurses, Handoffs
from app.schemas.nurses import PatientsBase, VitalSignsBase, \
    VitalMedicalDataBase, NurseNotesBase, NursesBase, HandoffsBase
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlmodel import select


def get_patient_by_id(patient_id: int) -> Patients:
    with get_session() as session:
        statement = select(Patients).where(Patients.id == patient_id)
        results = session.exec(statement)
        return results.first()


def get_vital_signs_by_patient_id(patient_id: int) -> VitalSigns:
    with get_session() as session:
        statement = select(VitalSigns).where(
            VitalSigns.patient_id == patient_id)
        results = session.exec(statement)
        return results.first()


def get_vital_medical_data_by_patient_id(patient_id: int) -> VitalMedicalData:
    with get_session() as session:
        statement = select(VitalMedicalData).where(
            VitalMedicalData.patient_id == patient_id)
        results = session.exec(statement)
        return results.first()


def get_nurse_notes_by_patient_id(patient_id: int,
                                  nurse_id: int) -> NurseNotes:
    with get_session() as session:
        statement = select(NurseNotes).where(
            NurseNotes.patient_id == patient_id).where(
            NurseNotes.nurse_id == nurse_id)
        results = session.exec(statement)
        return results.first()


def get_patient_data(patient_id: int, nurse_id: int):
    with (get_session() as session):
        statement = select(Patients, VitalSigns, VitalMedicalData,
                           NurseNotes, Nurses).where(
            Patients.id == patient_id).join(VitalSigns).where(
            VitalSigns.patient_id == patient_id).join(VitalMedicalData).where(
            VitalMedicalData.patient_id == patient_id).join(NurseNotes).where(
            NurseNotes.patient_id == patient_id).where(
            NurseNotes.nurse_id == nurse_id).join(Nurses).where(
            NurseNotes.nurse_id == Nurses.id)

        results = session.exec(statement)
        return results.all()


def get_nurse_by_id(nurse_id: int) -> Nurses:
    with get_session() as session:
        statement = select(Nurses).where(Nurses.id == nurse_id)
        results = session.exec(statement)
        return results.first()


def service_create_patient(patient: PatientsBase) -> Patients:
    try:
        db_patients = Patients(
            first_name=patient.first_name,
            last_name=patient.last_name,
            birth_date=patient.birth_date,
            medical_record_number=patient.medical_record_number,
            room_number=patient.room_number,
            admission_date=patient.admission_date,
        )

        with get_session() as session:
            session.add(db_patients)
            session.commit()
            session.refresh(db_patients)
            return db_patients
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=409,
                            detail="Patient already exists")


def service_create_vital_signs(vital_signs: VitalSignsBase) -> VitalSigns:
    patient = get_patient_by_id(vital_signs.patient_id)
    if patient is None:
        raise HTTPException(status_code=404, detail="Patient not found")

    try:
        db_vital_sign = VitalSigns(
            time_stamp=vital_signs.time_stamp,
            blood_pressure_systolic=vital_signs.blood_pressure_systolic,
            blood_pressure_diastolic=vital_signs.blood_pressure_diastolic,
            heart_rate=vital_signs.heart_rate,
            respiratory_rate=vital_signs.respiratory_rate,
            oxygen_saturation=vital_signs.oxygen_saturation,
            temperature=vital_signs.temperature,
            source=vital_signs.source,
            patient_id=patient.id
        )

        with get_session() as session:
            session.add(db_vital_sign)
            session.commit()
            session.refresh(db_vital_sign)
            return db_vital_sign
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=409,
                            detail="Error adding vital signs")


def service_create_vital_medical(
        vital_medical: VitalMedicalDataBase) -> VitalMedicalData:
    patient = get_patient_by_id(vital_medical.patient_id)
    if patient is None:
        raise HTTPException(status_code=404, detail="Patient not found")

    try:
        db_vital_medical = VitalMedicalData(
            time_stamp=vital_medical.time_stamp,
            data_type=vital_medical.data_type,
            data_value=vital_medical.data_value,
            source=vital_medical.source,
            patient_id=patient.id
        )

        with get_session() as session:
            session.add(db_vital_medical)
            session.commit()
            session.refresh(db_vital_medical)
            return db_vital_medical
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=409,
                            detail="Error adding vital medical")


def service_create_nurse_note(
        nurse_note: NurseNotesBase) -> NurseNotes:
    patient = get_patient_by_id(nurse_note.patient_id)
    if patient is None:
        raise HTTPException(status_code=404, detail="Patient not found")

    try:
        db_nurse_notes = NurseNotes(
            time_stamp=nurse_note.time_stamp,
            note_text=nurse_note.note_text,
            category=nurse_note.category,
            patient_id=nurse_note.patient_id,
            nurse_id=nurse_note.nurse_id
        )

        with get_session() as session:
            session.add(db_nurse_notes)
            session.commit()
            session.refresh(db_nurse_notes)
            return db_nurse_notes
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=400,
                            detail="Error adding nurse notes")


def service_create_nurse(nurse: NursesBase) -> Nurses:
    try:
        db_nurse = Nurses(
            first_name=nurse.first_name,
            last_name=nurse.last_name,
            license_number=nurse.license_number
        )

        with get_session() as session:
            session.add(db_nurse)
            session.commit()
            session.refresh(db_nurse)
            return db_nurse
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=409,
                            detail="Nurse already exists")


def service_create_handoffs(handoffs: HandoffsBase) -> Handoffs:
    try:
        db_handoffs = Handoffs(
            report_text=handoffs.report_text,
            status=handoffs.status,
            patient_id=handoffs.patient_id,
            outgoing_nurse_id=handoffs.outgoing_nurse_id,
            incoming_nurse_id=handoffs.incoming_nurse_id
        )

        with get_session() as session:
            session.add(db_handoffs)
            session.commit()
            session.refresh(db_handoffs)
            return db_handoffs
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=400,
                            detail="Error in adding Handoffs")


def service_get_patient_data(patient_id: int, nurse_id: int):
    result = get_patient_data(patient_id, nurse_id);
    for row in result:
        patient, vital_sign, medical_data, nurse_notes, nurses = row

    return patient, vital_sign, medical_data, nurse_notes, nurses


def main():
    patient, vital_sign, medical_data, nurse_notes, nurses = service_get_patient_data(
        1, 1);

    print(nurses)


if __name__ == '__main__':
    main()
