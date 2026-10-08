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

- [x] **Milestone 1: Complete Folder Architecture & Runnable Health Connection** *(Current)*
  - End-to-end folder scaffolding, Pydantic & TS schemas, explicit CORS, FastAPI `/health` route, setup screen, Dockerfile, tests, and documentation.
- [ ] **Milestone 2: Supabase Authentication, Patient Grants & Directory**
  - Auth client, role checks, RLS policies, patient directory list.
- [ ] **Milestone 3: Private Uploads, PDF Extraction & Ingestion**
  - Signed PDF uploads to Supabase Storage, `pdfplumber` text & bounding box extraction.
- [ ] **Milestone 4: Embeddings, Retrieval, Gemini Answers & Citations**
  - Sentence Transformers embedding pipeline, `pgvector` similarity search, Gemini completion adapter with exact page citations.
- [ ] **Milestone 5: Connected Timeline, Brief & PDF Evidence Viewer**
  - Dynamic patient timeline visualizer, case brief banner, embedded PDF.js page bounding box highlighter.
- [ ] **Milestone 6: Cycle Comparison, Test/Result Matching & New-Report Updates**
  - Cross-report lab matching, treatment cycle comparison table, automated delta detection on upload.
- [ ] **Milestone 7: Groq Fallback, Verification & Demo Preparation**
  - Provider failover to Groq SDK, end-to-end Playwright tests, synthetic demo dataset validation.
