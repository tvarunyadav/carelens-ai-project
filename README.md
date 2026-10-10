# CareLens AI

**Synthetic Patient EHR Insight & Evidence Engine**

- **Developer:** Varun Yadav T
- **Local Directory:** `D:\carelens-ai project`
- **GitHub Repository:** [https://github.com/tvarunyadav/carelens-ai-project](https://github.com/tvarunyadav/carelens-ai-project)

---

## 🎯 Project Vision

CareLens AI empowers authorized clinic staff to navigate, query, and verify synthetic patient electronic health records (EHR). The platform transforms complex clinical documentation into structured patient timelines, cited factual answers, visual PDF evidence coordinates, treatment-cycle comparisons, and delta reports when new medical records arrive.

---

## 🛠️ Technology Stack

| Layer | Technologies |
| :--- | :--- |
| **Frontend** | React 19, Vite, TypeScript, Tailwind CSS, Lucide React, PDF.js |
| **Backend** | Python 3.11, FastAPI, Pydantic v2, `pydantic-settings`, Uvicorn |
| **Database** | Supabase PostgreSQL + `pgvector` (Milestone 2+) |
| **Authentication** | Supabase Auth + JWT Verification |
| **PDF Extraction** | `pdfplumber` (Backend page & bounding box parser) |
| **AI / Embeddings**| Local Sentence Transformers (`all-MiniLM-L6-v2`) |
| **LLMs** | Primary: Google Gemini via `google-genai` SDK • Fallback: Groq SDK |
| **Testing** | `pytest`, `HTTPX`, `Playwright` E2E |
| **Containerization**| Docker |

---

## 🏗️ Architecture & Module Structure

```
d:\carelens-ai project\
├── backend/                # Python FastAPI Application
│   ├── app/
│   │   ├── main.py         # FastAPI Entrypoint & CORS configuration
│   │   ├── core/           # Settings (pydantic-settings) & DB connections
│   │   ├── auth/           # JWT & Patient-level authorization checks
│   │   ├── api/            # API Route controllers
│   │   ├── schemas/        # Shared Pydantic data contracts
│   │   ├── patients/       # Patient directory, timeline & summary briefs
│   │   ├── documents/      # Private storage & upload coordination
│   │   ├── ingestion/      # PDF text, chunking & fact provenance
│   │   ├── retrieval/      # Patient-scoped vector search & citations
│   │   ├── providers/      # Gemini & Groq LLM adapters
│   │   ├── reconciliation/ # Test matching, cycle comparisons & deltas
│   │   └── audit/          # Access & telemetry logging (no secret logging)
│   ├── tests/              # Pytest & HTTPX async test suite
│   ├── .env.example        # Environment variables template
│   ├── Dockerfile          # Production backend Docker container
│   └── requirements.txt    # Python dependencies
├── frontend/               # React 19 + Vite + TypeScript Application
│   ├── src/
│   │   ├── pages/          # SetupPage & clinical dashboards
│   │   ├── components/     # UI components & HealthCheckCard
│   │   ├── services/       # Reusable API Client with timeouts & retry logic
│   │   ├── hooks/          # Custom state hooks (useHealthCheck)
│   │   └── types/          # TypeScript interfaces for API contracts
│   └── .env.example
├── database/               # SQL migrations & seeds (Milestone 2+)
├── demo-data/              # Synthetic patient PDFs & expected answers
└── docs/                   # System architecture, API contracts & build logs
```

---

## 🚀 Quickstart & Verification (Milestone 1)

### 1. Backend

```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```
Backend Readiness Endpoint: `http://127.0.0.1:8000/health`

### 2. Frontend

```powershell
cd frontend
npm install
npm run dev
```
Access Frontend Setup Screen: `http://localhost:5173`

---

## 🗺️ Development Milestones

- [x] **Milestone 1: Complete Folder Architecture & Runnable Health Connection**
- [x] **Milestone 2: Supabase Authentication, Patient Grants & Directory**
- [x] **Milestone 3: Private Uploads, PDF Extraction & Ingestion**
- [x] **Milestone 4: Embeddings, Retrieval, Gemini Answers & Citations**
- [x] **Milestone 5: Connected Timeline, Brief & PDF Evidence Viewer**
- [x] **Milestone 6: Secure Document Intake, OCR & Record Version History**
- [x] **Milestone 7: Problem 2 Prototype — Patient History Retrieval, 10 Synthetic Patients & Conflict Reconciliation**
  - **10 Synthetic Patients**: Canonical datasets covering demographics, consultations, fertility cycles, labs, procedures, and pending orders.
  - **Source Citation & Original PDF Viewer**: Opens original synthetic PDFs or uploaded documents from private storage with page provenance and `URL.revokeObjectURL` cleanup.
  - **Conflict & Reconciliation Review**: Surfaces discrepant clinical values with explicit staff resolution recording and immutable audit tracking.
  - **Multilingual Voice & Cross-Language Retrieval**: Web Speech API transcription for Tamil and English with grounded RAG retrieval (`BAAI/bge-small-en-v1.5`, 384 dimensions).

---

## 🗄️ Database Migrations

1. `001_initial_schema.sql`: Initial synthetic patients and staff tables.
2. `002_fix_staff_uuids.sql`: UUID alignment for authentication.
3. `003_patient_workspace_schema.sql`: Patient documents, document versions, timeline events, and fertility cycles tables.
4. `004_patient_vector_search.sql`: Vector chunks table and similarity search RPC functions.
5. `005_patient_vector_search_repair.sql`: Vector chunk foreign key repair and indexing updates.
6. `006_restricted_audit_policies.sql`: Audit event policies and restricted access logs.
7. `007_document_intake_versioning.sql`: Milestone 6 intake fields, review status, content hash indexes, and RLS write policies.
8. `008_atomic_versioning_and_fixes.sql`: Atomic version creation RPC (`create_atomic_document_version`) and version uniqueness constraint.
9. `009_conflict_reviews_and_activity_history.sql`: Clinical conflict resolution reviews table and RLS policies.

