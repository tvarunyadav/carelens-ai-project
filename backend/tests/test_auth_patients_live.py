import pytest
import os
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.core.config import settings

@pytest.mark.asyncio
async def test_live_supabase_auth_integration():
    """
    Live integration test for Supabase Auth API verification.
    Executes only if real live Supabase credentials are path-configured in environment.
    """
    supabase_url = settings.SUPABASE_URL
    if not supabase_url or "your-supabase" in supabase_url or "placeholder" in supabase_url:
        pytest.skip("Live Supabase credentials not set in environment settings. Skipping live integration test.")

    test_token = os.getenv("TEST_SUPABASE_ACCESS_TOKEN")
    if not test_token:
        pytest.skip("TEST_SUPABASE_ACCESS_TOKEN not provided in environment. Skipping live integration test.")

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        headers = {"Authorization": f"Bearer {test_token}"}
        response = await client.get("/api/v1/me", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "email" in data
