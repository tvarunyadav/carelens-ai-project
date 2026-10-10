# CareLens AI Shared API Contracts

All contracts are defined as Pydantic models in `backend/app/schemas/models.py` and mirrored as TypeScript interfaces in `frontend/src/types/index.ts`.

---

## 1. HealthStatus Contract (`GET /health`)

```json
{
  "status": "ok",
  "service": "CareLens AI",
  "version": "0.1.0",
  "timestamp": "2026-10-09T00:15:00Z"
}
```

---

## 2. StaffProfile Contract (`GET /api/v1/me`)

Requires `Authorization: Bearer <token>` header. Rejects missing/invalid token with `401 Unauthorized`.

```json
{
  "id": "7b7c7b68-8c02-4081-a5a3-18b6cdcb26f7",
  "email": "coord.bob@clinic.org",
  "full_name": "Bob Vance",
  "role": "coordinator"
}
```

---

## 3. Patient List Contract (`GET /api/v1/patients`)

Requires `Authorization: Bearer <token>` header. Returns ONLY patients for which the authenticated user holds an explicit access grant.

```json
{
  "patients": [
    {
      "id": "33333333-3333-3333-3333-333333333333",
      "mrn": "MRN-441029",
      "first_name": "Sophia",
      "last_name": "Patel",
      "dob": "1982-11-05",
      "gender": "Female",
      "status": "active",
      "record_version": 1
    }
  ],
  "total": 1
}
```

---

## 4. History Assistant Summary (`POST /api/v1/patients/{patient_id}/ai/summary`)

Requires `Authorization: Bearer <token>`. Generates grounded history summary.

```json
{
  "status": "success",
  "answer": "Sophia Patel is a 43-year-old female undergoing IVF treatment. [EV-1]",
  "provider": "Gemini (gemini-2.5-flash)",
  "evidence": [
    {
      "id": "EV-1",
      "type": "document_chunk",
      "title": "Initial Reproductive Endocrinology Consultation",
      "document_id": "31111111-1111-1111-1111-111111111111",
      "page_number": 1,
      "date": "2026-04-15",
      "snippet": "Initial Reproductive Endocrinology Consultation..."
    }
  ],
  "evidence_citations": ["EV-1"],
  "evidence_limitations": null
}
```

---

## 5. History Assistant Question Answering (`POST /api/v1/patients/{patient_id}/ai/query`)

Requires `Authorization: Bearer <token>`.

**Request Body:**
```json
{
  "query": "கடைசி இரண்டு சுழற்சிகள் மற்றும் நிலுவை அறிக்கைகள்?",
  "input_mode": "voice",
  "input_language": "ta",
  "answer_language": "en"
}
```

**Response Body:**
```json
{
  "status": "success",
  "answer": "Sophia Patel completed two IVF cycles: IVF Cycle 1 (May 1–28, 2026) and FET cycle (July 10–Sept 1, 2026). [EV-1] [EV-2] Additionally, Karyotype & Chromosomal Microarray Panel was requested on September 15, 2026 and remains pending. [EV-3]",
  "provider": "Gemini (gemini-2.5-flash)",
  "evidence": [
    {
      "id": "EV-1",
      "type": "fertility_cycle",
      "title": "IVF Cycle 1 - Antagonist Ovulation Induction",
      "date": "2026-05-01",
      "snippet": "Status: completed, Metrics: {'oocytes_retrieved': 10, 'mature': 8, 'blastocysts_frozen': 4}"
    }
  ],
  "evidence_citations": ["EV-1", "EV-2", "EV-3"],
  "evidence_limitations": null
}
```

