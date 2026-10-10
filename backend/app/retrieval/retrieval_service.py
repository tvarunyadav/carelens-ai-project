import os
import logging
import asyncio
from typing import Dict, Any, List, Optional, Tuple
import httpx
from fastapi import HTTPException, status

from app.core.config import settings
from app.core.http_client import get_http_client
from app.schemas.models import StaffProfile
from app.patients.service import PatientService
from app.retrieval.embedding import generate_embedding
from app.retrieval.llm_service import (
    LLMService, 
    AINotConfiguredException, 
    AIModelUnavailableException, 
    AIProviderUnavailableException
)

logger = logging.getLogger(__name__)

class RetrievalService:
    @staticmethod
    async def gather_patient_context(
        patient_id: str,
        staff: StaffProfile,
        token: str,
        query: Optional[str] = None
    ) -> Tuple[List[Dict[str, Any]], str]:
        """
        Retrieves authorized patient evidence:
        1. Patient detail (demographics, DOB, MRN)
        2. Vector similarity chunks for relevant query terms (or general summary chunks)
        3. Structured fertility cycles (sorted by start_date DESC)
        4. Pending lab orders & documents
        5. Timeline events
        Returns (evidence_items, formatted_context_text).
        """
        # Step 1: Verify patient access grant
        await PatientService.verify_staff_patient_access(patient_id, staff, token)

        supabase_url = settings.SUPABASE_URL.rstrip('/')
        auth_header = token if token else settings.SUPABASE_ANON_KEY
        headers = {
            "Authorization": f"Bearer {auth_header}",
            "apikey": settings.SUPABASE_ANON_KEY
        }
        client = get_http_client()

        # Gather parallel structured records
        pat_task = client.get(f"{supabase_url}/rest/v1/patients?id=eq.{patient_id}&select=*", headers=headers)
        cyc_task = client.get(f"{supabase_url}/rest/v1/fertility_cycles?patient_id=eq.{patient_id}&order=start_date.desc", headers=headers)
        doc_task = client.get(f"{supabase_url}/rest/v1/patient_documents?patient_id=eq.{patient_id}&order=clinical_date.desc", headers=headers)
        time_task = client.get(f"{supabase_url}/rest/v1/patient_timeline_events?patient_id=eq.{patient_id}&order=event_date.desc", headers=headers)

        pat_res, cyc_res, doc_res, time_res = await asyncio.gather(pat_task, cyc_task, doc_task, time_task, return_exceptions=True)

        patient_info = pat_res.json()[0] if (not isinstance(pat_res, Exception) and pat_res.status_code == 200 and pat_res.json()) else {}
        cycles = cyc_res.json() if (not isinstance(cyc_res, Exception) and cyc_res.status_code == 200) else []
        raw_documents = doc_res.json() if (not isinstance(doc_res, Exception) and doc_res.status_code == 200) else []
        documents = [d for d in raw_documents if d.get("review_status", "reviewed") == "reviewed" and d.get("status") in ("reviewed", "final", "pending")]
        events = time_res.json() if (not isinstance(time_res, Exception) and time_res.status_code == 200) else []

        # Vector retrieval for chunks
        chunks = []
        try:
            search_text = query if query else "clinical history consultation IVF lab ultrasound medications"
            query_embedding = await generate_embedding(search_text)

            rpc_url = f"{supabase_url}/rest/v1/rpc/match_patient_document_chunks"
            rpc_payload = {
                "target_patient_id": patient_id,
                "query_embedding": query_embedding,
                "match_threshold": 0.1,
                "match_count": 8
            }
            res_chunks = await client.post(rpc_url, json=rpc_payload, headers=headers)
            if res_chunks.status_code == 200:
                chunks = res_chunks.json()
        except Exception as exc:
            logger.warning(f"Vector retrieval RPC failed or unindexed: {str(exc)}")

        evidence_items: List[Dict[str, Any]] = []
        context_lines: List[str] = []
        ev_counter = 1

        # Add Patient Header Info
        if patient_info:
            context_lines.append(f"PATIENT DEMOGRAPHICS: Name: {patient_info.get('first_name')} {patient_info.get('last_name')}, MRN: {patient_info.get('mrn')}, DOB: {patient_info.get('dob')}, Gender: {patient_info.get('gender')}")

        # Add Chunks Evidence (Only for reviewed documents)
        doc_map = {d["id"]: d for d in documents}
        for chk in chunks:
            doc_meta = doc_map.get(chk.get("document_id"))
            if not doc_meta or doc_meta.get("review_status") == "pending_review":
                continue  # Skip unreviewed draft chunks

            ev_id = f"EV-{ev_counter}"
            ev_counter += 1
            doc_meta = doc_map.get(chk.get("document_id"), {})
            title = doc_meta.get("title", "Clinical Document")
            page_num = chk.get("page_number", 1)
            
            ev_item = {
                "id": ev_id,
                "type": "document_chunk",
                "title": title,
                "document_id": chk.get("document_id"),
                "document_version_id": chk.get("document_version_id"),
                "page_number": page_num,
                "date": doc_meta.get("clinical_date"),
                "snippet": chk.get("chunk_text")
            }
            evidence_items.append(ev_item)
            context_lines.append(f"[{ev_id}] DOCUMENT '{title}' (Page {page_num}, Date: {doc_meta.get('clinical_date')}):\n{chk.get('chunk_text')}")

        # Add Fertility Cycles Evidence
        for cyc in cycles:
            ev_id = f"EV-{ev_counter}"
            ev_counter += 1
            ev_item = {
                "id": ev_id,
                "type": "fertility_cycle",
                "title": cyc.get("cycle_name"),
                "document_id": None,
                "document_version_id": None,
                "page_number": None,
                "date": cyc.get("start_date"),
                "snippet": f"Status: {cyc.get('status')}, Metrics: {cyc.get('notes_json')}"
            }
            evidence_items.append(ev_item)
            context_lines.append(f"[{ev_id}] FERTILITY CYCLE '{cyc.get('cycle_name')}' (Start: {cyc.get('start_date')}, End: {cyc.get('end_date')}, Status: {cyc.get('status')}):\nMetrics: {cyc.get('notes_json')}")

        # Add Pending Orders Evidence
        pending_docs = [d for d in documents if d.get("status") == "pending"]
        for pdoc in pending_docs:
            ev_id = f"EV-{ev_counter}"
            ev_counter += 1
            ev_item = {
                "id": ev_id,
                "type": "pending_order",
                "title": pdoc.get("title"),
                "document_id": pdoc.get("id"),
                "document_version_id": None,
                "page_number": None,
                "date": pdoc.get("clinical_date"),
                "snippet": f"Pending Order: {pdoc.get('title')} requested on {pdoc.get('clinical_date')}. Result not yet recorded."
            }
            evidence_items.append(ev_item)
            context_lines.append(f"[{ev_id}] PENDING LAB ORDER '{pdoc.get('title')}' (Requested Date: {pdoc.get('clinical_date')}): Result not yet recorded.")

        # Add Timeline Events Evidence
        for ev in events:
            ev_id = f"EV-{ev_counter}"
            ev_counter += 1
            ev_item = {
                "id": ev_id,
                "type": "timeline_event",
                "title": ev.get("title"),
                "document_id": ev.get("document_id"),
                "document_version_id": None,
                "page_number": None,
                "date": ev.get("event_date"),
                "snippet": ev.get("summary")
            }
            evidence_items.append(ev_item)
            context_lines.append(f"[{ev_id}] TIMELINE EVENT '{ev.get('title')}' ({ev.get('event_type')}, Date: {ev.get('event_date')}): {ev.get('summary')}")

        formatted_context = "\n\n".join(context_lines)
        return evidence_items, formatted_context

    @staticmethod
    async def generate_patient_summary(
        patient_id: str,
        staff: StaffProfile,
        token: str
    ) -> Dict[str, Any]:
        """
        Generates grounded pre-consultation patient history summary.
        """
        evidence_items, context_text = await RetrievalService.gather_patient_context(patient_id, staff, token)

        if not LLMService.is_configured():
            summary_lines = ["### Patient History Overview"]
            for item in evidence_items[:5]:
                summary_lines.append(f"- **{item['title']}** ({item.get('date')}): {item['snippet'][:120]}...")

            return {
                "status": "ai_not_configured",
                "answer": "\n".join(summary_lines),
                "provider": "Structured Records Engine",
                "evidence": evidence_items,
                "evidence_citations": [e["id"] for e in evidence_items[:5]],
                "evidence_limitations": "AI provider API key is not configured in backend environment."
            }

        prompt = f"""Generate a concise, factual, grounded pre-consultation summary for the patient based ONLY on the context below.

CLINICAL CONTEXT:
{context_text}
"""
        try:
            response_dict, provider = await LLMService.generate_grounded_response(prompt, evidence_items)
            return {
                "status": "success",
                "answer": response_dict.get("answer", ""),
                "provider": provider,
                "evidence": evidence_items,
                "evidence_citations": response_dict.get("evidence_citations", []),
                "evidence_limitations": response_dict.get("evidence_limitations")
            }
        except AINotConfiguredException as exc:
            return {
                "status": "ai_not_configured",
                "answer": "AI provider keys not configured in backend environment.",
                "provider": "Structured Records Engine",
                "evidence": evidence_items,
                "evidence_citations": [e["id"] for e in evidence_items[:5]],
                "evidence_limitations": str(exc)
            }
        except AIModelUnavailableException as exc:
            return {
                "status": "ai_model_unavailable",
                "answer": "Selected AI model is currently unavailable (404 / Model Not Found). Medical records remain fully accessible below.",
                "provider": "Error Fallback Engine",
                "evidence": evidence_items,
                "evidence_citations": [],
                "evidence_limitations": f"AI_MODEL_UNAVAILABLE: {str(exc)}"
            }
        except AIProviderUnavailableException as exc:
            return {
                "status": "ai_provider_unavailable",
                "answer": "AI service provider is experiencing an outage or high demand. Medical records remain fully accessible below.",
                "provider": "Error Fallback Engine",
                "evidence": evidence_items,
                "evidence_citations": [],
                "evidence_limitations": f"AI_PROVIDER_UNAVAILABLE: {str(exc)}"
            }
        except Exception as exc:
            return {
                "status": "error",
                "answer": "An unexpected error occurred while calling the AI model.",
                "provider": "Error Fallback Engine",
                "evidence": evidence_items,
                "evidence_citations": [],
                "evidence_limitations": str(exc)
            }

    @staticmethod
    async def answer_patient_query(
        patient_id: str,
        query: str,
        staff: StaffProfile,
        token: str,
        input_language: str = "en",
        answer_language: str = "en"
    ) -> Dict[str, Any]:
        """
        Answers plain-language patient history question grounded strictly in authorized evidence.
        Written answer is ALWAYS generated in English with citations [EV-1].
        Detects question language ('en', 'ta', 'mixed') and generates optional Tamil TTS text for speech readout.
        """
        # Genuine language detection & cross-language normalization into English for vector search
        normalized_query, detected_lang = await LLMService.normalize_and_detect_language(query)
        
        evidence_items, context_text = await RetrievalService.gather_patient_context(patient_id, staff, token, normalized_query)

        if not LLMService.is_configured():
            q_lower = (query + " " + normalized_query).lower()
            cited = []
            sections = []

            if "cycle" in q_lower or "சுழற்சி" in query or "வரிசை" in query:
                cyc_items = [e for e in evidence_items if e["type"] == "fertility_cycle"]
                if cyc_items:
                    lines = ["Recorded fertility cycle(s):"]
                    for c in cyc_items[:2]:
                        lines.append(f"- [{c['id']}] **{c['title']}** (Started: {c['date']}): {c['snippet']}")
                        cited.append(c['id'])
                    sections.append("\n".join(lines))
                else:
                    sections.append("No fertility cycle records found in patient file.")

            if "pending" in q_lower or "test" in q_lower or "report" in q_lower or "request" in q_lower or "order" in q_lower or "நிலுவையில்" in query or "அறிக்கை" in query:
                pend_items = [e for e in evidence_items if e["type"] == "pending_order"]
                if pend_items:
                    lines = ["Pending order(s) & lab requests:"]
                    for p in pend_items:
                        lines.append(f"- [{p['id']}] **{p['title']}** requested on {p['date']}. Result not yet recorded.")
                        cited.append(p['id'])
                    sections.append("\n".join(lines))
                else:
                    sections.append("No pending orders or outstanding lab requests found in patient records.")

            if sections:
                answer_text = "\n\n".join(sections)
            else:
                answer_text = f"Loaded {len(evidence_items)} evidence records. Configure AI API keys in backend environment for natural language completions."

            return {
                "status": "ai_not_configured",
                "answer": answer_text,
                "provider": "Structured Records Engine",
                "evidence": evidence_items,
                "evidence_citations": cited,
                "evidence_limitations": "AI provider API key is not configured in backend environment.",
                "detected_language": detected_lang,
                "tamil_audio_text": None
            }

        prompt = f"""Answer the following plain-language question grounded ONLY in the provided clinical context.
The written answer MUST be in English and MUST include bracketed evidence citations like [EV-1], [EV-2].

ORIGINAL USER QUESTION: "{query}"
SEARCH NORMALIZED QUERY: "{normalized_query}"

CLINICAL CONTEXT:
{context_text}
"""
        try:
            response_dict, provider = await LLMService.generate_grounded_response(prompt, evidence_items, answer_language="en")
            english_answer = response_dict.get("answer", "")

            # If question was Tamil or mixed, generate Tamil text specifically for optional TTS readout
            tamil_audio_text = None
            if detected_lang in ("ta", "mixed"):
                tamil_audio_text = await LLMService.generate_tamil_audio_translation(english_answer)

            return {
                "status": "success",
                "answer": english_answer,
                "provider": provider,
                "evidence": evidence_items,
                "evidence_citations": response_dict.get("evidence_citations", []),
                "evidence_limitations": response_dict.get("evidence_limitations"),
                "detected_language": detected_lang,
                "tamil_audio_text": tamil_audio_text
            }
        except AINotConfiguredException as exc:
            return {
                "status": "ai_not_configured",
                "answer": "AI provider keys not configured in backend environment.",
                "provider": "Structured Records Engine",
                "evidence": evidence_items,
                "evidence_citations": [],
                "evidence_limitations": str(exc),
                "detected_language": detected_lang,
                "tamil_audio_text": None
            }
        except AIModelUnavailableException as exc:
            return {
                "status": "ai_model_unavailable",
                "answer": "Selected AI model is currently unavailable (404 / Model Not Found). Medical records remain fully accessible below.",
                "provider": "Error Fallback Engine",
                "evidence": evidence_items,
                "evidence_citations": [],
                "evidence_limitations": f"AI_MODEL_UNAVAILABLE: {str(exc)}",
                "detected_language": detected_lang,
                "tamil_audio_text": None
            }
        except AIProviderUnavailableException as exc:
            return {
                "status": "ai_provider_unavailable",
                "answer": "AI service provider is experiencing an outage or high demand. Medical records remain fully accessible below.",
                "provider": "Error Fallback Engine",
                "evidence": evidence_items,
                "evidence_citations": [],
                "evidence_limitations": f"AI_PROVIDER_UNAVAILABLE: {str(exc)}",
                "detected_language": detected_lang,
                "tamil_audio_text": None
            }
        except Exception as exc:
            return {
                "status": "error",
                "answer": "An unexpected error occurred while generating AI response.",
                "provider": "Error Fallback Engine",
                "evidence": evidence_items,
                "evidence_citations": [],
                "evidence_limitations": str(exc),
                "detected_language": detected_lang,
                "tamil_audio_text": None
            }


