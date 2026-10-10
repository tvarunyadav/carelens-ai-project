# CareLens AI Milestone 4 Setup Guide

**Grounded Patient History Assistant & Vector Retrieval (RAG)**

- **Developer:** Varun Yadav T
- **Repository:** `https://github.com/tvarunyadav/carelens-ai-project.git`
- **Target Branch:** `feature/auth-patients`

---

## 1. Environment Variable Configuration

Add the following keys to `backend/.env`:

```ini
# AI LLM Provider Configuration (Milestone 4)
GEMINI_API_KEY=your-gemini-api-key
GROQ_API_KEY=your-groq-api-key
PRIMARY_LLM_MODEL=gemini-2.5-flash
FALLBACK_LLM_MODEL=llama-3.3-70b-versatile
```

---

## 2. Database Migration & Vector Indexing Order

Execute in your [Supabase Dashboard](https://supabase.com/dashboard) SQL Editor:

### Step 1: Run pgvector Migration
- File: [`database/migrations/004_patient_vector_search.sql`](../database/migrations/004_patient_vector_search.sql)
- Description: Enables `pgvector` extension, creates `public.patient_document_chunks` table, configures RLS policies, HNSW vector distance indexes, and creates `match_patient_document_chunks` RPC function with `SECURITY INVOKER` and explicit patient isolation.

### Step 2: Index Patient Document Chunks
Run the repeatable Python indexing script from `backend/`:

```powershell
cd backend
.\venv\Scripts\python.exe scripts/index_patient_chunks.py
```
**Output:** Scans synthetic PDF documents, extracts per-page text using `pdfplumber`, creates page-level text chunks, computes 384-dimensional embeddings, and upserts chunks idempotently to `public.patient_document_chunks`.

---

## 3. Verification Commands Matrix

### A. Backend Pytest Suite
```powershell
cd backend
.\venv\Scripts\python.exe -m pytest tests/ -v
```
**Output:** `27 passed, 1 skipped`. Verifies RAG retrieval, page-level provenance, pending orders handling, citation validation, Gemini primary + Groq fallback, and unauthorized patient AI isolation.

### B. Frontend Production Build
```powershell
cd frontend
npm run build
```
**Output:** Generates clean Vite production assets in `dist/`.
