from datetime import datetime, timezone, date
from typing import Optional

from sqlmodel import Field, SQLModel
from sqlalchemy import JSON, Column


class Patients(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    first_name: str = Field(unique=False, index=True)
    last_name: str = Field(unique=False, index=True)
    birth_date: date
    medical_record_number: str = Field(unique=True, index=True)
    room_number: str
    admission_date: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    discharge_date: Optional[datetime]

    created_at: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    updated_at: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column_kwargs={"onupdate": lambda: datetime.now(timezone.utc)},
    )


class VitalSigns(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    time_stamp: Optional[datetime]
    blood_pressure_systolic: int
    blood_pressure_diastolic: int
    heart_rate: int
    respiratory_rate: int
    oxygen_saturation: int
    temperature: float
    source: str
    created_at: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    updated_at: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column_kwargs={"onupdate": lambda: datetime.now(timezone.utc)},
    )

    patient_id: int = Field(default=None, foreign_key="patients.id")


class VitalMedicalData(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    time_stamp: Optional[datetime]
    data_type: str
    data_value: dict = Field(default_factory=dict, sa_column=Column(JSON))
    source: str
    created_at: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    updated_at: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column_kwargs={"onupdate": lambda: datetime.now(timezone.utc)},
    )

    patient_id: int = Field(default=None, foreign_key="patients.id")


class NurseNotes(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    time_stamp: Optional[datetime]
    note_text: str
    category: str
    created_at: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    updated_at: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column_kwargs={"onupdate": lambda: datetime.now(timezone.utc)},
    )

    patient_id: int = Field(default=None, foreign_key="patients.id")
    nurse_id: int = Field(default=None, foreign_key="nurses.id")


class Nurses(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    first_name: str = Field(unique=False, index=True)
    last_name: str = Field(unique=False, index=True)
    license_number: str = Field(unique=True, index=True)

    created_at: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    updated_at: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column_kwargs={"onupdate": lambda: datetime.now(timezone.utc)},
    )


class Handoffs(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    report_text: dict = Field(default_factory=dict, sa_column=Column(JSON))
    status: str

    created_at: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    updated_at: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column_kwargs={"onupdate": lambda: datetime.now(timezone.utc)},
    )

    patient_id: int = Field(default=None, foreign_key="patients.id")
    outgoing_nurse_id: int = Field(default=None, foreign_key="nurses.id")
    incoming_nurse_id: int = Field(default=None, foreign_key="nurses.id")
