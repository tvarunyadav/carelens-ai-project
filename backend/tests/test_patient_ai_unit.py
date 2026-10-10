import pytest
from datetime import date
from unittest.mock import patch, AsyncMock
from httpx import AsyncClient, ASGITransport, Response
from fastapi import HTTPException
from app.main import app
from app.auth.verifier import verify_supabase_token
from app.schemas.models import StaffProfile, Patient
from app.retrieval.llm_service import LLMService, AIModelUnavailableException
from app.retrieval.retrieval_service import RetrievalService


STAFF_BOB = StaffProfile(
    id="7b7c7b68-8c02-4081-a5a3-18b6cdcb26f7",
    email="coord.bob@clinic.org",
    full_name="Bob Vance",
    role="coordinator"
)

SOPHIA_ID = "33333333-3333-3333-3333-333333333333"
ELEANOR_ID = "11111111-1111-1111-1111-111111111111"

@pytest.mark.asyncio
async def test_ai_summary_unconfigured_fallback():
    app.dependency_overrides[verify_supabase_token] = lambda: STAFF_BOB
    try:
        mock_evidence = [
            {"id": "EV-1", "type": "fertility_cycle", "title": "IVF Cycle 1", "date": "2026-05-01", "snippet": "Oocytes retrieved: 10"}
        ]
        with patch("app.retrieval.retrieval_service.RetrievalService.gather_patient_context", return_value=(mock_evidence, "Context...")):
            with patch("app.retrieval.llm_service.LLMService.is_configured", return_value=False):
                transport = ASGITransport(app=app)
                async with AsyncClient(transport=transport, base_url="http://testserver") as client:
                    res = await client.post(f"/api/v1/patients/{SOPHIA_ID}/ai/summary", headers={"Authorization": "Bearer mock-token"})
                    assert res.status_code == 200
                    data = res.json()
                    assert data["status"] == "ai_not_configured"
                    assert "Structured Records Engine" in data["provider"]
                    assert len(data["evidence"]) >= 1
    finally:
        app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_ai_query_last_two_cycles():
    app.dependency_overrides[verify_supabase_token] = lambda: STAFF_BOB
    try:
        mock_evidence = [
            {"id": "EV-1", "type": "fertility_cycle", "title": "IVF Cycle 1", "date": "2026-05-01", "snippet": "Oocytes: 10"},
            {"id": "EV-2", "type": "fertility_cycle", "title": "IVF Cycle 2 - FET", "date": "2026-07-10", "snippet": "Embryo: Day 5 4AA"}
        ]
        with patch("app.retrieval.retrieval_service.RetrievalService.gather_patient_context", return_value=(mock_evidence, "Context...")):
            with patch("app.retrieval.llm_service.LLMService.is_configured", return_value=False):
                transport = ASGITransport(app=app)
                async with AsyncClient(transport=transport, base_url="http://testserver") as client:
                    res = await client.post(
                        f"/api/v1/patients/{SOPHIA_ID}/ai/query",
                        json={"query": "What were her last two cycles?"},
                        headers={"Authorization": "Bearer mock-token"}
                    )
                    assert res.status_code == 200
                    data = res.json()
                    assert "IVF Cycle 1" in data["answer"] or "fertility cycle" in data["answer"]
    finally:
        app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_ai_query_pending_reports():
    app.dependency_overrides[verify_supabase_token] = lambda: STAFF_BOB
    try:
        mock_evidence = [
            {"id": "EV-1", "type": "pending_order", "title": "Karyotype Panel", "date": "2026-04-25", "snippet": "Result not yet recorded."}
        ]
        with patch("app.retrieval.retrieval_service.RetrievalService.gather_patient_context", return_value=(mock_evidence, "Context...")):
            with patch("app.retrieval.llm_service.LLMService.is_configured", return_value=False):
                transport = ASGITransport(app=app)
                async with AsyncClient(transport=transport, base_url="http://testserver") as client:
                    res = await client.post(
                        f"/api/v1/patients/{SOPHIA_ID}/ai/query",
                        json={"query": "Which reports are pending?"},
                        headers={"Authorization": "Bearer mock-token"}
                    )
                    assert res.status_code == 200
                    data = res.json()
                    assert "Karyotype Panel" in data["answer"] or "pending" in data["answer"]
    finally:
        app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_ai_unauthorized_patient_retrieval_denied():
    app.dependency_overrides[verify_supabase_token] = lambda: STAFF_BOB
    try:
        with patch("app.patients.service.PatientService.verify_staff_patient_access", side_effect=HTTPException(403, "Access denied")):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://testserver") as client:
                res = await client.post(
                    f"/api/v1/patients/{ELEANOR_ID}/ai/summary",
                    headers={"Authorization": "Bearer mock-token"}
                )
                assert res.status_code == 403
    finally:
        app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_reference_validation_strips_fabricated_citations():
    mock_evidence = [{"id": "EV-1", "type": "document_chunk", "title": "Consultation", "snippet": "Patient is a 43-year-old female."}]
    fake_model_output = '{"answer": "Patient is 43 [EV-1].\\nPatient had liver transplant in 2024 [EV-999_FAKE].", "evidence_citations": ["EV-1", "EV-999_FAKE"]}'
    
    with patch("app.core.config.settings.GEMINI_API_KEY", "real-gemini-key"):
        with patch("app.retrieval.llm_service.LLMService.is_configured", return_value=True):
            with patch("app.retrieval.llm_service.LLMService.call_gemini", return_value=fake_model_output):
                with patch.object(LLMService, "call_groq", return_value=""):
                    resp, provider = await LLMService.generate_grounded_response("Query", mock_evidence)
                    assert "EV-1" in resp["evidence_citations"]
                    assert "EV-999_FAKE" not in resp["evidence_citations"]
                    assert "liver transplant" not in resp["answer"]
                    assert resp["evidence_limitations"] is not None
                    assert "invalid citation ID" in resp["evidence_limitations"]

@pytest.mark.asyncio
async def test_fabricated_claim_attached_to_valid_id_rejected():
    mock_evidence = [{"id": "EV-1", "type": "document_chunk", "title": "Initial Reproductive Consultation", "snippet": "Patient: Sophia Patel MRN: MRN-441029 Date: 2026-04-15. 43-year-old female evaluating primary infertility."}]
    fake_model_output = '{"answer": "Patient undergoing fertility evaluation [EV-1].\\nPatient had emergency liver transplant [EV-1].", "evidence_citations": ["EV-1"]}'
    
    with patch("app.core.config.settings.GEMINI_API_KEY", "real-gemini-key"):
        with patch("app.retrieval.llm_service.LLMService.is_configured", return_value=True):
            with patch("app.retrieval.llm_service.LLMService.call_gemini", return_value=fake_model_output):
                with patch.object(LLMService, "call_groq", return_value=""):
                    resp, provider = await LLMService.generate_grounded_response("Query", mock_evidence)
                    assert "fertility evaluation" in resp["answer"]
                    assert "liver transplant" not in resp["answer"]
                    assert resp["evidence_limitations"] is not None
                    assert "unsupported claim" in resp["evidence_limitations"] or "missing from evidence" in resp["evidence_limitations"]

@pytest.mark.asyncio
async def test_numeric_contradiction_rejected():
    mock_evidence = [{"id": "EV-1", "type": "document_chunk", "title": "Oocyte Retrieval", "snippet": "Embryology findings: 10 oocytes retrieved. AMH level: 2.8 ng/mL."}]
    fake_output = '{"answer": "Retrieved 10 oocytes [EV-1].\\nRetrieved 12 oocytes during cycle [EV-1].\\nAMH level was 1.8 ng/mL [EV-1].", "evidence_citations": ["EV-1"]}'
    
    with patch("app.core.config.settings.GEMINI_API_KEY", "real-gemini-key"):
        with patch("app.retrieval.llm_service.LLMService.is_configured", return_value=True):
            with patch("app.retrieval.llm_service.LLMService.call_gemini", return_value=fake_output):
                resp, _ = await LLMService.generate_grounded_response("Query", mock_evidence)
                assert "Retrieved 10 oocytes" in resp["answer"]
                assert "12 oocytes" not in resp["answer"]
                assert "1.8 ng/mL" not in resp["answer"]
                assert resp["evidence_limitations"] is not None
                assert "numeric contradiction" in resp["evidence_limitations"].lower() or "lab contradiction" in resp["evidence_limitations"].lower()

@pytest.mark.asyncio
async def test_date_contradiction_rejected():
    mock_evidence = [{"id": "EV-1", "type": "document_chunk", "title": "IVF Cycle 1", "snippet": "IVF Cycle 1 started May 1, 2026."}]
    fake_output = '{"answer": "IVF Cycle 1 started in May 2026 [EV-1].\\nIVF Cycle 1 started in February 2026 [EV-1].", "evidence_citations": ["EV-1"]}'
    
    with patch("app.core.config.settings.GEMINI_API_KEY", "real-gemini-key"):
        with patch("app.retrieval.llm_service.LLMService.is_configured", return_value=True):
            with patch("app.retrieval.llm_service.LLMService.call_gemini", return_value=fake_output):
                resp, _ = await LLMService.generate_grounded_response("Query", mock_evidence)
                assert "May 2026" in resp["answer"]
                assert "February" not in resp["answer"]
                assert "date contradiction" in resp["evidence_limitations"].lower()

@pytest.mark.asyncio
async def test_negation_contradiction_rejected():
    mock_evidence = [{"id": "EV-1", "type": "document_chunk", "title": "Initial Consultation", "snippet": "Clinical History: No prior pelvic surgeries reported."}]
    fake_output = '{"answer": "Patient denies prior pelvic surgeries [EV-1].\\nPatient has a history of prior pelvic surgeries [EV-1].", "evidence_citations": ["EV-1"]}'
    
    with patch("app.core.config.settings.GEMINI_API_KEY", "real-gemini-key"):
        with patch("app.retrieval.llm_service.LLMService.is_configured", return_value=True):
            with patch("app.retrieval.llm_service.LLMService.call_gemini", return_value=fake_output):
                resp, _ = await LLMService.generate_grounded_response("Query", mock_evidence)
                assert "denies prior pelvic surgeries" in resp["answer"]
                assert "has a history of prior pelvic surgeries" not in resp["answer"]
                assert "negation contradiction" in resp["evidence_limitations"].lower()

@pytest.mark.asyncio
async def test_historical_medication_misframing_rejected():
    mock_evidence = [{"id": "EV-1", "type": "document_chunk", "title": "Prescription - IVF 1", "snippet": "Medication Orders for IVF Stimulation Protocol 1: Gonal-F 150 IU daily."}]
    fake_output = '{"answer": "Gonal-F 150 IU was ordered for IVF Stimulation Protocol 1 [EV-1].\\nPatient is currently taking Gonal-F 150 IU as an active daily prescription [EV-1].", "evidence_citations": ["EV-1"]}'
    
    with patch("app.core.config.settings.GEMINI_API_KEY", "real-gemini-key"):
        with patch("app.retrieval.llm_service.LLMService.is_configured", return_value=True):
            with patch("app.retrieval.llm_service.LLMService.call_gemini", return_value=fake_output):
                resp, _ = await LLMService.generate_grounded_response("Query", mock_evidence)
                assert "ordered for IVF Stimulation Protocol 1" in resp["answer"]
                assert "currently taking" not in resp["answer"]
                assert resp["evidence_limitations"] is not None
                assert "currently" in resp["evidence_limitations"].lower() or "medication" in resp["evidence_limitations"].lower()

@pytest.mark.asyncio
async def test_multilingual_tamil_query_normalization():
    tamil_query = "Sophia-வின் கடைசி இரண்டு சுழற்சிகள் மற்றும் நிலுவையில் உள்ள அறிக்கைகள் என்ன?"
    normalized = await LLMService.normalize_query_to_english(tamil_query)
    assert "cycles" in normalized.lower() or "pending" in normalized.lower() or "reports" in normalized.lower()

@pytest.mark.asyncio
async def test_multilingual_tamil_answer_generation():
    app.dependency_overrides[verify_supabase_token] = lambda: STAFF_BOB
    try:
        mock_evidence = [
            {"id": "EV-1", "type": "fertility_cycle", "title": "IVF Cycle 1", "date": "2026-05-01", "snippet": "Oocytes retrieved: 10"},
            {"id": "EV-2", "type": "pending_order", "title": "Karyotype Panel", "date": "2026-09-15", "snippet": "Result not yet recorded."}
        ]
        with patch("app.retrieval.retrieval_service.RetrievalService.gather_patient_context", return_value=(mock_evidence, "Context...")):
            with patch("app.retrieval.llm_service.LLMService.is_configured", return_value=False):
                transport = ASGITransport(app=app)
                async with AsyncClient(transport=transport, base_url="http://testserver") as client:
                    res = await client.post(
                        f"/api/v1/patients/{SOPHIA_ID}/ai/query",
                        json={
                            "query": "கடைசி இரண்டு சுழற்சிகள் மற்றும் நிலுவை அறிக்கைகள்?",
                            "input_language": "ta",
                            "answer_language": "ta"
                        },
                        headers={"Authorization": "Bearer mock-token"}
                    )
                    assert res.status_code == 200
                    data = res.json()
                    assert "EV-1" in data["evidence_citations"] or "EV-2" in data["evidence_citations"]
                    assert data["status"] == "ai_not_configured"
    finally:
        app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_gemini_failure_triggers_groq_fallback():
    mock_evidence = [{"id": "EV-1", "type": "document_chunk", "title": "Consultation", "snippet": "Patient age 43."}]
    groq_output = '{"answer": "Answer from Groq fallback [EV-1]", "evidence_citations": ["EV-1"]}'

    with patch("app.core.config.settings.GEMINI_API_KEY", "real-gemini-key"):
        with patch("app.core.config.settings.GROQ_API_KEY", "real-groq-key"):
            with patch("app.retrieval.llm_service.LLMService.call_gemini", side_effect=RuntimeError("503 Service Unavailable")):
                with patch("app.retrieval.llm_service.LLMService.call_groq", return_value=groq_output):
                    resp, provider = await LLMService.generate_grounded_response("Query", mock_evidence)
                    assert "Groq" in provider
                    assert "Answer from Groq fallback" in resp["answer"]


@pytest.mark.asyncio
async def test_successful_provider_response_with_not_found_text_not_classified_as_404():
    """Verify HTTP 200 responses containing 'not found' in body are NOT classified as AIModelUnavailableException 404."""
    mock_http_res = Response(200, json={
        "candidates": [{
            "content": {"parts": [{"text": '{"answer": "Information not found in the available patient records.", "evidence_citations": []}'}]}
        }]
    })

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_http_res
        text = await LLMService.call_gemini("Test prompt", "System instruction")
        assert "not found" in text.lower()
        assert "evidence_citations" in text


@pytest.mark.asyncio
async def test_valid_not_found_response_with_empty_citations():
    """Verify that a valid 'not found' response returns status success with empty citations, without erroring."""
    app.dependency_overrides[verify_supabase_token] = lambda: STAFF_BOB
    try:
        mock_evidence = [
            {"id": "EV-1", "type": "fertility_cycle", "title": "IVF Cycle 1", "date": "2026-05-01", "snippet": "Oocytes: 10"}
        ]
        
        with patch("app.retrieval.retrieval_service.RetrievalService.gather_patient_context", return_value=(mock_evidence, "Context...")):
            with patch("app.retrieval.llm_service.LLMService.is_configured", return_value=True):
                with patch("app.retrieval.llm_service.LLMService.generate_grounded_response", return_value=({"answer": "Information not found in the available patient records regarding cardiac MRI.", "evidence_citations": [], "evidence_limitations": None}, "Gemini 2.5 Flash")):
                    transport = ASGITransport(app=app)
                    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
                        res = await client.post(
                            f"/api/v1/patients/{SOPHIA_ID}/ai/query",
                            json={"query": "What are her cardiac MRI results?"},
                            headers={"Authorization": "Bearer mock-token"}
                        )
                        assert res.status_code == 200
                        data = res.json()
                        assert data["status"] == "success"
                        assert data["evidence_citations"] == []
                        assert "not found" in data["answer"].lower()
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_malformed_output_handled_separately_from_unavailable_model():
    """Verify malformed non-JSON output from provider does not raise 404 AIModelUnavailableException."""
    mock_evidence = [{"id": "EV-1", "type": "document_chunk", "title": "Consultation", "snippet": "Patient age 43."}]
    malformed_raw_output = "I cannot parse this into JSON format directly standard response text."

    with patch("app.core.config.settings.GEMINI_API_KEY", "real-gemini-key"):
        with patch("app.retrieval.llm_service.LLMService.is_configured", return_value=True):
            with patch("app.retrieval.llm_service.LLMService.call_gemini", return_value=malformed_raw_output):
                resp, provider = await LLMService.generate_grounded_response("Query", mock_evidence)
                assert "answer" in resp
                assert isinstance(resp["evidence_citations"], list)


@pytest.mark.asyncio
async def test_no_raw_provider_output_or_reasoning_exposed():
    """Verify that response output never exposes raw API dumps or reasoning fields to user payload."""
    app.dependency_overrides[verify_supabase_token] = lambda: STAFF_BOB
    try:
        mock_evidence = [{"id": "EV-1", "type": "fertility_cycle", "title": "IVF Cycle 1", "date": "2026-05-01", "snippet": "Oocytes: 10"}]
        raw_output_with_internal_thinking = 'THINKING: Let me search patient notes... RESULT: {"answer": "Patient had 10 oocytes retrieved [EV-1].", "evidence_citations": ["EV-1"]}'
        
        with patch("app.retrieval.retrieval_service.RetrievalService.gather_patient_context", return_value=(mock_evidence, "Context...")):
            with patch("app.retrieval.llm_service.LLMService.is_configured", return_value=True):
                with patch("app.retrieval.llm_service.LLMService.call_gemini", return_value=raw_output_with_internal_thinking):
                    transport = ASGITransport(app=app)
                    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
                        res = await client.post(
                            f"/api/v1/patients/{SOPHIA_ID}/ai/query",
                            json={"query": "How many oocytes?"},
                            headers={"Authorization": "Bearer mock-token"}
                        )
                        assert res.status_code == 200
                        data = res.json()
                        assert "THINKING:" not in data["answer"]
                        assert "candidates" not in data
                        assert "prompt" not in data
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_speech_transcription_endpoint():
    """Verify POST /api/v1/speech/transcribe converts uploaded audio file to transcript and returns detected language."""
    app.dependency_overrides[verify_supabase_token] = lambda: STAFF_BOB
    try:
        with patch("app.retrieval.llm_service.LLMService.transcribe_audio", return_value=("What were her last two cycles?", "en")):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://testserver") as client:
                files = {"file": ("test.webm", b"dummy audio content byte padding " * 10, "audio/webm")}
                res = await client.post(
                    "/api/v1/speech/transcribe",
                    files=files,
                    headers={"Authorization": "Bearer mock-token"}
                )
                assert res.status_code == 200
                data = res.json()
                assert data["status"] == "success"
                assert data["transcript"] == "What were her last two cycles?"
                assert data["detected_language"] == "en"
    finally:
        app.dependency_overrides.clear()


