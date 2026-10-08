from datetime import datetime, timezone
from fastapi import APIRouter
from app.schemas.models import HealthStatus
from app.core.config import settings

router = APIRouter()

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
