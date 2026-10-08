# CareLens AI Milestone 2 Setup Guide

**Supabase Authentication, Patient Grants & Directory**

- **Developer:** Varun Yadav T
- **Repository:** `https://github.com/tvarunyadav/carelens-ai-project.git`
- **Target Branch:** `feature/auth-patients`

---

## 1. Supabase Dashboard & Database Migration Steps

### Step A: Database Schema Migration
1. Log into your [Supabase Dashboard](https://supabase.com/dashboard) and navigate to your project.
2. Go to the **SQL Editor** from the left navigation menu.
3. Open [`database/migrations/001_milestone2_auth_patients.sql`](../database/migrations/001_milestone2_auth_patients.sql) from the repository.
4. Copy and paste the entire SQL content into the SQL Editor and click **Run**.
   - This creates `public.staff_profiles`, `public.patients`, `public.patient_access_grants`, `public.audit_events`, and configures Row Level Security (RLS) policies.

### Step B: Seed Synthetic Patients
1. In the **SQL Editor**, open [`database/seeds/001_demo_seeds.sql`](../database/seeds/001_demo_seeds.sql).
2. Copy and run the SQL query to insert synthetic patient records:
   - Eleanor Vane (`MRN-884920`)
   - Marcus Chen (`MRN-993041`)
   - Sophia Patel (`MRN-441029`)

---

## 2. Creating Test Staff Accounts & Patient Grants

### Step A: Create Staff Accounts in Supabase Auth
Go to **Authentication -> Users** in your Supabase Dashboard and click **Add User -> Create User** for two test staff members:

1. **Dr. Alice Morgan** (Doctor):
   - **Email:** `dr.alice@clinic.org`
   - **Password:** `ClinicPass2026!`
   - *(Note down the generated User UUID, e.g. `ALICE_UUID`)*

2. **Bob Vance** (Coordinator):
   - **Email:** `coord.bob@clinic.org`
   - **Password:** `ClinicPass2026!`
   - *(Note down the generated User UUID, e.g. `BOB_UUID`)*

### Step B: Link Staff Profiles and Assign Explicit Patient Access Grants
In the Supabase SQL Editor, run the following query (replace `<ALICE_UUID>` and `<BOB_UUID>` with your actual Supabase Auth UUIDs):

```sql
-- 1. Insert Staff Profiles
INSERT INTO public.staff_profiles (id, email, full_name, role) VALUES
    ('<ALICE_UUID>', 'dr.alice@clinic.org', 'Dr. Alice Morgan', 'doctor'),
    ('<BOB_UUID>', 'coord.bob@clinic.org', 'Bob Vance', 'coordinator');

-- 2. Grant Dr. Alice access to Eleanor Vane & Marcus Chen
INSERT INTO public.patient_access_grants (staff_id, patient_id, action) VALUES
    ('<ALICE_UUID>', '11111111-1111-1111-1111-111111111111', 'read'),
    ('<ALICE_UUID>', '22222222-2222-2222-2222-222222222222', 'read');

-- 3. Grant Bob access to Sophia Patel ONLY
INSERT INTO public.patient_access_grants (staff_id, patient_id, action) VALUES
    ('<BOB_UUID>', '33333333-3333-3333-3333-333333333333', 'read');
```

---

## 3. Environment Variables Configuration

Copy `.env.example` templates to `.env` in both `backend` and `frontend` directories:

### Backend (`backend/.env`):
```ini
APP_ENV=development
APP_NAME="CareLens AI"
API_VERSION=0.1.0
DEBUG=True

HOST=127.0.0.1
PORT=8000
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173

# Supabase Real Credentials (Found in Supabase Settings -> API & JWT)
SUPABASE_URL=https://<your-project-ref>.supabase.co
SUPABASE_ANON_KEY=<your-anon-key>
SUPABASE_SERVICE_ROLE_KEY=<your-service-role-key>
SUPABASE_JWT_SECRET=<your-jwt-secret>
```

### Frontend (`frontend/.env`):
```ini
VITE_API_BASE_URL=http://localhost:8000
VITE_APP_TITLE="CareLens AI - Synthetic Patient EHR Insight Engine"

# Supabase Auth Public Configuration
VITE_SUPABASE_URL=https://<your-project-ref>.supabase.co
VITE_SUPABASE_ANON_KEY=<your-anon-key>
```

---

## 4. Verification Commands & Expected Results

### A. Run Automated Backend Test Suite
```powershell
cd backend
.\venv\Scripts\Activate.ps1
pytest -v
```
**Expected Result:** `9 passed in ~8s` (verifies token validation, missing token 401, invalid token 401, Dr. Alice isolation, Bob Vance isolation, Admin isolation, and 403 Forbidden access control).

### B. Run Frontend Typecheck & Build Verification
```powershell
cd frontend
npm run build
```
**Expected Result:** Successful Vite build generating production assets in `dist/`.

### C. Live Interactive Verification
1. Start FastAPI Backend: `uvicorn app.main:app --reload --port 8000`
2. Start Frontend Dev Server: `npm run dev`
3. Navigate to `http://localhost:5173`
4. Login as **Dr. Alice Morgan**:
   - Patient Directory displays **2 permitted patients** (Eleanor Vane & Marcus Chen).
5. Fast-switch / Login as **Bob Vance**:
   - Patient Directory displays **1 permitted patient** (Sophia Patel only).
6. Fast-switch / Login as **Sam Admin**:
   - Patient Directory displays **0 clinical records**, demonstrating that Admin role alone does NOT grant clinical access without explicit grants.
