# CareLens AI - Staging Deployment & Operations Guide

This guide documents the architecture, free hosting comparison, security configuration, deployment procedures, and verification checklist for staging and production deployments of CareLens AI.

---

## 1. System Architecture & Hosting Analysis

### 1.1 Frontend (React 18 + Vite + TailwindCSS)
- **Recommended Free Hosting:** **Vercel** or **Netlify** / **Cloudflare Pages**
- **Characteristics:**
  - Fast global CDN distribution for static assets.
  - Automatic HTTPS certificate provisioning out-of-the-box.
  - Zero cold starts for static frontend JavaScript/CSS bundles.
  - Native environment variable support via `VITE_API_BASE_URL`.
  - Continuous deployment connected directly to GitHub repository branches (`staging` / `main`).

### 1.2 Backend (FastAPI + Python 3.11 + FastEmbed ONNX)
- **Recommended Free/Hobby Hosting:** **Render** (Docker / Python Web Service), **Railway**, **Koyeb**, or **Hugging Face Spaces** (Docker CPU Space)
- **Memory & Resource Footprint:**
  - **FastEmbed ONNX Model (`BAAI/bge-small-en-v1.5`):** ~120 MB model file size on disk; requires ~150–200 MB RAM during vector inference.
  - **Total Memory Usage:** ~280 MB RAM total under active inference load, fitting safely within 512 MB to 1 GB RAM container limits.
  - **Cold Starts:** Free container tiers (e.g. Render Free) spin down after 15 minutes of inactivity; initial cold start response takes ~5–8 seconds to initialize ONNX runtime buffers, after which request latency drops to ~100–250 ms.
- **Port Binding:** Configured to dynamically bind to `0.0.0.0` and the hosting environment's `$PORT` environment variable (`os.getenv("PORT", 8010)`).

### 1.3 Persistent Document Storage & Provenance
- **Synthetic Patient Source PDFs:** 58 reviewed synthetic PDFs and image reports are packaged directly inside `backend/storage/patient_documents/` within the application artifact.
- **Private Stream Access:** Files are never exposed via unauthenticated public buckets. The backend endpoint `/api/v1/patients/{patient_id}/documents/{document_id}/download` authenticates callers using Supabase Auth JWT tokens (`verify_supabase_token`) and checks database RLS access grants before streaming raw PDF bytes.

---

## 2. Security & Audit Policy Configuration

### 2.1 Cryptographic Auth & Identity Verification
- All protected API routes enforce JWT verification through Supabase Auth (`verify_supabase_token` in `backend/app/auth/verifier.py`).
- No magic-string privileged access (e.g. `INTERNAL_SERVICE_ROLE`) or unauthenticated fallback to `service_role` key exists in the codebase.
- Caller identity (`staff_id`) is extracted directly from the verified Supabase Auth JWT payload (`auth.uid()`) and validated against `public.staff_profiles`.

### 2.2 Patient Isolation & RLS
- Cross-patient audit reads and document downloads enforce strict row-level security (`public.staff_patient_access_grants`).
- If an unauthorized staff member attempts to read patient history or retrieve audit logs for an unassigned patient, Supabase RLS returns `403 Forbidden` / empty response.

---

## 3. Environment Variables Reference

### Backend Environment Variables (`backend/.env`)
| Variable | Required | Description | Example |
| :--- | :---: | :--- | :--- |
| `APP_ENV` | Yes | Environment name | `production` or `staging` |
| `DEBUG` | Yes | FastApi debug mode | `False` |
| `HOST` | Yes | Binding host address | `0.0.0.0` |
| `PORT` | Yes | Server listening port | `8010` (or set automatically by host) |
| `CORS_ORIGINS` | Yes | Allowed frontend origins | `["https://carelens-staging.vercel.app"]` |
| `SUPABASE_URL` | Yes | Remote Supabase project URL | `https://xyzcompany.supabase.co` |
| `SUPABASE_ANON_KEY` | Yes | Public Supabase anon key | `eyJhbGciOi...` |
| `GEMINI_API_KEY` | Optional | Google Gemini API key for LLM | `AIzaSy...` |
| `GROQ_API_KEY` | Optional | Groq API key for Llama fallback | `gsk_...` |

### Frontend Environment Variables (`frontend/.env`)
| Variable | Required | Description | Example |
| :--- | :---: | :--- | :--- |
| `VITE_API_BASE_URL` | Yes | HTTPS Backend URL | `https://carelens-api.onrender.com` |
| `VITE_SUPABASE_URL` | Yes | Supabase Project URL | `https://xyzcompany.supabase.co` |
| `VITE_SUPABASE_ANON_KEY` | Yes | Supabase Public Anon Key | `eyJhbGciOi...` |

---

## 4. Step-by-Step Staging Deployment Procedure

### Step A: Database Schema Preparation (Supabase SQL Editor)
Run the following pending SQL migrations in exact order on the remote Supabase project:
1. `database/migrations/011_add_radiology_document_type.sql` (Expands `doc_type` check constraint to include `'radiology'`).
2. `database/migrations/010_incremental_demo_data_update.sql` (Inserts canonical 10-patient dataset using `ON CONFLICT DO NOTHING`).
3. `database/seeds/005_expanded_demo_grants.sql` (Optional: Provisions staff access grants for demo accounts).

### Step B: Deploy Backend to Render / Docker Host
1. Connect GitHub repository `tvarunyadav/carelens-ai-project` to Render.
2. Create a new **Web Service**:
   - **Environment:** Docker (uses `backend/Dockerfile`) or Python 3.11 (`pip install -r requirements.txt`).
   - **Root Directory:** `backend`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
3. Configure Environment Variables in Render Dashboard (`APP_ENV=production`, `DEBUG=False`, `SUPABASE_URL`, `SUPABASE_ANON_KEY`, `GEMINI_API_KEY`, `CORS_ORIGINS`).
4. Deploy and copy the assigned HTTPS backend URL (e.g. `https://carelens-api-staging.onrender.com`).

### Step C: Deploy Frontend to Vercel
1. Import GitHub repository `tvarunyadav/carelens-ai-project` in Vercel.
2. Configure Project Settings:
   - **Framework Preset:** Vite
   - **Root Directory:** `frontend`
   - **Build Command:** `npm run build`
   - **Output Directory:** `dist`
3. Set Environment Variable:
   - `VITE_API_BASE_URL` = `https://carelens-api-staging.onrender.com`
   - `VITE_SUPABASE_URL` = `https://<your-supabase-id>.supabase.co`
   - `VITE_SUPABASE_ANON_KEY` = `<your-supabase-anon-key>`
4. Click **Deploy**. Vercel will build and assign an HTTPS URL (e.g. `https://carelens-ai-staging.vercel.app`).

### Step D: Update CORS & Auth Redirects
1. Update `CORS_ORIGINS` in backend environment variables to include the frontend HTTPS URL.
2. In Supabase Dashboard -> **Authentication** -> **URL Configuration**:
   - Add `https://carelens-ai-staging.vercel.app` to **Redirect URLs**.

---

## 5. Verification Checklist

After deployment, verify the following core flows on the live staging URL:

- [ ] **Authentication Login:** Log in as staff (`alice@example.com` or `bob@example.com`) using Supabase Auth credentials.
- [ ] **Patient Access Isolation:** Select Sophia Williams or Eleanor Vane. Confirm unauthorized staff cannot access ungranted patient workspaces.
- [ ] **History Summary Generation:** Click *Generate Concise History Summary*. Confirm AI summary returns with citation badges.
- [ ] **Original Document Download & Page Citation:** Click *Original file* on Eleanor's AMH report or Sophia's HSG Radiology Report. Verify original PDF opens and jumps to target page.
- [ ] **Multilingual Voice Search:** Verify browser microphone permissions prompt and query execution.
- [ ] **Audit Trail Persistence:** Open Activity History after performing actions. Confirm audit events are saved and displayed with correct staff ID and timestamp.

---

## 6. Deployment Updates & Maintenance Workflow

To push future updates to the live staging environment:

```bash
# 1. Verify tests locally
cd backend
.\venv\Scripts\python.exe -m pytest tests/ -v

# 2. Build frontend
cd ../frontend
npm run build

# 3. Push to staging branch
git checkout -b staging
git add .
git commit -m "feat: staging update release"
git push origin staging
```
Vercel and Render will automatically trigger preview/staging builds upon push.
