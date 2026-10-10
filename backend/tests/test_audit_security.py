import pytest
from unittest.mock import patch, AsyncMock
from fastapi import HTTPException
from app.audit.service import AuditService
from app.schemas.models import StaffProfile

ELEANOR_ID = "11111111-1111-1111-1111-111111111111"
MARCUS_ID = "22222222-2222-2222-2222-222222222222"
ALICE_ID = "e562028e-e5d5-48be-81f1-14446243a01c"
BOB_ID = "7b7c7b68-8c02-4081-a5a3-18b6cdcb26f7"

@pytest.mark.asyncio
async def test_missing_or_malformed_token_denies_audit_reads():
    """Missing or malformed JWT token must return empty audit list without privileged fallback."""
    events_empty_token = await AuditService.get_patient_audit_events(ELEANOR_ID, token="")
    assert events_empty_token == []

    events_malformed_token = await AuditService.get_patient_audit_events(ELEANOR_ID, token="invalid-token-string")
    assert events_malformed_token == []

@pytest.mark.asyncio
async def test_missing_or_malformed_token_denies_audit_writes():
    """Missing or malformed JWT token must deny audit write without privileged service role fallback."""
    with patch("app.audit.service.get_http_client") as mock_get_client:
        mock_client = AsyncMock()
        mock_get_client.return_value = mock_client

        success_empty = await AuditService.log_event(
            staff_id=ALICE_ID,
            patient_id=ELEANOR_ID,
            action="VIEW_PATIENT_OVERVIEW",
            resource=f"/api/v1/patients/{ELEANOR_ID}",
            token=""
        )
        assert success_empty is False
        mock_client.post.assert_not_called()

        success_malformed = await AuditService.log_event(
            staff_id=ALICE_ID,
            patient_id=ELEANOR_ID,
            action="VIEW_PATIENT_OVERVIEW",
            resource=f"/api/v1/patients/{ELEANOR_ID}",
            token="invalid-token"
        )
        assert success_malformed is False
        mock_client.post.assert_not_called()

@pytest.mark.asyncio
async def test_actor_spoofing_rejected_for_user_writes():
    """Audit log_event must bind write payload to caller token and reject mismatched headers."""
    valid_mock_jwt = "header.payload.signature"
    
    with patch("app.audit.service.get_http_client") as mock_get_client:
        mock_client = AsyncMock()
        mock_response = AsyncMock()
        mock_response.status_code = 403
        mock_response.text = '{"detail": "Actor mismatch"}'
        mock_client.post.return_value = mock_response
        mock_get_client.return_value = mock_client

        # Attempt to log with Alice's ID using an unauthorized/rejected payload
        success = await AuditService.log_event(
            staff_id=ALICE_ID,
            patient_id=ELEANOR_ID,
            action="VIEW_PATIENT_OVERVIEW",
            resource=f"/api/v1/patients/{ELEANOR_ID}",
            details={"attempt": "spoof"},
            token=valid_mock_jwt
        )
        assert success is False
        mock_client.post.assert_called_once()
        headers_sent = mock_client.post.call_args.kwargs.get("headers", {})
        assert headers_sent.get("Authorization") == f"Bearer {valid_mock_jwt}"

@pytest.mark.asyncio
async def test_unauthorized_cross_patient_audit_read_denied():
    """Unauthorized staff attempt to read audit history for forbidden patient must be denied by RLS."""
    bob_jwt = "bob.valid.token"
    
    with patch("app.audit.service.get_http_client") as mock_get_client:
        mock_client = AsyncMock()
        mock_response = AsyncMock()
        mock_response.status_code = 403
        mock_response.text = '{"detail": "Access denied by RLS policy"}'
        mock_client.get.return_value = mock_response
        mock_get_client.return_value = mock_client

        # Bob attempts to read Eleanor's audit events (no grant)
        events = await AuditService.get_patient_audit_events(ELEANOR_ID, token=bob_jwt)
        assert events == []
        mock_client.get.assert_called_once()
        headers_sent = mock_client.get.call_args.kwargs.get("headers", {})
        assert headers_sent.get("Authorization") == f"Bearer {bob_jwt}"

@pytest.mark.asyncio
async def test_legitimate_authenticated_action_creates_persisted_audit_event():
    """A legitimate authenticated staff action creates a persisted audit event."""
    alice_jwt = "alice.valid.token"
    
    with patch("app.audit.service.get_http_client") as mock_get_client:
        mock_client = AsyncMock()
        mock_response = AsyncMock()
        mock_response.status_code = 201
        mock_response.json.return_value = [{"id": "audit-123", "action": "AI_QUERY_ASKED"}]
        mock_client.post.return_value = mock_response
        mock_get_client.return_value = mock_client

        success = await AuditService.log_event(
            staff_id=ALICE_ID,
            patient_id=ELEANOR_ID,
            action="AI_QUERY_ASKED",
            resource=f"/api/v1/patients/{ELEANOR_ID}/ai/query",
            details={"query": "What were her last two cycles?"},
            token=alice_jwt
        )
        assert success is True
        mock_client.post.assert_called_once()

@pytest.mark.asyncio
async def test_forged_three_part_jwt_token_rejected():
    """A forged 3-part token passes format checking but must be rejected by cryptographic Supabase Auth verification."""
    forged_jwt = "forged.header.signature"
    
    with patch("app.audit.service.get_http_client") as mock_get_client:
        mock_client = AsyncMock()
        mock_response = AsyncMock()
        mock_response.status_code = 401
        mock_response.text = '{"message": "Invalid JWT signature"}'
        mock_client.get.return_value = mock_response
        mock_client.post.return_value = mock_response
        mock_get_client.return_value = mock_client

        # Audit read with forged token must fail (empty list)
        read_events = await AuditService.get_patient_audit_events(ELEANOR_ID, token=forged_jwt)
        assert read_events == []

        # Audit write with forged token must fail (False)
        write_success = await AuditService.log_event(
            staff_id=ALICE_ID,
            patient_id=ELEANOR_ID,
            action="VIEW_PATIENT_OVERVIEW",
            resource=f"/api/v1/patients/{ELEANOR_ID}",
            token=forged_jwt
        )
        assert write_success is False
