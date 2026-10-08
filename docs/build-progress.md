# CareLens AI Milestone 2 Build Progress & Verification Log

**Date:** October 9, 2026  
**Developer:** Varun Yadav T  
**Local Workspace:** `D:\carelens-ai project`  
**GitHub Repository:** `https://github.com/tvarunyadav/carelens-ai-project.git`  
**Current Feature Branch:** `feature/auth-patients`

---

## 1. Implemented Capabilities (Milestone 2)

- [x] **Database Migration & Security Schema**:
  - Auth-linked staff profile table (`public.staff_profiles`) with constrained `doctor`, `coordinator`, and `admin` roles.
  - Synthetic patients table (`public.patients`) with UUID primary keys, MRN uniqueness, and `record_version` counter.
  - Patient access grants table (`public.patient_access_grants`) enforcing patient-level isolation (`UNIQUE(staff_id, patient_id, action)`).
  - Telemetry audit events table (`public.audit_events`) excluding secret logging.
  - Row Level Security (RLS) policies configured on all tables. Ordinary users cannot modify their own roles or assign arbitrary grants. Admin role alone does NOT grant clinical access to every patient without explicit grants.
- [x] **Backend Bearer Token Verification & Authorization Endpoints**:
  - Official Supabase access token verification (`app/auth/verifier.py`) rejecting missing, invalid, or expired tokens (HTTP 401).
  - Implemented `GET /api/v1/me` returning verified staff profile.
  - Implemented `GET /api/v1/patients` returning only patients for which the authenticated user holds an explicit access grant.
  - Implemented `GET /api/v1/patients/{patient_id}` with pre-authorization check returning `403 Forbidden` for unauthorized patient records.
- [x] **Frontend Supabase Auth & Patient Directory Integration**:
  - `@supabase/supabase-js` SDK initialized in `frontend/src/lib/supabase.ts`.
  - Auth context provider (`AuthProvider` & `useAuth`) managing session state, Supabase login, token storage, and logout state clearing.
  - Medical-themed `LoginPage` with live Supabase authentication and dev test account switcher.
  - Interactive `PatientsPage` displaying authorized synthetic patient records, search filtering, and detail modal inspection.
  - Tab navigation between Patient Directory and Milestone 1 Setup / Health Verifier.
- [x] **Documentation & Setup**:
  - Created [`docs/milestone-2-setup.md`](./milestone-2-setup.md) detailing Supabase migration execution, staff user creation, patient grant assignment, and environment variable configuration.
  - Updated [`docs/api-contracts.md`](./api-contracts.md) with `/api/v1/me`, `/api/v1/patients`, and `/api/v1/patients/{patient_id}` specifications.

---

## 2. Empirical Verification Results

### A. Backend Pytest Suite (Auth & Patient Isolation)
- **Command:** `.\venv\Scripts\pytest -v` (in `backend/`)
- **Result:** **PASSED (Exit Code: 0)**
- **Output:**
  ```text
  collected 9 items
  tests/test_auth_patients.py::test_health_endpoint PASSED [ 11%]
  tests/test_auth_patients.py::test_me_endpoint_missing_token PASSED [ 22%]
  tests/test_auth_patients.py::test_me_endpoint_invalid_token PASSED [ 33%]
  tests/test_auth_patients.py::test_me_endpoint_valid_token PASSED [ 44%]
  tests/test_auth_patients.py::test_patients_isolation_dr_alice PASSED [ 55%]
  tests/test_auth_patients.py::test_patients_isolation_bob_coordinator PASSED [ 66%]
  tests/test_auth_patients.py::test_admin_without_explicit_grant_has_zero_clinical_patients PASSED [ 77%]
  tests/test_auth_patients.py::test_patient_detail_authorized_vs_unauthorized PASSED [ 88%]
  tests/test_health.py::test_health_check_endpoint PASSED [100%]
  ======================= 9 passed in 8.44s =======================
  ```

### B. Frontend TypeScript & Production Build Verification
- **Command:** `npm run build` (in `frontend/`)
- **Result:** **PASSED (Exit Code: 0)**
- **Output:**
  ```text
  vite v8.3.4 building client environment for production...
  ✓ 1955 modules transformed.
  dist/index.html                   0.45 kB │ gzip:   0.29 kB
  dist/assets/index-BcDAGczn.css   20.99 kB │ gzip:   4.80 kB
  dist/assets/index-oZn6oQUf.js   503.66 kB │ gzip: 142.67 kB
  ✓ built in 32.34s
  ```

---

## 3. Planned vs. Implemented Separation (Deferrals)

The following capabilities remain explicitly **deferred** to future milestones:
- PDF document storage & signed URL upload (Deferred to Milestone 3).
- `pdfplumber` page extraction & text chunking (Deferred to Milestone 3).
- Sentence Transformers embedding generation & `pgvector` similarity search (Deferred to Milestone 4).
- Gemini & Groq LLM completion adapters (Deferred to Milestone 4 & 7).
- Dynamic clinical history timeline visualizer & PDF.js evidence viewer (Deferred to Milestone 5).
- Treatment cycle comparison & reconciliation diffing (Deferred to Milestone 6).

---

## 4. Remaining Live Configuration Items

To connect the application to a live external Supabase project:
1. Run [`database/migrations/001_milestone2_auth_patients.sql`](../database/migrations/001_milestone2_auth_patients.sql) in the Supabase SQL Editor.
2. Run [`database/seeds/001_demo_seeds.sql`](../database/seeds/001_demo_seeds.sql) in the Supabase SQL Editor.
3. Configure `backend/.env` with your `SUPABASE_URL`, `SUPABASE_ANON_KEY`, and `SUPABASE_JWT_SECRET`.
4. Configure `frontend/.env` with your `VITE_SUPABASE_URL` and `VITE_SUPABASE_ANON_KEY`.

---

## 5. Next Steps for Milestone 3

- **Private Document Uploads & Storage:** Create private PDF bucket in Supabase Storage and build signed upload URL endpoints.
- **PDF Extraction Engine:** Integrate `pdfplumber` to extract page text, page numbers, and bounding box coordinates for fact provenance.
