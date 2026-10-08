from datetime import datetime, timezone
from typing import List
from fastapi import APIRouter, Depends
from app.schemas.models import HealthStatus, StaffProfile, Patient, PatientListResponse
from app.core.config import settings
from app.auth.verifier import verify_supabase_token
from app.patients.service import PatientService

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
async def list_permitted_patients(current_staff: StaffProfile = Depends(verify_supabase_token)):
    """
    Returns only the patient records for which the verified staff member holds an explicit grant.
    Enforces patient access isolation across all roles.
    """
    permitted_patients = PatientService.get_permitted_patients_for_staff(current_staff)
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
    current_staff: StaffProfile = Depends(verify_supabase_token)
):
    """
    Authorizes detail access BEFORE returning patient information.
    Raises 403 Forbidden if the staff member does not hold an explicit access grant.
    """
    return PatientService.get_patient_detail_for_staff(patient_id, current_staff)
