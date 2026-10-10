import pytest
from unittest.mock import patch
from httpx import AsyncClient, ASGITransport, Response
from app.main import app
from app.auth.verifier import verify_supabase_token, fetch_staff_profile_from_db
from app.patients.service import PatientService
from app.schemas.models import StaffProfile

# Fixtures
STAFF_ALICE = StaffProfile(
    id="7b7c7b68-8c02-4081-a5a3-18b6cdcb26f7",
    email="dr.alice@clinic.org",
    full_name="Dr. Alice Morgan",
    role="doctor"
)

STAFF_BOB = StaffProfile(
    id="e562028e-e5d5-48be-81f1-14446243a01c",
    email="coord.bob@clinic.org",
    full_name="Bob Vance",
    role="coordinator"
)

@pytest.mark.asyncio
async def test_health_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"

@pytest.mark.asyncio
async def test_me_endpoint_unauthenticated():
    app.dependency_overrides.clear()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.get("/api/v1/me")
        assert response.status_code == 401
        assert "Missing Authorization header" in response.json()["detail"]

@pytest.mark.asyncio
async def test_me_endpoint_authenticated_doctor():
    app.dependency_overrides[verify_supabase_token] = lambda: STAFF_ALICE
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            headers = {"Authorization": "Bearer mock-test-header"}
            response = await client.get("/api/v1/me", headers=headers)
            assert response.status_code == 200
            data = response.json()
            assert data["email"] == "dr.alice@clinic.org"
            assert data["role"] == "doctor"
    finally:
        app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_fetch_staff_profile_from_db_success():
    mock_row = [{
        "id": "e562028e-e5d5-48be-81f1-14446243a01c",
        "email": "coord.bob@clinic.org",
        "full_name": "Bob Vance",
        "role": "coordinator"
    }]
    mock_resp = Response(200, json=mock_row)
    with patch("app.auth.verifier.httpx.AsyncClient.get", return_value=mock_resp):
        profile = await fetch_staff_profile_from_db("e562028e-e5d5-48be-81f1-14446243a01c", "mock_token")
        assert profile.id == "e562028e-e5d5-48be-81f1-14446243a01c"
        assert profile.full_name == "Bob Vance"
        assert profile.role == "coordinator"

@pytest.mark.asyncio
async def test_missing_staff_profile_denies_access():
    mock_resp = Response(200, json=[])
    with patch("app.auth.verifier.httpx.AsyncClient.get", return_value=mock_resp):
        with pytest.raises(Exception) as exc_info:
            await fetch_staff_profile_from_db("unknown_uuid", "mock_token")
        assert "403" in str(exc_info.value) or "Access denied" in str(exc_info.value)

@pytest.mark.asyncio
async def test_database_failure_returns_sanitized_service_error():
    with patch("app.auth.verifier.httpx.AsyncClient.get", side_effect=Exception("Database connection timeout")):
        with pytest.raises(Exception) as exc_info:
            await fetch_staff_profile_from_db("e562028e-e5d5-48be-81f1-14446243a01c", "mock_token")
        assert "Database access failure" in str(exc_info.value)

@pytest.mark.asyncio
async def test_patient_service_get_permitted_patients_bob():
    grants_resp = Response(200, json=[{"patient_id": "33333333-3333-3333-3333-333333333333", "action": "read"}])
    patients_resp = Response(200, json=[{
        "id": "33333333-3333-3333-3333-333333333333",
        "mrn": "MRN-441029",
        "first_name": "Sophia",
        "last_name": "Patel",
        "dob": "1982-11-05",
        "gender": "Female",
        "status": "active",
        "record_version": 1
    }])

    async def mock_get(self, url, **kwargs):
        if "patient_access_grants" in url:
            return grants_resp
        return patients_resp

    with patch("app.patients.service.httpx.AsyncClient.get", side_effect=mock_get, autospec=True):
        patients = await PatientService.get_permitted_patients_for_staff(STAFF_BOB, "mock_token")
        assert len(patients) == 1
        assert patients[0].first_name == "Sophia"
        assert patients[0].last_name == "Patel"

@pytest.mark.asyncio
async def test_patient_service_unauthorized_detail_request_denied():
    grants_resp = Response(200, json=[]) # Empty grant for Bob requesting Eleanor
    with patch("app.patients.service.httpx.AsyncClient.get", return_value=grants_resp):
        with pytest.raises(Exception) as exc_info:
            await PatientService.get_patient_detail_for_staff("11111111-1111-1111-1111-111111111111", STAFF_BOB, "mock_token")
        assert "Access denied" in str(exc_info.value)

@pytest.mark.asyncio
async def test_patient_service_database_failure():
    with patch("app.patients.service.httpx.AsyncClient.get", side_effect=Exception("PostgREST network error")):
        with pytest.raises(Exception) as exc_info:
            await PatientService.get_permitted_patients_for_staff(STAFF_BOB, "mock_token")
        assert "Database access failure" in str(exc_info.value)

from datetime import date
from app.schemas.models import Patient

@pytest.mark.asyncio
async def test_route_patients_bob_isolation():
    app.dependency_overrides[verify_supabase_token] = lambda: STAFF_BOB
    mock_patients = [
        Patient(
            id="33333333-3333-3333-3333-333333333333",
            mrn="MRN-441029",
            first_name="Sophia",
            last_name="Patel",
            dob=date(1982, 11, 5),
            gender="Female",
            status="active",
            record_version=1
        )
    ]
    try:
        with patch("app.patients.service.PatientService.get_permitted_patients_for_staff", return_value=mock_patients):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://testserver") as client:
                headers = {"Authorization": "Bearer mock-test-token"}
                res = await client.get("/api/v1/patients", headers=headers)
                assert res.status_code == 200
                data = res.json()
                assert data["total"] == 1
                assert data["patients"][0]["first_name"] == "Sophia"
    finally:
        app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_tampered_or_invalid_token_rejected():
    app.dependency_overrides.clear()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        headers = {"Authorization": "Bearer invalid.tampered.token"}
        res = await client.get("/api/v1/patients", headers=headers)
        assert res.status_code == 401

@pytest.mark.asyncio
async def test_supabase_auth_rejected_token_denies_access():
    app.dependency_overrides.clear()
    mock_auth_401 = Response(401, json={"error": "invalid_grant"})
    with patch("app.auth.verifier.httpx.AsyncClient.get", return_value=mock_auth_401):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            headers = {"Authorization": "Bearer rejected-by-supabase-auth"}
            res = await client.get("/api/v1/patients", headers=headers)
            assert res.status_code == 401





