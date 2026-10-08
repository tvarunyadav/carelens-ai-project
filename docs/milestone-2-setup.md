# CareLens AI Milestone 2 Setup Guide

**Supabase Authentication, Patient Grants & Directory**

- **Developer:** Varun Yadav T
- **Repository:** `https://github.com/tvarunyadav/carelens-ai-project.git`
- **Target Branch:** `feature/auth-patients`

---

## 1. Environment Variable Alignment

Both `.env.example` templates and setup guides consume these exact environment variable names:

### Backend Configuration (`backend/.env`):
```ini
APP_ENV=development
APP_NAME="CareLens AI"
API_VERSION=0.1.0
DEBUG=True

HOST=127.0.0.1
PORT=8000
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173

# Supabase Authentication & PostgreSQL Configuration
SUPABASE_URL=https://<your-project-ref>.supabase.co
SUPABASE_ANON_KEY=<your-anon-key>
SUPABASE_SERVICE_ROLE_KEY=<your-service-role-key>
SUPABASE_JWT_SECRET=<your-jwt-secret>
```

### Frontend Configuration (`frontend/.env`):
```ini
VITE_API_BASE_URL=http://localhost:8000
VITE_APP_TITLE="CareLens AI - Synthetic Patient EHR Insight Engine"

# Supabase Auth Public Configuration
VITE_SUPABASE_URL=https://<your-project-ref>.supabase.co
VITE_SUPABASE_ANON_KEY=<your-anon-key>
```

---

## 2. Database Migration & Setup Order

Follow this exact sequence in your [Supabase Dashboard](https://supabase.com/dashboard) SQL Editor:

### Step 1: Run Initial Schema Migration
- File: [`database/migrations/001_initial_schema.sql`](../database/migrations/001_initial_schema.sql)
- Description: Creates `public.staff_profiles`, `public.patients`, `public.patient_access_grants`, `public.audit_events`, and configures Row Level Security (RLS) policies.

### Step 2: Seed Synthetic Patients
- File: [`database/seeds/001_synthetic_patients.sql`](../database/seeds/001_synthetic_patients.sql)
- Description: Populates synthetic non-PHI patient records (`Eleanor Vane`, `Marcus Chen`, `Sophia Patel`). This file has no dependencies on Auth users.

### Step 3: Create Staff Accounts in Supabase Auth
In Supabase Dashboard -> **Authentication -> Users**, click **Add User -> Create User**:

1. **Dr. Alice Morgan**
   - **Email:** `dr.alice@clinic.org`
   - **Password:** *(Your strong password)*
   - *Copy User UUID (e.g. `ALICE_UUID`)*

2. **Bob Vance**
   - **Email:** `coord.bob@clinic.org`
   - **Password:** *(Your strong password)*
   - *Copy User UUID (e.g. `BOB_UUID`)*

### Step 4: Assign Staff Profiles & Patient Grants
- File: [`database/seeds/002_staff_grants_template.sql`](../database/seeds/002_staff_grants_template.sql)
- Replace `<STAFF_UUID_ALICE>` and `<STAFF_UUID_BOB>` with the actual Auth user UUIDs from Step 3 and execute in SQL Editor:

```sql
INSERT INTO public.staff_profiles (id, email, full_name, role) VALUES
    ('<ALICE_UUID>', 'dr.alice@clinic.org', 'Dr. Alice Morgan', 'doctor'),
    ('<BOB_UUID>', 'coord.bob@clinic.org', 'Bob Vance', 'coordinator');

-- Grant Dr. Alice access to Eleanor Vane & Marcus Chen
INSERT INTO public.patient_access_grants (staff_id, patient_id, action) VALUES
    ('<ALICE_UUID>', '11111111-1111-1111-1111-111111111111', 'read'),
    ('<ALICE_UUID>', '22222222-2222-2222-2222-222222222222', 'read');

-- Grant Bob access to Sophia Patel ONLY
INSERT INTO public.patient_access_grants (staff_id, patient_id, action) VALUES
    ('<BOB_UUID>', '33333333-3333-3333-3333-333333333333', 'read');
```

---

## 3. Verification Commands Matrix

### A. Isolated Backend Unit Tests (Dependency Overrides)
```powershell
cd backend
.\venv\Scripts\Activate.ps1
pytest tests/test_auth_patients_unit.py -v
```
**Output:** `9 passed` (Exercises endpoint serialization, 401 unauthenticated errors, 403 forbidden access, and patient isolation logic).

### B. Live Supabase Integration Verification
```powershell
cd backend
$env:TEST_SUPABASE_ACCESS_TOKEN="<your-real-bearer-token>"
pytest tests/test_auth_patients_live.py -v
```
**Output:** Exercises live HTTP token validation against Supabase Auth API (`GET /auth/v1/user`).

### C. Frontend Production Build
```powershell
cd frontend
npm run build
```
**Output:** Generates clean Vite production assets in `dist/`.
