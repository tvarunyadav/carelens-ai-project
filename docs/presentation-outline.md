# CareLens AI - Executive Presentation & Architecture Outline

## 1. Problem Statement & Mission
- **Target Problem**: Problem 2 — Patient History Retrieval & EHR Insight Engine.
- **Goal**: Enable healthcare staff to instantly query patient history across multiple visits, labs, procedures, and medication records with zero hallucinated facts, strict source citations, and robust privacy controls.

---

## 2. Core Architecture & System Components

```
+-----------------------------------------------------------------------------------+
|                                 CareLens AI System                                |
+-----------------------------------------------------------------------------------+
|  Frontend: React + Vite + TypeScript (Navy/Teal Clinical Theme, Speech Synthesis) |
|  Backend:  FastAPI + Uvicorn + Pydantic (Async HTTP Client, FastEmbed ONNX RAG)  |
|  Database: Supabase PostgreSQL + pgvector (384-dim BAAI/bge-small-en-v1.5 RAG)     |
|  Security: Supabase Auth JWT + Row Level Security (RLS) + Private Storage        |
+-----------------------------------------------------------------------------------+
```

### Key Technical Pillars:
1. **Deterministic Grounding**: Every factual claim is backed by semantic chunks indexed in `patient_document_chunks`.
2. **Strict RLS Access Boundary**: Staff permissions (`read`, `write`, `admin`) enforced at database and API layers.
3. **Multilingual Voice Capabilities**: Web Speech API for Tamil & English transcription with zero third-party telemetry.
4. **Immutable Audit Persistence**: Cryptographically verified audit logging (`audit_events`).

---

## 3. Grounded RAG Pipeline & Semantic Search
- **Embedding Model**: `BAAI/bge-small-en-v1.5` (384 dimensions).
- **Vector Storage**: Supabase `pgvector` with cosine similarity (`match_patient_document_chunks` RPC).
- **Citation Precision**: Citations map directly to exact document ID, version number, and page number.
