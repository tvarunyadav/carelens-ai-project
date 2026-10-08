# CareLens AI Shared API Contracts

All contracts are defined as Pydantic models in `backend/app/schemas/models.py` and mirrored as TypeScript interfaces in `frontend/src/types/index.ts`.

## 1. HealthStatus Contract (`GET /health`)

```json
{
  "status": "ok",
  "service": "CareLens AI",
  "version": "0.1.0",
  "timestamp": "2026-10-09T00:15:00Z"
}
```

## 2. Patient Schema

```json
{
  "id": "pat_9f8a7b6c-5d4e-3f2a-1b0c-9d8e7f6a5b4c",
  "mrn": "MRN-884920",
  "first_name": "Eleanor",
  "last_name": "Vane",
  "dob": "1968-04-12",
  "gender": "Female",
  "status": "active",
  "created_at": "2026-10-09T00:00:00Z"
}
```

## 3. Question Schema

```json
{
  "id": "q_12345678-aaaa-bbbb-cccc-ddddeeeeffff",
  "patient_id": "pat_9f8a7b6c-5d4e-3f2a-1b0c-9d8e7f6a5b4c",
  "text": "What was the patient's latest HbA1c measurement and when was it taken?",
  "asked_by": "staff_dr_smith@clinic.org",
  "created_at": "2026-10-09T00:10:00Z"
}
```

## 4. Citation Schema

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

## 5. Claim Schema

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

## 6. TimelineEvent Schema

```json
{
  "id": "evt_99887766-5544-3322-1100-aabbccddeeff",
  "patient_id": "pat_9f8a7b6c-5d4e-3f2a-1b0c-9d8e7f6a5b4c",
  "event_date": "2025-09-14",
  "category": "Lab Result",
  "summary": "HbA1c tested at 6.8%",
  "document_id": "doc_lab_results_2025_09.pdf"
}
```
