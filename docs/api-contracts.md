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
  "id": "11111111-aaaa-1111-aaaa-111111111111",
  "email": "dr.alice@clinic.org",
  "full_name": "Dr. Alice Morgan",
  "role": "doctor"
}
```

---

## 3. Patient List Contract (`GET /api/v1/patients`)

Requires `Authorization: Bearer <token>` header. Returns ONLY patients for which the authenticated user holds an explicit access grant.

```json
{
  "patients": [
    {
      "id": "11111111-1111-1111-1111-111111111111",
      "mrn": "MRN-884920",
      "first_name": "Eleanor",
      "last_name": "Vane",
      "dob": "1968-04-12",
      "gender": "Female",
      "status": "active",
      "record_version": 1,
      "created_at": "2026-10-09T00:00:00Z"
    },
    {
      "id": "22222222-2222-2222-2222-222222222222",
      "mrn": "MRN-993041",
      "first_name": "Marcus",
      "last_name": "Chen",
      "dob": "1975-09-28",
      "gender": "Male",
      "status": "active",
      "record_version": 1,
      "created_at": "2026-10-09T00:00:00Z"
    }
  ],
  "total": 2
}
```

---

## 4. Patient Detail Contract (`GET /api/v1/patients/{patient_id}`)

Requires `Authorization: Bearer <token>` header. Authorizes detail access BEFORE returning patient data. Returns `403 Forbidden` if unauthorized.

```json
{
  "id": "11111111-1111-1111-1111-111111111111",
  "mrn": "MRN-884920",
  "first_name": "Eleanor",
  "last_name": "Vane",
  "dob": "1968-04-12",
  "gender": "Female",
  "status": "active",
  "record_version": 1,
  "created_at": "2026-10-09T00:00:00Z"
}
```

---

## 5. Question Schema (Milestone 4+)

```json
{
  "id": "q_12345678-aaaa-bbbb-cccc-ddddeeeeffff",
  "patient_id": "11111111-1111-1111-1111-111111111111",
  "text": "What was the patient's latest HbA1c measurement and when was it taken?",
  "asked_by": "dr.alice@clinic.org",
  "created_at": "2026-10-09T00:10:00Z"
}
```

---

## 6. Citation Schema (Milestone 4+)

```json
{
  "id": "cit_001",
  "document_id": "doc_lab_results_2025_09.pdf",
  "document_name": "Metabolic Panel & HbA1c Report.pdf",
  "page_number": 2,
  "text_snippet": "HbA1c: 6.8% (Reference Range: < 5.7%). Date of specimen collection: Sep 14, 2025.",
  "bounding_box": {
    "x_min": 72.0,
    "y_min": 140.5,
    "x_max": 540.0,
    "y_max": 185.2
  }
}
```

---

## 7. Claim Schema (Milestone 4+)

```json
{
  "id": "clm_550e8400-e29b-41d4-a716-446655440000",
  "text": "The patient's most recent HbA1c level was 6.8% on September 14, 2025, indicating diabetic range glycemic control.",
  "confidence": 0.96,
  "citations": [
    {
      "id": "cit_001",
      "document_id": "doc_lab_results_2025_09.pdf",
      "document_name": "Metabolic Panel & HbA1c Report.pdf",
      "page_number": 2,
      "text_snippet": "HbA1c: 6.8% (Reference Range: < 5.7%). Date of specimen collection: Sep 14, 2025.",
      "bounding_box": {
        "x_min": 72.0,
        "y_min": 140.5,
        "x_max": 540.0,
        "y_max": 185.2
      }
    }
  ]
}
```

---

## 8. TimelineEvent Schema (Milestone 5+)

```json
{
  "id": "evt_99887766-5544-3322-1100-aabbccddeeff",
  "patient_id": "11111111-1111-1111-1111-111111111111",
  "event_date": "2025-09-14",
  "category": "Lab Result",
  "summary": "HbA1c tested at 6.8%",
  "document_id": "doc_lab_results_2025_09.pdf"
}
```
