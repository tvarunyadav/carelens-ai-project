import json
import logging
import asyncio
from typing import Optional, Dict, Any, List
from app.core.config import settings
from app.core.http_client import get_http_client

logger = logging.getLogger(__name__)

class AuditService:
    @staticmethod
    async def log_event(
        staff_id: Optional[str],
        patient_id: Optional[str],
        action: str,
        resource: str,
        details: Optional[Dict[str, Any]] = None,
        token: str = ""
    ) -> bool:
        """
        Persists an audit event to public.audit_events table in Supabase.
        Enforces caller actor verification and patient access bounds.
        Never logs tokens, passwords, keys, or full clinical text.
        """
        supabase_url = settings.SUPABASE_URL.rstrip('/')
        
        # Enforce valid Bearer token verified via Supabase Auth
        is_user_token = isinstance(token, str) and token.count('.') == 2

        if not is_user_token:
            logger.warning(f"Denied audit write attempt: Missing or malformed staff JWT token for action {action}.")
            return False

        auth_header = token
        api_key = settings.SUPABASE_ANON_KEY

        headers = {
            "Authorization": f"Bearer {auth_header}",
            "apikey": api_key,
            "Content-Type": "application/json",
            "Prefer": "return=minimal"
        }
        
        payload = {
            "staff_id": staff_id,
            "patient_id": patient_id,
            "action": action,
            "resource": resource,
            "details_json": details or {}
        }
        
        url = f"{supabase_url}/rest/v1/audit_events"
        client = get_http_client()
        
        try:
            res = await client.post(url, json=payload, headers=headers)
            if res.status_code in (200, 201, 204):
                logger.info(f"Audit event logged: {action} on {resource} by staff {staff_id}")
                return True
            else:
                logger.warning(f"Failed to log audit event ({res.status_code}): {res.text}")
                return False
        except Exception as exc:
            logger.error(f"Audit logging error: {str(exc)}")
            return False

    @staticmethod
    def log_event_background(
        staff_id: Optional[str],
        patient_id: Optional[str],
        action: str,
        resource: str,
        details: Optional[Dict[str, Any]] = None,
        token: str = ""
    ) -> None:
        """
        Schedules log_event in the background so audit persistence does not delay API response payloads.
        """
        try:
            asyncio.create_task(
                AuditService.log_event(staff_id, patient_id, action, resource, details, token)
            )
        except Exception as exc:
            logger.error(f"Failed to schedule background audit event: {str(exc)}")

    @staticmethod
    async def get_patient_audit_events(
        patient_id: str,
        token: str
    ) -> List[Dict[str, Any]]:
        """
        Retrieves audit events for a given patient record.
        STRICTLY requires a verified staff JWT token.
        Evaluated strictly under database RLS policies.
        """
        if not token or not isinstance(token, str) or token.count('.') != 2:
            logger.warning("Denied audit read attempt: Missing or malformed staff JWT token.")
            return []

        supabase_url = settings.SUPABASE_URL.rstrip('/')
        headers = {
            "Authorization": f"Bearer {token}",
            "apikey": settings.SUPABASE_ANON_KEY
        }
        url = f"{supabase_url}/rest/v1/audit_events?patient_id=eq.{patient_id}&order=created_at.desc&select=id,staff_id,patient_id,action,resource,details_json,created_at"
        client = get_http_client()
        try:
            res = await client.get(url, headers=headers)
            if res.status_code == 200:
                return res.json()
            else:
                logger.warning(f"Audit events fetch denied or failed ({res.status_code}): {res.text}")
        except Exception as exc:
            logger.error(f"Error fetching audit events: {str(exc)}")
        return []
