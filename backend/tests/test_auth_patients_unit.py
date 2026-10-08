import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.auth.verifier import verify_supabase_token
from app.schemas.models import StaffProfile

# Test Staff Fixtures
STAFF_ALICE = StaffProfile(
    id="11111111-aaaa-1111-aaaa-111111111111",
    email="dr.alice@clinic.org",
    full_name="Dr. Alice Morgan",
    role="doctor"
)

STAFF_BOB = StaffProfile(
    id="22222222-bbbb-2222-bbbb-222222222222",
    email="coord.bob@clinic.org",
    full_name="Bob Vance",
    role="coordinator"
)

STAFF_ADMIN = StaffProfile(
    id="33333333-cccc-3333-cccc-333333333333",
    email="admin.sam@clinic.org",
    full_name="Sam Admin",
    role="admin"
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
    # Clear overrides to test actual 401 error
    app.dependency_overrides.clear()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.get("/api/v1/me")
        assert response.status_code == 401
        assert "Missing Authorization header" in response.json()["detail"]

@pytest.mark.asyncio
async def test_me_endpoint_invalid_token():
    app.dependency_overrides.clear()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        headers = {"Authorization": "Bearer invalid-token-xyz"}
        response = await client.get("/api/v1/me", headers=headers)
        assert response.status_code == 401

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
async def test_patients_isolation_dr_alice():
    app.dependency_overrides[verify_supabase_token] = lambda: STAFF_ALICE
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            headers = {"Authorization": "Bearer mock-test-header"}
            response = await client.get("/api/v1/patients", headers=headers)
            assert response.status_code == 200
            data = response.json()
            assert data["total"] == 2
            names = [p["first_name"] for p in data["patients"]]
            assert "Eleanor" in names
            assert "Marcus" in names
            assert "Sophia" not in names
    finally:
        app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_patients_isolation_bob_coordinator():
    app.dependency_overrides[verify_supabase_token] = lambda: STAFF_BOB
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            headers = {"Authorization": "Bearer mock-test-header"}
            response = await client.get("/api/v1/patients", headers=headers)
            assert response.status_code == 200
            data = response.json()
            assert data["total"] == 1
            assert data["patients"][0]["first_name"] == "Sophia"
    finally:
        app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_admin_without_explicit_grant_has_zero_clinical_patients():
    app.dependency_overrides[verify_supabase_token] = lambda: STAFF_ADMIN
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            headers = {"Authorization": "Bearer mock-test-header"}
            response = await client.get("/api/v1/patients", headers=headers)
            assert response.status_code == 200
            data = response.json()
            assert data["total"] == 0
    finally:
        app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_patient_detail_authorized_vs_unauthorized():
    eleanor_id = "11111111-1111-1111-1111-111111111111"

    # 1. Dr. Alice HAS grant -> 200 OK
    app.dependency_overrides[verify_supabase_token] = lambda: STAFF_ALICE
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            resp_alice = await client.get(f"/api/v1/patients/{eleanor_id}", headers={"Authorization": "Bearer token"})
            assert resp_alice.status_code == 200
            assert resp_alice.json()["first_name"] == "Eleanor"
    finally:
        app.dependency_overrides.clear()

    # 2. Bob Vance DOES NOT have grant -> 403 Forbidden
    app.dependency_overrides[verify_supabase_token] = lambda: STAFF_BOB
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            resp_bob = await client.get(f"/api/v1/patients/{eleanor_id}", headers={"Authorization": "Bearer token"})
            assert resp_bob.status_code == 403
            assert "Access denied" in resp_bob.json()["detail"]
    finally:
        app.dependency_overrides.clear()
