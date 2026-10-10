import os
import pytest
from datetime import date
from unittest.mock import patch, AsyncMock
from httpx import AsyncClient, ASGITransport, Response
from fastapi import HTTPException
from app.main import app
from app.auth.verifier import verify_supabase_token
from app.patients.service import PatientService
from app.schemas.models import (
    StaffProfile, Patient, TimelineEventItem, DocumentItem, FertilityCycleItem, DocumentSourceResponse
)
from app.documents.extractor import PDFExtractor
from app.audit.service import AuditService

STAFF_ALICE = StaffProfile(
    id="e562028e-e5d5-48be-81f1-14446243a01c",
    email="dr.alice@clinic.org",
    full_name="Dr. Alice Morgan",
    role="doctor"
)

STAFF_BOB = StaffProfile(
    id="7b7c7b68-8c02-4081-a5a3-18b6cdcb26f7",
    email="coord.bob@clinic.org",
    full_name="Bob Vance",
    role="coordinator"
)

SOPHIA_ID = "33333333-3333-3333-3333-333333333333"
ELEANOR_ID = "11111111-1111-1111-1111-111111111111"

@pytest.mark.asyncio
async def test_get_patient_timeline_authorized():
    app.dependency_overrides[verify_supabase_token] = lambda: STAFF_BOB
    mock_events = [
        TimelineEventItem(
            id="t1",
            patient_id=SOPHIA_ID,
            event_date=date(2026, 4, 15),
            event_type="visit",
            title="Initial Consultation",
            summary="Evaluation completed"
        )
    ]
    try:
        with patch("app.patients.service.PatientService.get_patient_timeline", return_value=mock_events):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://testserver") as client:
                res = await client.get(f"/api/v1/patients/{SOPHIA_ID}/timeline", headers={"Authorization": "Bearer mock-token"})
                assert res.status_code == 200
                data = res.json()
                assert data["total"] == 1
                assert data["events"][0]["title"] == "Initial Consultation"
    finally:
        app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_get_patient_timeline_unauthorized_bob_eleanor():
    # Bob has NO grant for Eleanor
    grants_resp = Response(200, json=[])
    with patch("app.patients.service.get_http_client") as mock_http:
        mock_client = AsyncMock()
        mock_client.get.return_value = grants_resp
        mock_http.return_value = mock_client
        
        with pytest.raises(Exception) as exc_info:
            await PatientService.get_patient_timeline(ELEANOR_ID, STAFF_BOB, "mock-token")
        assert "Access denied" in str(exc_info.value) or "403" in str(exc_info.value)

@pytest.mark.asyncio
async def test_get_patient_documents_authorized():
    app.dependency_overrides[verify_supabase_token] = lambda: STAFF_BOB
    mock_docs = [
        DocumentItem(
            id="d1",
            patient_id=SOPHIA_ID,
            title="Baseline Hormone Panel",
            doc_type="lab_report",
            clinical_date=date(2026, 4, 20),
            status="final",
            storage_path="sophia_initial_consultation_2026-04-15.pdf"
        )
    ]
    try:
        with patch("app.patients.service.PatientService.get_patient_documents", return_value=mock_docs):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://testserver") as client:
                res = await client.get(f"/api/v1/patients/{SOPHIA_ID}/documents", headers={"Authorization": "Bearer mock-token"})
                assert res.status_code == 200
                data = res.json()
                assert data["total"] == 1
                assert data["documents"][0]["title"] == "Baseline Hormone Panel"
    finally:
        app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_download_pending_document_returns_400():
    app.dependency_overrides[verify_supabase_token] = lambda: STAFF_BOB
    pending_doc = DocumentItem(
        id="d_pending",
        patient_id=SOPHIA_ID,
        title="Pending Karyotype Order",
        doc_type="pending_lab_order",
        clinical_date=date(2026, 4, 25),
        status="pending",
        storage_path=None
    )
    try:
        with patch("app.patients.service.PatientService.get_patient_document_detail", return_value=pending_doc):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://testserver") as client:
                res = await client.get(
                    f"/api/v1/patients/{SOPHIA_ID}/documents/d_pending/download",
                    headers={"Authorization": "Bearer mock-token"}
                )
                assert res.status_code == 400
                assert "Result not yet recorded" in res.json()["detail"]
    finally:
        app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_download_unauthorized_patient_document_denied():
    app.dependency_overrides[verify_supabase_token] = lambda: STAFF_BOB
    try:
        with patch("app.patients.service.PatientService.get_patient_document_detail", side_effect=HTTPException(403, "Access denied")):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://testserver") as client:
                res = await client.get(
                    f"/api/v1/patients/{ELEANOR_ID}/documents/d_eleanor/download",
                    headers={"Authorization": "Bearer mock-token"}
                )
                assert res.status_code == 403
    finally:
        app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_get_fertility_cycles_authorized():
    app.dependency_overrides[verify_supabase_token] = lambda: STAFF_BOB
    mock_cycles = [
        FertilityCycleItem(
            id="c1",
            patient_id=SOPHIA_ID,
            cycle_name="IVF Cycle 1",
            start_date=date(2026, 5, 1),
            end_date=date(2026, 5, 28),
            status="completed"
        )
    ]
    try:
        with patch("app.patients.service.PatientService.get_fertility_cycles", return_value=mock_cycles):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://testserver") as client:
                res = await client.get(f"/api/v1/patients/{SOPHIA_ID}/cycles", headers={"Authorization": "Bearer mock-token"})
                assert res.status_code == 200
                data = res.json()
                assert data["total"] == 1
                assert data["cycles"][0]["cycle_name"] == "IVF Cycle 1"
    finally:
        app.dependency_overrides.clear()

def test_pdf_extractor_synthetic_file():
    test_pdf_path = "backend/storage/patient_documents/sophia_initial_consultation_2026-04-15.pdf"
    if os.path.exists(test_pdf_path):
        result = PDFExtractor.extract_text_and_provenance(test_pdf_path)
        assert result["status"] == "processed"
        assert result["page_count"] >= 1
        assert "Sophia Patel" in result["extracted_text"] or "Infertility" in result["extracted_text"]

@pytest.mark.asyncio
async def test_audit_event_logging():
    with patch("app.audit.service.get_http_client") as mock_http:
        mock_client = AsyncMock()
        mock_client.post.return_value = Response(201)
        mock_http.return_value = mock_client

        success = await AuditService.log_event(
            staff_id=STAFF_BOB.id,
            patient_id=SOPHIA_ID,
            action="VIEW_PATIENT_TIMELINE",
            resource=f"/api/v1/patients/{SOPHIA_ID}/timeline",
            details={"count": 5},
            token="mock.bearer.token"
        )
        assert success is True
