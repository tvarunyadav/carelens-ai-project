from datetime import datetime, date
from typing import List, Optional
from pydantic import BaseModel, Field, EmailStr

class HealthStatus(BaseModel):
    status: str = Field(..., description="System operational state, e.g., 'ok'")
    service: str = Field(..., description="Service identifier name")
    version: str = Field(..., description="Semantic version string")
    timestamp: datetime = Field(..., description="ISO 8601 UTC server timestamp")

class BoundingBox(BaseModel):
    x_min: float
    y_min: float
    x_max: float
    y_max: float

class Citation(BaseModel):
    id: str = Field(..., description="Unique citation identifier")
    document_id: str = Field(..., description="Source PDF document ID")
    document_name: str = Field(..., description="Human-readable filename")
    page_number: int = Field(..., ge=1, description="1-indexed PDF page number")
    text_snippet: str = Field(..., description="Exact textual excerpt from PDF")
    bounding_box: Optional[BoundingBox] = Field(None, description="Visual location on page")

class Claim(BaseModel):
    id: str = Field(..., description="Unique claim identifier")
    text: str = Field(..., description="Factual medical assertion extracted from answer")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Verification confidence score")
    citations: List[Citation] = Field(default_factory=list, description="Supporting document evidence")

class Patient(BaseModel):
    id: str = Field(..., description="Patient UUID")
    mrn: str = Field(..., description="Medical Record Number")
    first_name: str = Field(..., description="First name (synthetic)")
    last_name: str = Field(..., description="Last name (synthetic)")
    dob: date = Field(..., description="Date of birth")
    gender: str = Field(..., description="Gender designation")
    status: str = Field(default="active", description="Patient file status ('active' | 'archived')")
    record_version: int = Field(default=1, description="Record revision counter")
    created_at: datetime = Field(default_factory=datetime.utcnow)

class StaffProfile(BaseModel):
    id: str = Field(..., description="Supabase Auth User UUID")
    email: str = Field(..., description="Staff email address")
    full_name: str = Field(..., description="Full display name")
    role: str = Field(..., description="Role ('doctor' | 'coordinator' | 'admin')")
    created_at: Optional[datetime] = None

class PatientAccessGrant(BaseModel):
    id: str = Field(..., description="Grant UUID")
    staff_id: str = Field(..., description="Target staff UUID")
    patient_id: str = Field(..., description="Target patient UUID")
    action: str = Field(..., description="Granted action ('read' | 'write' | 'admin')")
    granted_by: Optional[str] = None
    granted_at: datetime = Field(default_factory=datetime.utcnow)

class PatientListResponse(BaseModel):
    patients: List[Patient] = Field(default_factory=list, description="List of permitted patient records")
    total: int = Field(..., description="Total count of authorized patients")

class Question(BaseModel):
    id: str = Field(..., description="Question UUID")
    patient_id: str = Field(..., description="Target patient ID")
    text: str = Field(..., description="Natural language question asked by staff")
    asked_by: str = Field(..., description="User ID or email of authorized staff")
    created_at: datetime = Field(default_factory=datetime.utcnow)

class TimelineEvent(BaseModel):
    id: str = Field(..., description="Timeline event ID")
    patient_id: str = Field(..., description="Target patient ID")
    event_date: date = Field(..., description="Clinical event date")
    category: str = Field(..., description="Category, e.g., 'Lab Result', 'Diagnosis', 'Medication'")
    summary: str = Field(..., description="Short event summary")
    document_id: Optional[str] = Field(None, description="Associated document ID")
