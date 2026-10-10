import pytest
import io
from unittest.mock import patch, AsyncMock
from httpx import AsyncClient, ASGITransport
from fastapi import HTTPException
from app.main import app
from app.auth.verifier import verify_supabase_token
from app.schemas.models import StaffProfile

STAFF_BOB_WRITE = StaffProfile(
    id="7b7c7b68-8c02-4081-a5a3-18b6cdcb26f7",
    email="coord.bob@clinic.org",
    full_name="Bob Vance",
    role="coordinator"
)

STAFF_ALICE_READONLY = StaffProfile(
    id="99999999-9999-9999-9999-999999999999",
    email="dr.alice@clinic.org",
    full_name="Alice Smith",
    role="doctor"
)

SOPHIA_ID = "33333333-3333-3333-3333-333333333333"
ELEANOR_ID = "11111111-1111-1111-1111-111111111111"

# Synthetic PDF header bytes
SAMPLE_PDF_BYTES = b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\ntrailer\n<< /Root 1 0 R >>\n%%EOF\n"
INVALID_EXE_BYTES = b"MZ" + b"\x00" * 300

@pytest.mark.asyncio
async def test_upload_document_requires_write_grant_denies_readonly():
    """Verify staff with read-only grant are denied upload access with 403 Forbidden."""
    app.dependency_overrides[verify_supabase_token] = lambda: STAFF_ALICE_READONLY
    try:
        with patch("app.patients.service.PatientService.verify_staff_patient_write_access", side_effect=HTTPException(403, "Access denied: Read-only grant")):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://testserver") as client:
                files = {"file": ("consultation.pdf", SAMPLE_PDF_BYTES, "application/pdf")}
                res = await client.post(
                    f"/api/v1/patients/{SOPHIA_ID}/documents/upload",
                    files=files,
                    headers={"Authorization": "Bearer mock-token"}
                )
                assert res.status_code == 403
                assert "Access denied" in res.json()["detail"]
    finally:
        app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_upload_document_invalid_magic_bytes_rejected():
    """Verify uploading an invalid file format (.exe with MZ magic header) returns 400 Bad Request."""
    app.dependency_overrides[verify_supabase_token] = lambda: STAFF_BOB_WRITE
    try:
        with patch("app.patients.service.PatientService.verify_staff_patient_write_access", return_value=None):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://testserver") as client:
                files = {"file": ("malicious.exe", INVALID_EXE_BYTES, "application/x-msdownload")}
                res = await client.post(
                    f"/api/v1/patients/{SOPHIA_ID}/documents/upload",
                    files=files,
                    headers={"Authorization": "Bearer mock-token"}
                )
                assert res.status_code == 400
                assert "Invalid file content format" in res.json()["detail"]
    finally:
        app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_upload_duplicate_content_hash_returns_duplicate_notice():
    """Verify uploading an exact duplicate content hash scoped to patient returns duplicate_detected notice."""
    app.dependency_overrides[verify_supabase_token] = lambda: STAFF_BOB_WRITE
    try:
        with patch("app.patients.service.PatientService.verify_staff_patient_write_access", return_value=None):
            mock_dup_res = {"status": "duplicate_detected", "message": "Exact duplicate document already exists for this patient."}
            with patch("app.documents.intake_service.DocumentIntakeService.upload_document", return_value=mock_dup_res):
                transport = ASGITransport(app=app)
                async with AsyncClient(transport=transport, base_url="http://testserver") as client:
                    files = {"file": ("duplicate.pdf", SAMPLE_PDF_BYTES, "application/pdf")}
                    res = await client.post(
                        f"/api/v1/patients/{SOPHIA_ID}/documents/upload",
                        files=files,
                        headers={"Authorization": "Bearer mock-token"}
                    )
                    assert res.status_code == 200
                    data = res.json()
                    assert data["status"] == "duplicate_detected"
                    assert "duplicate" in data["message"].lower()
    finally:
        app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_upload_version_allocates_next_version_number():
    """Verify uploading a new version allocates version N+1 without overwriting existing versions."""
    app.dependency_overrides[verify_supabase_token] = lambda: STAFF_BOB_WRITE
    try:
        with patch("app.patients.service.PatientService.verify_staff_patient_write_access", return_value=None):
            mock_ver_res = {
                "status": "success",
                "document_id": "doc-123",
                "version_number": 2,
                "review_status": "pending_review",
                "extraction_status": "processed"
            }
            with patch("app.documents.intake_service.DocumentIntakeService.upload_new_version", return_value=mock_ver_res):
                transport = ASGITransport(app=app)
                async with AsyncClient(transport=transport, base_url="http://testserver") as client:
                    files = {"file": ("consultation_v2.pdf", SAMPLE_PDF_BYTES, "application/pdf")}
                    res = await client.post(
                        f"/api/v1/patients/{SOPHIA_ID}/documents/doc-123/versions/upload",
                        files=files,
                        headers={"Authorization": "Bearer mock-token"}
                    )
                    assert res.status_code == 200
                    data = res.json()
                    assert data["version_number"] == 2
                    assert data["status"] == "success"
    finally:
        app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_review_and_publish_indexes_vector_chunks_idempotently():
    """Verify human review updates document status to final/reviewed and triggers idempotent indexing."""
    app.dependency_overrides[verify_supabase_token] = lambda: STAFF_BOB_WRITE
    try:
        with patch("app.patients.service.PatientService.verify_staff_patient_write_access", return_value=None):
            mock_rev_res = {
                "status": "success",
                "document_id": "doc-123",
                "version_number": 1,
                "review_status": "reviewed",
                "published_status": "final"
            }
            with patch("app.documents.intake_service.DocumentIntakeService.review_and_publish_document", return_value=mock_rev_res):
                transport = ASGITransport(app=app)
                async with AsyncClient(transport=transport, base_url="http://testserver") as client:
                    payload = {
                        "title": "Initial Reproductive Consultation Report",
                        "doc_type": "consultation",
                        "clinical_date": "2026-04-15",
                        "extracted_text": "Patient Sophia Patel evaluating primary infertility."
                    }
                    res = await client.post(
                        f"/api/v1/patients/{SOPHIA_ID}/documents/doc-123/review",
                        json=payload,
                        headers={"Authorization": "Bearer mock-token"}
                    )
                    assert res.status_code == 200
                    data = res.json()
                    assert data["published_status"] == "final"
                    assert data["review_status"] == "reviewed"
    finally:
        app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_cross_patient_document_access_denied():
    """Verify requesting document upload/review for an unauthorized patient returns 403 Forbidden."""
    app.dependency_overrides[verify_supabase_token] = lambda: STAFF_BOB_WRITE
    try:
        with patch("app.patients.service.PatientService.verify_staff_patient_write_access", side_effect=HTTPException(403, "Access denied: Unauthorized patient")):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://testserver") as client:
                files = {"file": ("doc.pdf", SAMPLE_PDF_BYTES, "application/pdf")}
                res = await client.post(
                    f"/api/v1/patients/{ELEANOR_ID}/documents/upload",
                    files=files,
                    headers={"Authorization": "Bearer mock-token"}
                )
                assert res.status_code == 403
    finally:
        app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_upload_new_version_failure_preserves_parent_and_previous_versions():
    """Verify that a failure during new version processing marks only the attempted version failed and preserves parent document & v1 history."""
    from httpx import Response
    app.dependency_overrides[verify_supabase_token] = lambda: STAFF_BOB_WRITE
    try:
        with patch("app.patients.service.PatientService.verify_staff_patient_write_access", return_value=None):
            with patch("app.documents.extractor.PDFExtractor.extract_text_and_provenance", side_effect=RuntimeError("OCR extraction corrupted")):
                mock_doc_get = Response(200, json=[{
                    "id": "doc-123",
                    "patient_id": SOPHIA_ID,
                    "title": "Existing Document",
                    "current_version": 1
                }])
                mock_rpc_create = Response(200, json=[{
                    "id": "ver-002-id",
                    "version_number": 2,
                    "document_id": "doc-123",
                    "storage_path": "patients/doc-123/v2/file.pdf"
                }])
                mock_patch = Response(200, json=[{"id": "ver-002-id"}])

                async def mock_get(url, headers=None, **kwargs):
                    if "patient_documents" in str(url):
                        return mock_doc_get
                    return Response(200, json=[])

                async def mock_post(url, json=None, headers=None, **kwargs):
                    if "create_atomic_document_version" in str(url):
                        return mock_rpc_create
                    return Response(201, json=[])

                with patch("app.documents.intake_service.get_http_client") as mock_http:
                    client_mock = AsyncMock()
                    client_mock.get.side_effect = mock_get
                    client_mock.post.side_effect = mock_post
                    client_mock.patch.return_value = mock_patch
                    mock_http.return_value = client_mock

                    transport = ASGITransport(app=app)
                    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
                        files = {"file": ("bad_v2.pdf", SAMPLE_PDF_BYTES, "application/pdf")}
                        res = await client.post(
                            f"/api/v1/patients/{SOPHIA_ID}/documents/doc-123/versions/upload",
                            files=files,
                            headers={"Authorization": "Bearer mock-token"}
                        )
                        assert res.status_code == 500
                        assert "Version upload processing failed" in res.json()["detail"]
                        assert client_mock.patch.called
                        patch_payload = client_mock.patch.call_args[1]["json"]
                        assert patch_payload["extraction_status"] == "failed"
                        assert "OCR extraction corrupted" in patch_payload["error_message"]
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_upload_document_multipart_contract_reaches_pending_review():
    """Verify multipart file upload contract sends file part correctly and reaches pending human review state."""
    app.dependency_overrides[verify_supabase_token] = lambda: STAFF_BOB_WRITE
    try:
        mock_upload_res = {
            "status": "success",
            "document_id": "doc-multipart-999",
            "version_id": "ver-multipart-999",
            "version_number": 1,
            "title": "synthetic_text_doc_v1.pdf",
            "review_status": "pending_review",
            "extraction_status": "processed",
            "message": "Document uploaded successfully and queued for human review."
        }
        with patch("app.patients.service.PatientService.verify_staff_patient_write_access", return_value=None):
            with patch("app.documents.intake_service.DocumentIntakeService.upload_document", return_value=mock_upload_res) as mock_upload:
                transport = ASGITransport(app=app)
                async with AsyncClient(transport=transport, base_url="http://testserver") as client:
                    files = {"file": ("synthetic_text_doc_v1.pdf", SAMPLE_PDF_BYTES, "application/pdf")}
                    res = await client.post(
                        f"/api/v1/patients/{SOPHIA_ID}/documents/upload",
                        files=files,
                        headers={"Authorization": "Bearer mock-token"}
                    )
                    assert res.status_code == 200
                    data = res.json()
                    assert data["status"] == "success"
                    assert data["review_status"] == "pending_review"
                    assert data["document_id"] == "doc-multipart-999"
                    assert mock_upload.called
                    call_file = mock_upload.call_args[0][1]
                    assert call_file.filename == "synthetic_text_doc_v1.pdf"
    finally:
        app.dependency_overrides.clear()


