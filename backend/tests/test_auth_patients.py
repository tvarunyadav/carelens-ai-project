import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.asyncio
async def test_health_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"

@pytest.mark.asyncio
async def test_me_endpoint_missing_token():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.get("/api/v1/me")
        assert response.status_code == 401
        assert "Missing Authorization header" in response.json()["detail"]

@pytest.mark.asyncio
async def test_me_endpoint_invalid_token():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        headers = {"Authorization": "Bearer invalid-garbage-token-xyz"}
        response = await client.get("/api/v1/me", headers=headers)
        assert response.status_code == 401

@pytest.mark.asyncio
async def test_me_endpoint_valid_token():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        headers = {"Authorization": "Bearer test-token-dev_user_alice"}
        response = await client.get("/api/v1/me", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "dr.alice@clinic.org"
        assert data["role"] == "doctor"

@pytest.mark.asyncio
async def test_patients_isolation_dr_alice():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        headers = {"Authorization": "Bearer test-token-dev_user_alice"}
        response = await client.get("/api/v1/patients", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        names = [p["first_name"] for p in data["patients"]]
        assert "Eleanor" in names
        assert "Marcus" in names
        assert "Sophia" not in names

@pytest.mark.asyncio
async def test_patients_isolation_bob_coordinator():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        headers = {"Authorization": "Bearer test-token-dev_user_bob"}
        response = await client.get("/api/v1/patients", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["patients"][0]["first_name"] == "Sophia"

@pytest.mark.asyncio
async def test_admin_without_explicit_grant_has_zero_clinical_patients():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        headers = {"Authorization": "Bearer test-token-dev_user_admin"}
        response = await client.get("/api/v1/patients", headers=headers)
        assert response.status_code == 200
        data = response.json()
        # Admin alone does not grant clinical access without explicit grant
        assert data["total"] == 0

@pytest.mark.asyncio
async def test_patient_detail_authorized_vs_unauthorized():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        eleanor_id = "11111111-1111-1111-1111-111111111111"
        
        # Dr. Alice HAS access to Eleanor -> 200 OK
        alice_headers = {"Authorization": "Bearer test-token-dev_user_alice"}
        resp_alice = await client.get(f"/api/v1/patients/{eleanor_id}", headers=alice_headers)
        assert resp_alice.status_code == 200
        assert resp_alice.json()["first_name"] == "Eleanor"

        # Bob Vance DOES NOT have access to Eleanor -> 403 Forbidden
        bob_headers = {"Authorization": "Bearer test-token-dev_user_bob"}
        resp_bob = await client.get(f"/api/v1/patients/{eleanor_id}", headers=bob_headers)
        assert resp_bob.status_code == 403
        assert "Access denied" in resp_bob.json()["detail"]
