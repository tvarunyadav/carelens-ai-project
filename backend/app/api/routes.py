import os
from datetime import datetime, timezone
from typing import Optional, List
from fastapi import APIRouter, Depends, Security, Query, HTTPException, status, UploadFile, File
from fastapi.responses import FileResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.schemas.models import (
    HealthStatus, StaffProfile, Patient, PatientListResponse,
    TimelineEventItem, TimelineListResponse,
    DocumentItem, DocumentListResponse,
    FertilityCycleItem, FertilityCycleListResponse,
    DocumentSourceResponse, AIQueryRequest, AIResponse
)
from app.core.config import settings
from app.auth.verifier import verify_supabase_token, security
from app.patients.service import PatientService
from app.audit.service import AuditService
from app.retrieval.retrieval_service import RetrievalService
from app.retrieval.llm_service import LLMService
from app.documents.intake_service import DocumentIntakeService

router = APIRouter()


# --- Milestone 1 Endpoint (Preserved) ---
@router.get("/health", response_model=HealthStatus, summary="Check service health and readiness")
async def health_check():
    """
    Public readiness endpoint for infrastructure and frontend checks.
    Returns service metadata without exposing sensitive credentials or system internals.
    """
    return HealthStatus(
        status="ok",
        service=settings.APP_NAME,
        version=settings.API_VERSION,
        timestamp=datetime.now(timezone.utc)
    )



# --- Milestone 2 Endpoints (Auth & Patient Directory) ---

@router.get(
    "/api/v1/me",
    response_model=StaffProfile,
    summary="Get verified staff profile",
    tags=["Auth & Identity"]
)
async def get_current_staff_profile(current_staff: StaffProfile = Depends(verify_supabase_token)):
    """
    Returns verified clinic staff profile extracted from authenticated Supabase JWT.
    Rejects unauthenticated requests with 401 Unauthorized.
    """
    return current_staff


@router.get(
    "/api/v1/patients",
    response_model=PatientListResponse,
    summary="List authorized synthetic patient records",
    tags=["Patient Directory"]
)
async def list_permitted_patients(
    current_staff: StaffProfile = Depends(verify_supabase_token),
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security)
):
    """
    Returns only the patient records for which the verified staff member holds an explicit grant.
    Enforces patient access isolation across all roles.
    """
    token = credentials.credentials.strip() if credentials else ""
    permitted_patients = await PatientService.get_permitted_patients_for_staff(current_staff, token)
    return PatientListResponse(
        patients=permitted_patients,
        total=len(permitted_patients)
    )


@router.get(
    "/api/v1/patients/{patient_id}",
    response_model=Patient,
    summary="Get specific synthetic patient record details",
    tags=["Patient Directory"]
)
async def get_patient_detail(
    patient_id: str,
    current_staff: StaffProfile = Depends(verify_supabase_token),
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security)
):
    """
    Authorizes detail access BEFORE returning patient information.
    Raises 403 Forbidden if the staff member does not hold an explicit access grant.
    """
    token = credentials.credentials.strip() if credentials else ""
    return await PatientService.get_patient_detail_for_staff(patient_id, current_staff, token)


# --- Milestone 3 Endpoints (Patient Workspace: Timeline, Documents, Cycles) ---

@router.get(
    "/api/v1/patients/{patient_id}/timeline",
    response_model=TimelineListResponse,
    summary="Get authorized patient timeline events",
    tags=["Patient Workspace"]
)
async def get_patient_timeline(
    patient_id: str,
    event_type: Optional[str] = Query(None, description="Optional filter by event_type"),
    current_staff: StaffProfile = Depends(verify_supabase_token),
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security)
):
    token = credentials.credentials.strip() if credentials else ""
    events = await PatientService.get_patient_timeline(patient_id, current_staff, token, event_type)
    return TimelineListResponse(events=events, total=len(events))


@router.get(
    "/api/v1/patients/{patient_id}/documents",
    response_model=DocumentListResponse,
    summary="List authorized patient document records",
    tags=["Patient Workspace"]
)
async def get_patient_documents(
    patient_id: str,
    doc_type: Optional[str] = Query(None, description="Optional filter by doc_type"),
    current_staff: StaffProfile = Depends(verify_supabase_token),
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security)
):
    token = credentials.credentials.strip() if credentials else ""
    documents = await PatientService.get_patient_documents(patient_id, current_staff, token, doc_type)
    return DocumentListResponse(documents=documents, total=len(documents))


@router.get(
    "/api/v1/patients/{patient_id}/documents/{document_id}",
    response_model=DocumentItem,
    summary="Get authorized patient document detail",
    tags=["Patient Workspace"]
)
async def get_patient_document_detail(
    patient_id: str,
    document_id: str,
    current_staff: StaffProfile = Depends(verify_supabase_token),
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security)
):
    token = credentials.credentials.strip() if credentials else ""
    return await PatientService.get_patient_document_detail(patient_id, document_id, current_staff, token)


@router.get(
    "/api/v1/patients/{patient_id}/documents/{document_id}/source-url",
    response_model=DocumentSourceResponse,
    summary="Get authorized presigned or proxy source URL for original document",
    tags=["Patient Workspace"]
)
async def get_document_source_url(
    patient_id: str,
    document_id: str,
    current_staff: StaffProfile = Depends(verify_supabase_token),
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security)
):
    token = credentials.credentials.strip() if credentials else ""
    return await PatientService.get_document_source_url(patient_id, document_id, current_staff, token)


@router.get(
    "/api/v1/patients/{patient_id}/documents/{document_id}/download",
    summary="Stream original synthetic PDF document file",
    tags=["Patient Workspace"]
)
async def download_patient_document_file(
    patient_id: str,
    document_id: str,
    version_id: Optional[str] = Query(None),
    current_staff: StaffProfile = Depends(verify_supabase_token),
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security)
):
    token = credentials.credentials.strip() if credentials else ""
    doc = await PatientService.get_patient_document_detail(patient_id, document_id, current_staff, token)

    if doc.status == "pending" or not doc.storage_path:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Result not yet recorded for pending order"
        )

    target_rel_path = doc.storage_path
    if version_id:
        ver_info = await PatientService.get_document_version_by_id(document_id, version_id, current_staff, token)
        if ver_info and ver_info.get("file_path"):
            target_rel_path = ver_info["file_path"]

    filename = os.path.basename(target_rel_path)
    
    candidates = [
        target_rel_path,
        os.path.abspath(target_rel_path),
        os.path.abspath(os.path.join("scratch", "storage", target_rel_path)),
        os.path.abspath(os.path.join("backend", "scratch", "storage", target_rel_path)),
        os.path.abspath(os.path.join("backend", "storage", "patient_documents", filename)),
        os.path.abspath(os.path.join("storage", "patient_documents", filename))
    ]

    filepath = None
    for cand in candidates:
        if cand and os.path.exists(cand) and os.path.isfile(cand):
            filepath = cand
            break

    if not filepath:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Synthetic document file not found on server storage"
        )

    AuditService.log_event_background(
        current_staff.id,
        patient_id,
        "OPEN_DOCUMENT_SOURCE",
        f"/api/v1/patients/{patient_id}/documents/{document_id}/download",
        {"document_title": doc.title, "version_id": version_id},
        token
    )

    mime_type = doc.mime_type or "application/pdf"
    if filename.lower().endswith(".png"):
        mime_type = "image/png"
    elif filename.lower().endswith((".jpg", ".jpeg")):
        mime_type = "image/jpeg"

    return FileResponse(filepath, media_type=mime_type, filename=filename)


@router.get(
    "/api/v1/patients/{patient_id}/cycles",
    response_model=FertilityCycleListResponse,
    summary="List authorized fertility cycles",
    tags=["Patient Workspace"]
)
async def get_patient_cycles(
    patient_id: str,
    current_staff: StaffProfile = Depends(verify_supabase_token),
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security)
):
    token = credentials.credentials.strip() if credentials else ""
    cycles = await PatientService.get_fertility_cycles(patient_id, current_staff, token)
    return FertilityCycleListResponse(cycles=cycles, total=len(cycles))


# --- Milestone 4 Endpoints (Grounded AI History Assistant) ---

@router.post(
    "/api/v1/patients/{patient_id}/ai/summary",
    response_model=AIResponse,
    summary="Generate grounded patient history summary",
    tags=["History Assistant"]
)
async def generate_patient_history_summary(
    patient_id: str,
    current_staff: StaffProfile = Depends(verify_supabase_token),
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security)
):
    token = credentials.credentials.strip() if credentials else ""
    summary_data = await RetrievalService.generate_patient_summary(patient_id, current_staff, token)
    
    AuditService.log_event_background(
        current_staff.id,
        patient_id,
        "GENERATE_PATIENT_SUMMARY",
        f"/api/v1/patients/{patient_id}/ai/summary",
        {"provider": summary_data.get("provider"), "evidence_count": len(summary_data.get("evidence", []))},
        token
    )
    return AIResponse(**summary_data)

@router.post(
    "/api/v1/patients/{patient_id}/ai/query",
    response_model=AIResponse,
    summary="Answer plain-language question about patient history",
    tags=["History Assistant"]
)
async def answer_patient_history_query(
    patient_id: str,
    request: AIQueryRequest,
    current_staff: StaffProfile = Depends(verify_supabase_token),
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security)
):
    token = credentials.credentials.strip() if credentials else ""
    query_text = (request.query or "").strip()
    if not query_text:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Question query text cannot be empty.")

    input_mode = request.input_mode or "typed"

    query_data = await RetrievalService.answer_patient_query(
        patient_id, query_text, current_staff, token
    )
    
    AuditService.log_event_background(
        current_staff.id,
        patient_id,
        "QUERY_PATIENT_HISTORY",
        f"/api/v1/patients/{patient_id}/ai/query",
        {
            "provider": query_data.get("provider"),
            "evidence_count": len(query_data.get("evidence", [])),
            "input_mode": input_mode,
            "detected_language": query_data.get("detected_language", "en"),
            "status": query_data.get("status")
        },
        token
    )
    return AIResponse(**query_data)


ALLOWED_AUDIO_TYPES = {"audio/webm", "audio/wav", "audio/mp3", "audio/mpeg", "audio/ogg", "audio/m4a", "audio/x-m4a", "audio/mp4", "application/octet-stream"}
ALLOWED_AUDIO_EXTS = {".webm", ".wav", ".mp3", ".ogg", ".m4a", ".mp4"}
MAX_AUDIO_BYTES = 10 * 1024 * 1024  # 10 MB

@router.post(
    "/api/v1/speech/transcribe",
    summary="Transcribe spoken audio with automatic language detection",
    tags=["Speech"]
)
async def transcribe_speech_audio(
    file: UploadFile = File(...),
    current_staff: StaffProfile = Depends(verify_supabase_token),
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security)
):
    if not file:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No audio file uploaded.")

    content_type = (file.content_type or "").lower()
    filename = (file.filename or "").lower()
    ext = os.path.splitext(filename)[1] if filename else ""

    if content_type not in ALLOWED_AUDIO_TYPES and ext not in ALLOWED_AUDIO_EXTS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported audio format. Supported formats: WEBM, WAV, MP3, OGG, M4A."
        )

    audio_bytes = await file.read()
    if not audio_bytes or len(audio_bytes) < 100:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Audio recording is empty or unreadable.")

    if len(audio_bytes) > MAX_AUDIO_BYTES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Audio recording exceeds maximum allowed size limit of 10 MB."
        )

    try:
        transcript, detected_lang = await LLMService.transcribe_audio(audio_bytes, file.filename or "speech.webm")
        return {
            "status": "success",
            "transcript": transcript,
            "detected_language": detected_lang
        }
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Speech transcription service temporarily unavailable.")


# --- Milestone 6 Endpoints: Secure Document Intake, Review & Version Control ---

@router.post(
    "/api/v1/patients/{patient_id}/documents/upload",
    summary="Upload a new clinical document (PDF, PNG, JPEG)",
    tags=["Documents"]
)
async def upload_patient_document(
    patient_id: str,
    file: UploadFile = File(...),
    current_staff: StaffProfile = Depends(verify_supabase_token),
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security)
):
    token = credentials.credentials.strip() if credentials else ""
    return await DocumentIntakeService.upload_document(patient_id, file, current_staff, token)


@router.post(
    "/api/v1/patients/{patient_id}/documents/{document_id}/versions/upload",
    summary="Upload a new version N+1 for an existing document",
    tags=["Documents"]
)
async def upload_patient_document_version(
    patient_id: str,
    document_id: str,
    file: UploadFile = File(...),
    current_staff: StaffProfile = Depends(verify_supabase_token),
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security)
):
    token = credentials.credentials.strip() if credentials else ""
    return await DocumentIntakeService.upload_new_version(patient_id, document_id, file, current_staff, token)


@router.post(
    "/api/v1/patients/{patient_id}/documents/{document_id}/review",
    summary="Review metadata, extracted text, and publish document to vector retrieval index",
    tags=["Documents"]
)
async def review_and_publish_document(
    patient_id: str,
    document_id: str,
    payload: dict,
    current_staff: StaffProfile = Depends(verify_supabase_token),
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security)
):
    token = credentials.credentials.strip() if credentials else ""
    return await DocumentIntakeService.review_and_publish_document(patient_id, document_id, payload, current_staff, token)


@router.get(
    "/api/v1/patients/{patient_id}/documents/{document_id}/versions",
    summary="Get complete version history for a document with diff metrics",
    tags=["Documents"]
)
async def get_document_version_history(
    patient_id: str,
    document_id: str,
    current_staff: StaffProfile = Depends(verify_supabase_token),
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security)
):
    token = credentials.credentials.strip() if credentials else ""
    return await DocumentIntakeService.get_document_versions(patient_id, document_id, current_staff, token)


@router.get(
    "/api/v1/patients/{patient_id}/activity-history",
    summary="Get patient audit and activity history",
    tags=["Audit"]
)
async def get_patient_activity_history(
    patient_id: str,
    current_staff: StaffProfile = Depends(verify_supabase_token),
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security)
):
    token = credentials.credentials.strip() if credentials else ""
    return await AuditService.get_patient_audit_events(patient_id, token)


@router.get(
    "/api/v1/patients/{patient_id}/conflict-reviews",
    summary="Get clinical conflict reviews for patient documents",
    tags=["Conflict Reviews"]
)
async def get_patient_conflict_reviews(
    patient_id: str,
    current_staff: StaffProfile = Depends(verify_supabase_token),
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security)
):
    token = credentials.credentials.strip() if credentials else ""
    auth_header = token if (isinstance(token, str) and token.count('.') == 2) else settings.SUPABASE_ANON_KEY
    headers = {
        "Authorization": f"Bearer {auth_header}",
        "apikey": settings.SUPABASE_ANON_KEY
    }
    url = f"{settings.SUPABASE_URL.rstrip('/')}/rest/v1/clinical_conflict_reviews?patient_id=eq.{patient_id}&order=created_at.desc&select=*"
    client = get_http_client()
    try:
        res = await client.get(url, headers=headers)
        if res.status_code == 200:
            return res.json()
    except Exception as exc:
        logger.error(f"Error fetching conflict reviews: {str(exc)}")
    return []


@router.post(
    "/api/v1/patients/{patient_id}/conflict-reviews",
    summary="Record or resolve a human clinical conflict review",
    tags=["Conflict Reviews"]
)
async def create_patient_conflict_review(
    patient_id: str,
    payload: dict,
    current_staff: StaffProfile = Depends(verify_supabase_token),
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security)
):
    token = credentials.credentials.strip() if credentials else ""
    auth_header = token if (isinstance(token, str) and token.count('.') == 2) else settings.SUPABASE_ANON_KEY
    headers = {
        "Authorization": f"Bearer {auth_header}",
        "apikey": settings.SUPABASE_ANON_KEY,
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }
    
    body = {
        "patient_id": patient_id,
        "document_id": payload.get("document_id"),
        "field_name": payload.get("field_name", "clinical_value"),
        "source_doc_a": payload.get("source_doc_a"),
        "source_doc_b": payload.get("source_doc_b"),
        "value_a": str(payload.get("value_a", "")),
        "value_b": str(payload.get("value_b", "")),
        "date_a": payload.get("date_a"),
        "date_b": payload.get("date_b"),
        "review_status": payload.get("review_status", "pending_human_review"),
        "resolution_notes": payload.get("resolution_notes", ""),
        "reviewer_staff_id": current_staff.id
    }
    
    url = f"{settings.SUPABASE_URL.rstrip('/')}/rest/v1/clinical_conflict_reviews"
    client = get_http_client()
    try:
        res = await client.post(url, json=body, headers=headers)
        if res.status_code in (200, 201):
            AuditService.log_event_background(
                staff_id=current_staff.id,
                patient_id=patient_id,
                action="conflict_review_recorded",
                resource=f"clinical_conflict_reviews/{payload.get('document_id', '')}",
                details={"field_name": body["field_name"], "status": body["review_status"]},
                token=token
            )
            return res.json()
    except Exception as exc:
        logger.error(f"Error creating conflict review: {str(exc)}")
    return {"status": "recorded", "patient_id": patient_id}





