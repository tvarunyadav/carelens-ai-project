import os
import io
import uuid
import hashlib
import logging
import difflib
from typing import List, Dict, Any, Optional
from datetime import datetime, date

from fastapi import HTTPException, status, UploadFile
import httpx

from app.core.config import settings
from app.core.http_client import get_http_client
from app.schemas.models import StaffProfile, DocumentItem, DocumentVersionItem
from app.patients.service import PatientService
from app.audit.service import AuditService
from app.documents.extractor import PDFExtractor
from app.documents.chunker import TextChunker
from app.retrieval.embedding import encode_text_sync

logger = logging.getLogger(__name__)


ALLOWED_MIME_TYPES = {
    "application/pdf": ".pdf",
    "image/png": ".png",
    "image/jpeg": ".jpg",
    "image/jpg": ".jpg"
}

MAX_FILE_BYTES = 15 * 1024 * 1024  # 15 MB
MAX_PAGE_COUNT = 20

def _get_auth_header(token: str) -> str:
    if isinstance(token, str) and token.count('.') == 2:
        return token
    return settings.SUPABASE_ANON_KEY

class DocumentIntakeService:
    @staticmethod
    def _validate_magic_bytes(file_bytes: bytes, filename: str) -> str:
        """Validates file signature magic bytes and returns normalized extension."""
        if not file_bytes or len(file_bytes) < 4:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Uploaded file is empty or corrupted.")

        if file_bytes.startswith(b"%PDF-"):
            return ".pdf"
        elif file_bytes.startswith(b"\x89PNG\r\n\x1a\n"):
            return ".png"
        elif file_bytes.startswith(b"\xff\xd8\xff"):
            return ".jpg"
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid file content format. Only genuine PDF, PNG, and JPEG files are supported."
            )

    @staticmethod
    def _calculate_content_hash(file_bytes: bytes) -> str:
        return hashlib.sha256(file_bytes).hexdigest()

    @staticmethod
    def _generate_metadata_suggestions(filename: str, extracted_text: str) -> Dict[str, Any]:
        """Generates AI metadata suggestions labeled clearly as suggestions."""
        suggested_title = os.path.splitext(filename)[0].replace("_", " ").replace("-", " ").title()
        suggested_type = "consultation"
        txt_lower = extracted_text.lower()

        if "lab" in txt_lower or "blood" in txt_lower or "amh" in txt_lower or "karyotype" in txt_lower or "report" in txt_lower:
            suggested_type = "lab_report"
        elif "ultrasound" in txt_lower or "follicle" in txt_lower or "scan" in txt_lower or "endometrial" in txt_lower:
            suggested_type = "ultrasound"
        elif "retrieval" in txt_lower or "procedure" in txt_lower or "transfer" in txt_lower or "fet" in txt_lower:
            suggested_type = "procedure"
        elif "medication" in txt_lower or "gonal" in txt_lower or "prescription" in txt_lower:
            suggested_type = "medication_record"
        elif "discharge" in txt_lower or "summary" in txt_lower:
            suggested_type = "discharge_summary"

        today_str = date.today().isoformat()
        return {
            "suggested_title": suggested_title,
            "suggested_doc_type": suggested_type,
            "suggested_clinical_date": today_str,
            "is_ai_suggestion": True
        }

    @staticmethod
    async def upload_document(
        patient_id: str,
        file: UploadFile,
        staff: StaffProfile,
        token: str
    ) -> Dict[str, Any]:
        """Uploads a new document for a patient with strict write/admin grant check, content hash duplicate detection, and text extraction."""
        # 1. Enforce write/admin access grant (fail 403 if read-only)
        await PatientService.verify_staff_patient_write_access(patient_id, staff, token)

        filename = file.filename or "uploaded_doc.pdf"
        file_bytes = await file.read()
        if len(file_bytes) > MAX_FILE_BYTES:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File exceeds maximum allowed size limit of 15 MB.")

        ext = DocumentIntakeService._validate_magic_bytes(file_bytes, filename)
        content_hash = DocumentIntakeService._calculate_content_hash(file_bytes)

        supabase_url = settings.SUPABASE_URL.rstrip('/')
        auth_header = _get_auth_header(token)
        headers = {
            "Authorization": f"Bearer {auth_header}",
            "apikey": settings.SUPABASE_ANON_KEY
        }
        client = get_http_client()

        # 2. Scoped Duplicate Check (scoped strictly to patient_id)
        dup_url = f"{supabase_url}/rest/v1/patient_documents?patient_id=eq.{patient_id}&content_hash=eq.{content_hash}&select=id,title,current_version"
        res_dup = await client.get(dup_url, headers=headers)
        if res_dup.status_code == 200 and res_dup.json():
            dup_item = res_dup.json()[0]
            await AuditService.log_event(staff.id, patient_id, "DUPLICATE_DOCUMENT_ATTEMPT", f"/api/v1/patients/{patient_id}/documents", {"hash": content_hash[:12]}, token)
            return {
                "status": "duplicate_detected",
                "message": f"Exact duplicate document already exists for this patient ('{dup_item['title']}').",
                "duplicate_document_id": dup_item["id"],
                "current_version": dup_item["current_version"]
            }

        # 3. Generate Storage Path & Save file locally / Supabase Storage
        doc_id = str(uuid.uuid4())
        version_id = str(uuid.uuid4())
        storage_rel_path = f"patients/{patient_id}/documents/{doc_id}/v1/{content_hash[:16]}{ext}"

        # Write storage file to scratch local storage directory
        storage_dir = os.path.join("scratch", "storage", "patients", patient_id, "documents", doc_id, "v1")
        os.makedirs(storage_dir, exist_ok=True)
        local_filepath = os.path.join(storage_dir, f"{content_hash[:16]}{ext}")
        with open(local_filepath, "wb") as f:
            f.write(file_bytes)

        # 4. Extract Text & Provenance
        mime_type = "application/pdf" if ext == ".pdf" else f"image/{ext.replace('.', '')}"
        extraction_res = PDFExtractor.extract_text_and_provenance(local_filepath, mime_type)

        if extraction_res["page_count"] > MAX_PAGE_COUNT:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Document exceeds maximum page limit of {MAX_PAGE_COUNT} pages.")

        extracted_text = extraction_res["extracted_text"]
        extraction_status = extraction_res["status"]
        provenance = extraction_res["provenance"]
        error_msg = extraction_res.get("error")

        suggestions = DocumentIntakeService._generate_metadata_suggestions(filename, extracted_text)

        # 5. Insert record into patient_documents (status='draft', review_status='pending_review')
        doc_payload = {
            "id": doc_id,
            "patient_id": patient_id,
            "title": suggestions["suggested_title"],
            "doc_type": suggestions["suggested_doc_type"],
            "clinical_date": suggestions["suggested_clinical_date"],
            "status": "draft",
            "review_status": "pending_review",
            "storage_path": storage_rel_path,
            "mime_type": mime_type,
            "file_size": len(file_bytes),
            "current_version": 1,
            "content_hash": content_hash
        }
        res_doc_ins = await client.post(f"{supabase_url}/rest/v1/patient_documents", json=doc_payload, headers=headers)
        if res_doc_ins.status_code not in (200, 201):
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error inserting document: {res_doc_ins.text}")

        # 6. Insert record into patient_document_versions
        ver_payload = {
            "id": version_id,
            "document_id": doc_id,
            "version_number": 1,
            "storage_path": storage_rel_path,
            "extracted_text": extracted_text,
            "page_count": extraction_res["page_count"],
            "extraction_status": extraction_status,
            "extraction_provenance": provenance,
            "error_message": error_msg,
            "metadata_suggestions": suggestions,
            "content_hash": content_hash,
            "uploaded_by": staff.id
        }
        res_ver_ins = await client.post(f"{supabase_url}/rest/v1/patient_document_versions", json=ver_payload, headers=headers)
        if res_ver_ins.status_code not in (200, 201):
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error inserting document version: {res_ver_ins.text}")

        await AuditService.log_event(staff.id, patient_id, "DOCUMENT_UPLOADED", f"/api/v1/patients/{patient_id}/documents/{doc_id}", {"title": doc_payload["title"], "version": 1}, token)

        return {
            "status": "success",
            "document_id": doc_id,
            "version_id": version_id,
            "version_number": 1,
            "review_status": "pending_review",
            "extraction_status": extraction_status,
            "extraction_provenance": provenance,
            "extracted_text": extracted_text,
            "metadata_suggestions": suggestions,
            "error_message": error_msg
        }

    @staticmethod
    async def upload_new_version(
        patient_id: str,
        document_id: str,
        file: UploadFile,
        staff: StaffProfile,
        token: str
    ) -> Dict[str, Any]:
        """Uploads a new version N+1 for an existing document without overwriting previous versions."""
        await PatientService.verify_staff_patient_write_access(patient_id, staff, token)

        supabase_url = settings.SUPABASE_URL.rstrip('/')
        auth_header = _get_auth_header(token)
        headers = {
            "Authorization": f"Bearer {auth_header}",
            "apikey": settings.SUPABASE_ANON_KEY
        }
        client = get_http_client()

        # Check existing document
        res_doc = await client.get(f"{supabase_url}/rest/v1/patient_documents?id=eq.{document_id}&patient_id=eq.{patient_id}", headers=headers)
        if res_doc.status_code != 200 or not res_doc.json():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Target document record not found.")

        doc_record = res_doc.json()[0]

        # Atomic Concurrency-Safe Version Allocation via Database RPC
        rpc_url = f"{supabase_url}/rest/v1/rpc/allocate_next_document_version"
        res_rpc = await client.post(rpc_url, json={"p_document_id": document_id}, headers=headers)
        if res_rpc.status_code == 200:
            new_version_number = int(res_rpc.json())
        else:
            current_max_version = doc_record.get("current_version", 1)
            new_version_number = current_max_version + 1

        filename = file.filename or "uploaded_version.pdf"
        file_bytes = await file.read()
        if len(file_bytes) > MAX_FILE_BYTES:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File exceeds maximum allowed size limit of 15 MB.")

        ext = DocumentIntakeService._validate_magic_bytes(file_bytes, filename)
        content_hash = DocumentIntakeService._calculate_content_hash(file_bytes)

        # Scoped duplicate check for this document
        ver_dup_url = f"{supabase_url}/rest/v1/patient_document_versions?document_id=eq.{document_id}&content_hash=eq.{content_hash}&select=version_number"
        res_vdup = await client.get(ver_dup_url, headers=headers)
        if res_vdup.status_code == 200 and res_vdup.json():
            v_num = res_vdup.json()[0]["version_number"]
            return {
                "status": "duplicate_version_detected",
                "message": f"Exact duplicate file already exists as Version {v_num} for this document.",
                "existing_version_number": v_num
            }

        # Atomic Concurrency-Safe Version Allocation AND Reservation via Database RPC
        rpc_url = f"{supabase_url}/rest/v1/rpc/create_atomic_document_version"
        temp_rel_path = f"patients/{patient_id}/documents/{document_id}/pending/{content_hash[:16]}{ext}"
        rpc_payload = {
            "p_document_id": document_id,
            "p_storage_path": temp_rel_path,
            "p_content_hash": content_hash,
            "p_extraction_provenance": "pending"
        }
        res_rpc = await client.post(rpc_url, json=rpc_payload, headers=headers)
        
        if res_rpc.status_code == 200 and res_rpc.json():
            rpc_res = res_rpc.json()
            ver_row = rpc_res[0] if isinstance(rpc_res, list) else rpc_res
            version_id = ver_row["id"]
            new_version_number = int(ver_row["version_number"])
        else:
            # Fallback atomic allocation if RPC function not deployed yet
            rpc_alloc_url = f"{supabase_url}/rest/v1/rpc/allocate_next_document_version"
            res_alloc = await client.post(rpc_alloc_url, json={"p_document_id": document_id}, headers=headers)
            if res_alloc.status_code == 200:
                new_version_number = int(res_alloc.json())
            else:
                current_max = doc_record.get("current_version", 1)
                new_version_number = current_max + 1

            version_id = str(uuid.uuid4())
            temp_rel_path = f"patients/{patient_id}/documents/{document_id}/v{new_version_number}/{content_hash[:16]}{ext}"
            ver_payload = {
                "id": version_id,
                "document_id": document_id,
                "version_number": new_version_number,
                "storage_path": temp_rel_path,
                "content_hash": content_hash,
                "uploaded_by": staff.id,
                "review_status": "pending_review",
                "extraction_status": "pending"
            }
            res_ins = await client.post(f"{supabase_url}/rest/v1/patient_document_versions", json=ver_payload, headers=headers)
            if res_ins.status_code not in (200, 201):
                # If unique constraint violation occurred due to concurrent insert
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Concurrent version creation conflict detected. Please retry.")

        storage_rel_path = f"patients/{patient_id}/documents/{document_id}/v{new_version_number}/{content_hash[:16]}{ext}"
        storage_dir = os.path.join("scratch", "storage", "patients", patient_id, "documents", document_id, f"v{new_version_number}")
        
        try:
            os.makedirs(storage_dir, exist_ok=True)
            local_filepath = os.path.join(storage_dir, f"{content_hash[:16]}{ext}")
            with open(local_filepath, "wb") as f:
                f.write(file_bytes)

            mime_type = "application/pdf" if ext == ".pdf" else f"image/{ext.replace('.', '')}"
            extraction_res = PDFExtractor.extract_text_and_provenance(local_filepath, mime_type)

            extracted_text = extraction_res["extracted_text"]
            extraction_status = extraction_res["status"]
            provenance = extraction_res["provenance"]
            error_msg = extraction_res.get("error")

            suggestions = DocumentIntakeService._generate_metadata_suggestions(filename, extracted_text)

            # Update reserved version record with extracted text, provenance, and final storage path
            ver_update = {
                "storage_path": storage_rel_path,
                "extracted_text": extracted_text,
                "page_count": extraction_res["page_count"],
                "extraction_status": extraction_status,
                "extraction_provenance": provenance,
                "error_message": error_msg,
                "metadata_suggestions": suggestions
            }
            await client.patch(f"{supabase_url}/rest/v1/patient_document_versions?id=eq.{version_id}", json=ver_update, headers=headers)

            await AuditService.log_event(staff.id, patient_id, "DOCUMENT_VERSION_CREATED", f"/api/v1/patients/{patient_id}/documents/{document_id}/versions", {"version_number": new_version_number}, token)

            return {
                "status": "success",
                "document_id": document_id,
                "version_id": version_id,
                "version_number": new_version_number,
                "review_status": "pending_review",
                "extraction_status": extraction_status,
                "extraction_provenance": provenance,
                "extracted_text": extracted_text,
                "metadata_suggestions": suggestions,
                "error_message": error_msg
            }
        except Exception as exc:
            # Handle storage or extraction failure by marking extraction_status failed without corrupting database
            fail_update = {
                "extraction_status": "failed",
                "error_message": f"Storage/processing error: {str(exc)}"
            }
            await client.patch(f"{supabase_url}/rest/v1/patient_document_versions?id=eq.{version_id}", json=fail_update, headers=headers)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Version upload processing failed: {str(exc)}")

    @staticmethod
    async def review_and_publish_document(
        patient_id: str,
        document_id: str,
        payload: Dict[str, Any],
        staff: StaffProfile,
        token: str
    ) -> Dict[str, Any]:
        """Reviews metadata and extracted text, links order if confirmed, marks document final/reviewed, and triggers idempotent vector indexing."""
        await PatientService.verify_staff_patient_write_access(patient_id, staff, token)

        title = payload.get("title", "").strip()
        doc_type = payload.get("doc_type", "").strip()
        clinical_date_str = payload.get("clinical_date", "").strip()
        extracted_text = payload.get("extracted_text", "").strip()
        order_id = payload.get("order_id")

        if not title or not doc_type or not clinical_date_str:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Title, doc_type, and clinical_date are required fields for human review.")

        supabase_url = settings.SUPABASE_URL.rstrip('/')
        auth_header = _get_auth_header(token)
        headers = {
            "Authorization": f"Bearer {auth_header}",
            "apikey": settings.SUPABASE_ANON_KEY,
            "Prefer": "return=representation"
        }
        client = get_http_client()

        # Fetch current document and latest version
        res_doc = await client.get(f"{supabase_url}/rest/v1/patient_documents?id=eq.{document_id}&patient_id=eq.{patient_id}", headers=headers)
        if res_doc.status_code != 200 or not res_doc.json():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document record not found.")

        doc_rec = res_doc.json()[0]
        cur_ver = doc_rec.get("current_version", 1)

        res_ver = await client.get(f"{supabase_url}/rest/v1/patient_document_versions?document_id=eq.{document_id}&version_number=eq.{cur_ver}", headers=headers)
        if res_ver.status_code != 200 or not res_ver.json():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document version record not found.")

        ver_rec = res_ver.json()[0]
        version_id = ver_rec["id"]

        # 1. Update patient_documents record
        upd_doc = {
            "title": title,
            "doc_type": doc_type,
            "clinical_date": clinical_date_str,
            "status": "final",
            "review_status": "reviewed",
            "reviewed_by": staff.id,
            "reviewed_at": datetime.utcnow().isoformat(),
            "order_id": order_id
        }
        res_doc_upd = await client.patch(f"{supabase_url}/rest/v1/patient_documents?id=eq.{document_id}", json=upd_doc, headers=headers)
        if res_doc_upd.status_code not in (200, 204):
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update reviewed document record.")

        # 2. Update patient_document_versions record
        upd_ver = {
            "extracted_text": extracted_text,
            "extraction_status": "processed" if extracted_text else "failed"
        }
        await client.patch(f"{supabase_url}/rest/v1/patient_document_versions?id=eq.{version_id}", json=upd_ver, headers=headers)

        # 3. Idempotent Vector Indexing for Retrieval (BAAI/bge-small-en-v1.5, 384 dimensions)
        try:
            pages = [{"page_number": 1, "text": extracted_text}]
            chunks = TextChunker.chunk_pages(
                patient_id=patient_id,
                document_id=document_id,
                document_version_id=version_id,
                pages=pages
            )

            # Idempotently delete existing chunks for this (document_id, version_id)
            await client.delete(f"{supabase_url}/rest/v1/patient_document_chunks?document_id=eq.{document_id}&document_version_id=eq.{version_id}", headers=headers)

            # Embed and insert chunks
            for chunk in chunks:
                vec = encode_text_sync(chunk["chunk_text"])
                chunk["embedding"] = vec
                await client.post(f"{supabase_url}/rest/v1/patient_document_chunks", json=chunk, headers=headers)


            logger.info(f"Idempotent vector indexing completed for doc {document_id} ver {cur_ver} ({len(chunks)} chunks)")
        except Exception as idx_exc:
            logger.warning(f"Vector indexing failed for document {document_id}: {idx_exc}")

        # If order_id link confirmed, mark pending order complete in timeline
        if order_id:
            try:
                await client.patch(
                    f"{supabase_url}/rest/v1/patient_timeline_events?id=eq.{order_id}&patient_id=eq.{patient_id}",
                    json={"summary": f"Completed & Linked to Report: {title}"},
                    headers=headers
                )
            except Exception as ord_exc:
                logger.warning(f"Order linkage update warning: {ord_exc}")

        await AuditService.log_event(staff.id, patient_id, "DOCUMENT_REVIEWED_AND_PUBLISHED", f"/api/v1/patients/{patient_id}/documents/{document_id}/review", {"title": title, "version": cur_ver}, token)

        return {
            "status": "success",
            "document_id": document_id,
            "version_id": version_id,
            "version_number": cur_ver,
            "review_status": "reviewed",
            "published_status": "final"
        }

    @staticmethod
    async def get_document_versions(
        patient_id: str,
        document_id: str,
        staff: StaffProfile,
        token: str
    ) -> List[Dict[str, Any]]:
        """Returns version history list for a document with uploader info, dates, and text comparison metrics."""
        await PatientService.verify_staff_patient_access(patient_id, staff, token)

        supabase_url = settings.SUPABASE_URL.rstrip('/')
        auth_header = _get_auth_header(token)
        headers = {
            "Authorization": f"Bearer {auth_header}",
            "apikey": settings.SUPABASE_ANON_KEY
        }
        client = get_http_client()

        res_ver = await client.get(
            f"{supabase_url}/rest/v1/patient_document_versions?document_id=eq.{document_id}&order=version_number.desc",
            headers=headers
        )
        if res_ver.status_code != 200:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Failed to load document version history.")

        versions = res_ver.json()
        version_items: List[Dict[str, Any]] = []

        for i, ver in enumerate(versions):
            prev_txt = versions[i + 1]["extracted_text"] if i + 1 < len(versions) and versions[i + 1].get("extracted_text") else ""
            curr_txt = ver.get("extracted_text") or ""

            # Diff comparison summary
            diff_lines = list(difflib.unified_diff(
                prev_txt.splitlines(),
                curr_txt.splitlines(),
                fromfile=f"v{ver.get('version_number', 1)-1}",
                tofile=f"v{ver.get('version_number', 1)}",
                lineterm=""
            ))

            version_items.append({
                "id": ver["id"],
                "document_id": ver["document_id"],
                "version_number": ver["version_number"],
                "storage_path": ver["storage_path"],
                "extracted_text": curr_txt,
                "page_count": ver.get("page_count", 1),
                "extraction_status": ver.get("extraction_status", "processed"),
                "extraction_provenance": ver.get("extraction_provenance", "pypdf_text"),
                "error_message": ver.get("error_message"),
                "metadata_suggestions": ver.get("metadata_suggestions") or {},
                "created_at": ver.get("created_at"),
                "diff_summary": "\n".join(diff_lines[:30]) if diff_lines else "No textual changes."
            })

        AuditService.log_event_background(staff.id, patient_id, "VIEW_DOCUMENT_VERSIONS", f"/api/v1/patients/{patient_id}/documents/{document_id}/versions", {"count": len(version_items)}, token)
        return version_items
