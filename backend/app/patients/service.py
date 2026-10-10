from typing import List, Optional, Dict, Any
from datetime import date
import os
import httpx
from fastapi import HTTPException, status
from app.core.config import settings
from app.core.http_client import get_http_client
from app.schemas.models import (
    Patient, StaffProfile, DocumentItem, DocumentVersionItem,
    TimelineEventItem, FertilityCycleItem, DocumentSourceResponse
)
from app.audit.service import AuditService

def _get_auth_header(token: str) -> str:
    if isinstance(token, str) and token.count('.') == 2:
        return token
    return settings.SUPABASE_ANON_KEY

class PatientService:
    @staticmethod
    async def verify_staff_patient_access(patient_id: str, staff: StaffProfile, token: str) -> None:
        """
        Verifies explicit access grant in public.patient_access_grants for staff and patient.
        Logs DENIED_ACCESS_ATTEMPT audit event and raises 403 Forbidden if grant is missing.
        """
        supabase_url = settings.SUPABASE_URL.rstrip('/')
        auth_header = _get_auth_header(token)
        headers = {
            "Authorization": f"Bearer {auth_header}",
            "apikey": settings.SUPABASE_ANON_KEY
        }
        client = get_http_client()
        grant_url = f"{supabase_url}/rest/v1/patient_access_grants?staff_id=eq.{staff.id}&patient_id=eq.{patient_id}&select=id,action"
        
        try:
            res_grant = await client.get(grant_url, headers=headers)
        except Exception as exc:
            await AuditService.log_event(staff.id, patient_id, "DENIED_ACCESS_ATTEMPT", f"/api/v1/patients/{patient_id}", {"error": str(exc)}, token)
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Database access failure: Unable to verify access grant ({str(exc)})"
            )

        if res_grant.status_code in (401, 403):
            await AuditService.log_event(staff.id, patient_id, "DENIED_ACCESS_ATTEMPT", f"/api/v1/patients/{patient_id}", {"status": res_grant.status_code}, token)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: You do not hold an explicit access grant for this patient record"
            )
        elif res_grant.status_code != 200:
            await AuditService.log_event(staff.id, patient_id, "DENIED_ACCESS_ATTEMPT", f"/api/v1/patients/{patient_id}", {"status": res_grant.status_code}, token)
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Database query failure (status {res_grant.status_code}): Unable to verify access grant"
            )

        grant_rows = res_grant.json()
        actions = [r.get("action") for r in grant_rows if r.get("action") in ("read", "write", "admin")]

        if not actions:
            await AuditService.log_event(staff.id, patient_id, "DENIED_ACCESS_ATTEMPT", f"/api/v1/patients/{patient_id}", {"reason": "Missing access grant"}, token)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: You do not hold an explicit access grant for this patient record"
            )

        if "admin" in actions:
            return "admin"
        elif "write" in actions:
            return "write"
        else:
            return "read"

    @staticmethod
    async def verify_staff_patient_write_access(patient_id: str, staff: StaffProfile, token: str) -> None:
        """
        Verifies explicit write or admin access grant in public.patient_access_grants for staff and patient.
        Logs DENIED_ACCESS_ATTEMPT audit event and raises 403 Forbidden if grant is missing or read-only.
        """
        supabase_url = settings.SUPABASE_URL.rstrip('/')
        auth_header = _get_auth_header(token)
        headers = {
            "Authorization": f"Bearer {auth_header}",
            "apikey": settings.SUPABASE_ANON_KEY
        }
        client = get_http_client()
        grant_url = f"{supabase_url}/rest/v1/patient_access_grants?staff_id=eq.{staff.id}&patient_id=eq.{patient_id}&select=id,action"
        
        try:
            res_grant = await client.get(grant_url, headers=headers)
        except Exception as exc:
            await AuditService.log_event(staff.id, patient_id, "DENIED_ACCESS_ATTEMPT", f"/api/v1/patients/{patient_id}", {"error": str(exc)}, token)
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Database access failure: Unable to verify access grant ({str(exc)})"
            )

        if res_grant.status_code in (401, 403):
            await AuditService.log_event(staff.id, patient_id, "DENIED_ACCESS_ATTEMPT", f"/api/v1/patients/{patient_id}", {"status": res_grant.status_code}, token)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: You do not hold an explicit access grant for this patient record"
            )
        elif res_grant.status_code != 200:
            await AuditService.log_event(staff.id, patient_id, "DENIED_ACCESS_ATTEMPT", f"/api/v1/patients/{patient_id}", {"status": res_grant.status_code}, token)
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Database query failure (status {res_grant.status_code}): Unable to verify access grant"
            )

        grant_rows = res_grant.json()
        has_write_grant = any(r.get("action") in ("write", "admin") for r in grant_rows)

        if not has_write_grant:
            await AuditService.log_event(staff.id, patient_id, "DENIED_ACCESS_ATTEMPT", f"/api/v1/patients/{patient_id}", {"reason": "Missing write/admin access grant"}, token)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: You require explicit write or admin access for this patient record"
            )


    @staticmethod
    async def get_permitted_patients_for_staff(staff: StaffProfile, token: str = "") -> List[Patient]:
        supabase_url = settings.SUPABASE_URL.rstrip('/')
        auth_header = _get_auth_header(token)
        headers = {
            "Authorization": f"Bearer {auth_header}",
            "apikey": settings.SUPABASE_ANON_KEY
        }
        client = get_http_client()

        grants_url = f"{supabase_url}/rest/v1/patient_access_grants?staff_id=eq.{staff.id}&select=patient_id,action"
        try:
            res_grants = await client.get(grants_url, headers=headers)
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Database access failure: Unable to load patient access grants ({str(exc)})"
            )

        if res_grants.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Database query failure (status {res_grants.status_code}): Unable to fetch access grants"
            )

        grants_rows = res_grants.json()
        grant_map = {}
        for row in grants_rows:
            pid = row.get("patient_id")
            act = row.get("action")
            if pid and act in ("read", "write", "admin"):
                if pid not in grant_map or act in ("admin", "write"):
                    grant_map[pid] = act

        permitted_patient_ids = list(grant_map.keys())

        if not permitted_patient_ids:
            return []

        ids_param = ",".join(permitted_patient_ids)
        patients_url = f"{supabase_url}/rest/v1/patients?id=in.({ids_param})&select=id,mrn,first_name,last_name,dob,gender,status,record_version"
        try:
            res_patients = await client.get(patients_url, headers=headers)
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Database access failure: Unable to load patient records ({str(exc)})"
            )

        if res_patients.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Database query failure (status {res_patients.status_code}): Unable to fetch patient records"
            )

        patient_rows = res_patients.json()
        return [
            Patient(
                id=p["id"],
                mrn=p["mrn"],
                first_name=p["first_name"],
                last_name=p["last_name"],
                dob=date.fromisoformat(p["dob"]) if isinstance(p["dob"], str) else p["dob"],
                gender=p["gender"],
                status=p["status"],
                record_version=p["record_version"],
                user_grant=grant_map.get(p["id"], "read"),
                can_write=grant_map.get(p["id"], "read") in ("write", "admin")
            )
            for p in patient_rows
        ]

    @staticmethod
    async def get_patient_detail_for_staff(patient_id: str, staff: StaffProfile, token: str = "") -> Patient:
        user_grant = await PatientService.verify_staff_patient_access(patient_id, staff, token)

        supabase_url = settings.SUPABASE_URL.rstrip('/')
        auth_header = _get_auth_header(token)
        headers = {
            "Authorization": f"Bearer {auth_header}",
            "apikey": settings.SUPABASE_ANON_KEY
        }
        client = get_http_client()

        patient_url = f"{supabase_url}/rest/v1/patients?id=eq.{patient_id}&select=id,mrn,first_name,last_name,dob,gender,status,record_version"
        try:
            res_patient = await client.get(patient_url, headers=headers)
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Database access failure: Unable to load patient record ({str(exc)})"
            )

        if res_patient.status_code != 200 or not res_patient.json():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient record not found")

        p = res_patient.json()[0]
        AuditService.log_event_background(staff.id, patient_id, "VIEW_PATIENT_OVERVIEW", f"/api/v1/patients/{patient_id}", {}, token)
        return Patient(
            id=p["id"],
            mrn=p["mrn"],
            first_name=p["first_name"],
            last_name=p["last_name"],
            dob=date.fromisoformat(p["dob"]) if isinstance(p["dob"], str) else p["dob"],
            gender=p["gender"],
            status=p["status"],
            record_version=p["record_version"],
            user_grant=user_grant,
            can_write=user_grant in ("write", "admin")
        )

    @staticmethod
    async def get_patient_timeline(patient_id: str, staff: StaffProfile, token: str = "", event_type: Optional[str] = None) -> List[TimelineEventItem]:
        await PatientService.verify_staff_patient_access(patient_id, staff, token)

        supabase_url = settings.SUPABASE_URL.rstrip('/')
        auth_header = _get_auth_header(token)
        headers = {
            "Authorization": f"Bearer {auth_header}",
            "apikey": settings.SUPABASE_ANON_KEY
        }
        client = get_http_client()

        url = f"{supabase_url}/rest/v1/patient_timeline_events?patient_id=eq.{patient_id}&order=event_date.desc"
        if event_type:
            url += f"&event_type=eq.{event_type}"

        try:
            res = await client.get(url, headers=headers)
        except Exception as exc:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"Database access failure loading timeline ({str(exc)})")

        if res.status_code != 200:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"Database query error status {res.status_code}")

        events = [
            TimelineEventItem(
                id=r["id"],
                patient_id=r["patient_id"],
                event_date=date.fromisoformat(r["event_date"]) if isinstance(r["event_date"], str) else r["event_date"],
                event_type=r["event_type"],
                title=r["title"],
                summary=r["summary"],
                document_id=r.get("document_id"),
                metadata_json=r.get("metadata_json") or {}
            )
            for r in res.json()
        ]
        AuditService.log_event_background(staff.id, patient_id, "VIEW_PATIENT_TIMELINE", f"/api/v1/patients/{patient_id}/timeline", {"count": len(events), "filter": event_type}, token)
        return events

    @staticmethod
    async def get_patient_documents(patient_id: str, staff: StaffProfile, token: str = "", doc_type: Optional[str] = None) -> List[DocumentItem]:
        await PatientService.verify_staff_patient_access(patient_id, staff, token)

        supabase_url = settings.SUPABASE_URL.rstrip('/')
        auth_header = _get_auth_header(token)
        headers = {
            "Authorization": f"Bearer {auth_header}",
            "apikey": settings.SUPABASE_ANON_KEY
        }
        client = get_http_client()

        url = f"{supabase_url}/rest/v1/patient_documents?patient_id=eq.{patient_id}&order=clinical_date.desc"
        if doc_type:
            url += f"&doc_type=eq.{doc_type}"

        try:
            res = await client.get(url, headers=headers)
        except Exception as exc:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"Database access failure loading documents ({str(exc)})")

        if res.status_code != 200:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"Database query error status {res.status_code}")

        docs = [
            DocumentItem(
                id=r["id"],
                patient_id=r["patient_id"],
                title=r["title"],
                doc_type=r["doc_type"],
                clinical_date=date.fromisoformat(r["clinical_date"]) if isinstance(r["clinical_date"], str) else r["clinical_date"],
                status=r["status"],
                storage_path=r.get("storage_path"),
                mime_type=r.get("mime_type") or "application/pdf",
                file_size=r.get("file_size") or 0,
                current_version=r.get("current_version") or 1
            )
            for r in res.json()
        ]
        AuditService.log_event_background(staff.id, patient_id, "VIEW_PATIENT_DOCUMENTS", f"/api/v1/patients/{patient_id}/documents", {"count": len(docs), "filter": doc_type}, token)
        return docs

    @staticmethod
    async def get_patient_document_detail(patient_id: str, document_id: str, staff: StaffProfile, token: str = "") -> DocumentItem:
        await PatientService.verify_staff_patient_access(patient_id, staff, token)

        supabase_url = settings.SUPABASE_URL.rstrip('/')
        auth_header = _get_auth_header(token)
        headers = {
            "Authorization": f"Bearer {auth_header}",
            "apikey": settings.SUPABASE_ANON_KEY
        }
        client = get_http_client()

        url = f"{supabase_url}/rest/v1/patient_documents?id=eq.{document_id}&patient_id=eq.{patient_id}"
        try:
            res = await client.get(url, headers=headers)
        except Exception as exc:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"Database failure: {str(exc)}")

        if res.status_code != 200 or not res.json():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document record not found")

        r = res.json()[0]
        return DocumentItem(
            id=r["id"],
            patient_id=r["patient_id"],
            title=r["title"],
            doc_type=r["doc_type"],
            clinical_date=date.fromisoformat(r["clinical_date"]) if isinstance(r["clinical_date"], str) else r["clinical_date"],
            status=r["status"],
            storage_path=r.get("storage_path"),
            mime_type=r.get("mime_type") or "application/pdf",
            file_size=r.get("file_size") or 0,
            current_version=r.get("current_version") or 1
        )

    @staticmethod
    async def get_document_source_url(patient_id: str, document_id: str, staff: StaffProfile, token: str = "") -> DocumentSourceResponse:
        doc = await PatientService.get_patient_document_detail(patient_id, document_id, staff, token)

        # Generate presigned download URL or proxy endpoint
        download_url = f"/api/v1/patients/{patient_id}/documents/{document_id}/download"
        AuditService.log_event_background(staff.id, patient_id, "OPEN_DOCUMENT_SOURCE", f"/api/v1/patients/{patient_id}/documents/{document_id}/source-url", {"document_title": doc.title}, token)
        
        return DocumentSourceResponse(
            document_id=doc.id,
            title=doc.title,
            download_url=download_url,
            expires_in_seconds=3600,
            mime_type=doc.mime_type
        )

    @staticmethod
    async def get_document_version_by_id(document_id: str, version_id: str, staff: StaffProfile, token: str = "") -> Optional[Dict[str, Any]]:
        supabase_url = settings.SUPABASE_URL.rstrip('/')
        auth_header = _get_auth_header(token)
        headers = {
            "Authorization": f"Bearer {auth_header}",
            "apikey": settings.SUPABASE_ANON_KEY
        }
        client = get_http_client()
        url = f"{supabase_url}/rest/v1/patient_document_versions?id=eq.{version_id}&document_id=eq.{document_id}&select=*"
        try:
            res = await client.get(url, headers=headers)
            if res.status_code == 200 and res.json():
                return res.json()[0]
        except Exception:
            pass
        return None

    @staticmethod
    async def get_fertility_cycles(patient_id: str, staff: StaffProfile, token: str = "") -> List[FertilityCycleItem]:
        await PatientService.verify_staff_patient_access(patient_id, staff, token)

        supabase_url = settings.SUPABASE_URL.rstrip('/')
        auth_header = _get_auth_header(token)
        headers = {
            "Authorization": f"Bearer {auth_header}",
            "apikey": settings.SUPABASE_ANON_KEY
        }
        client = get_http_client()

        url = f"{supabase_url}/rest/v1/fertility_cycles?patient_id=eq.{patient_id}&order=start_date.desc"
        try:
            res = await client.get(url, headers=headers)
        except Exception as exc:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"Database access failure loading cycles ({str(exc)})")

        if res.status_code != 200:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"Database query error status {res.status_code}")

        cycles = [
            FertilityCycleItem(
                id=r["id"],
                patient_id=r["patient_id"],
                cycle_name=r["cycle_name"],
                start_date=date.fromisoformat(r["start_date"]) if isinstance(r["start_date"], str) else r["start_date"],
                end_date=date.fromisoformat(r["end_date"]) if (r.get("end_date") and isinstance(r["end_date"], str)) else r.get("end_date"),
                status=r["status"],
                notes_json=r.get("notes_json") or {}
            )
            for r in res.json()
        ]
        AuditService.log_event_background(staff.id, patient_id, "VIEW_PATIENT_CYCLES", f"/api/v1/patients/{patient_id}/cycles", {"count": len(cycles)}, token)
        return cycles
