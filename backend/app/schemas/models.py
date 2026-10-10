from datetime import datetime, date
from typing import List, Optional, Any, Dict
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
    user_grant: Optional[str] = Field(default=None, description="Backend-confirmed grant action for current staff ('read' | 'write' | 'admin')")
    can_write: Optional[bool] = Field(default=None, description="Whether current staff has backend-confirmed write or admin grant for this patient")
    created_at: Optional[datetime] = None

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
    granted_at: Optional[datetime] = None

class PatientListResponse(BaseModel):
    patients: List[Patient] = Field(default_factory=list, description="List of permitted patient records")
    total: int = Field(..., description="Total count of authorized patients")

class DocumentItem(BaseModel):
    id: str = Field(..., description="Document UUID")
    patient_id: str = Field(..., description="Patient UUID owner")
    title: str = Field(..., description="Document title")
    doc_type: str = Field(..., description="Document clinical category type")
    clinical_date: date = Field(..., description="Clinical date of record")
    status: str = Field(default="final", description="Status ('final' | 'pending' | 'archived' | 'draft')")
    storage_path: Optional[str] = Field(None, description="Storage path in patient-documents bucket")
    mime_type: str = Field(default="application/pdf", description="MIME type")
    file_size: int = Field(default=0, description="File byte size")
    current_version: int = Field(default=1, description="Current active version number")
    created_at: Optional[datetime] = None

class DocumentVersionItem(BaseModel):
    id: str = Field(..., description="Document version UUID")
    document_id: str = Field(..., description="Parent document UUID")
    version_number: int = Field(..., description="Version number counter")
    storage_path: str = Field(..., description="Storage path for version")
    extracted_text: Optional[str] = Field(None, description="Extracted textual content")
    page_count: int = Field(default=1, description="Page count")
    extraction_status: str = Field(default="processed", description="Extraction state ('pending' | 'processed' | 'failed')")
    created_at: Optional[datetime] = None

class DocumentListResponse(BaseModel):
    documents: List[DocumentItem] = Field(default_factory=list)
    total: int

class TimelineEventItem(BaseModel):
    id: str = Field(..., description="Timeline event UUID")
    patient_id: str = Field(..., description="Target patient UUID")
    event_date: date = Field(..., description="Clinical event date")
    event_type: str = Field(..., description="Event type ('visit' | 'lab_result' | 'procedure' | 'medication' | 'fertility_cycle' | 'follow_up' | 'pending_order')")
    title: str = Field(..., description="Event title")
    summary: str = Field(..., description="Short event summary")
    document_id: Optional[str] = Field(None, description="Associated document ID")
    metadata_json: Dict[str, Any] = Field(default_factory=dict)
    created_at: Optional[datetime] = None

class TimelineListResponse(BaseModel):
    events: List[TimelineEventItem] = Field(default_factory=list)
    total: int

class FertilityCycleItem(BaseModel):
    id: str = Field(..., description="Cycle UUID")
    patient_id: str = Field(..., description="Target patient UUID")
    cycle_name: str = Field(..., description="Cycle title / description")
    start_date: date = Field(..., description="Cycle start date")
    end_date: Optional[date] = Field(None, description="Cycle end date")
    status: str = Field(default="completed", description="Cycle status ('active' | 'completed' | 'cancelled')")
    notes_json: Dict[str, Any] = Field(default_factory=dict)
    created_at: Optional[datetime] = None

class FertilityCycleListResponse(BaseModel):
    cycles: List[FertilityCycleItem] = Field(default_factory=list)
    total: int

class DocumentSourceResponse(BaseModel):
    document_id: str = Field(..., description="Document ID")
    title: str = Field(..., description="Document title")
    download_url: str = Field(..., description="Authorized presigned or proxy stream URL")
    expires_in_seconds: int = Field(default=3600, description="Expiration TTL in seconds")
    mime_type: str = Field(default="application/pdf", description="Document MIME type")

class AIQueryRequest(BaseModel):
    query: Optional[str] = Field(None, description="Optional question text for plain-language query")
    input_mode: Optional[str] = Field("typed", description="Input mode ('typed' | 'voice')")
    input_language: Optional[str] = Field("en", description="Input language ('en' | 'ta')")
    answer_language: Optional[str] = Field("en", description="Answer language ('en' | 'ta')")

class AIEvidenceItem(BaseModel):
    id: str = Field(..., description="Unique evidence citation marker (e.g. EV-1)")
    type: str = Field(..., description="Evidence type ('document_chunk' | 'fertility_cycle' | 'pending_order' | 'timeline_event')")
    title: str = Field(..., description="Document or record title")
    document_id: Optional[str] = Field(None, description="Document UUID")
    document_version_id: Optional[str] = Field(None, description="Document version UUID")
    page_number: Optional[int] = Field(None, description="1-indexed PDF page number")
    date: Optional[str] = Field(None, description="Clinical date string")
    snippet: str = Field(..., description="Extracted evidence text excerpt")

class AIResponse(BaseModel):
    status: str = Field(..., description="Completion status ('success' | 'ai_not_configured' | 'error')")
    answer: str = Field(..., description="Grounded answer text (always in English)")
    provider: str = Field(..., description="LLM model provider used")
    evidence: List[AIEvidenceItem] = Field(default_factory=list, description="All retrieved context items")
    evidence_citations: List[str] = Field(default_factory=list, description="Cited evidence IDs")
    evidence_limitations: Optional[str] = Field(None, description="Notes on evidence limits or null")
    detected_language: Optional[str] = Field("en", description="Detected question language ('en' | 'ta' | 'mixed')")
    tamil_audio_text: Optional[str] = Field(None, description="Optional Tamil audio readout translation for Tamil/mixed questions")

