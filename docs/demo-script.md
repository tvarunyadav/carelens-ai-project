# CareLens AI - Live Demonstration Script & Technical Walkthrough

**Target Problem:** Problem 2 — Patient History Retrieval & EHR Insight Engine  
**Environment:** Local Development (`http://localhost:5173` frontend, `http://127.0.0.1:8010` backend)  
**Security Model:** Cryptographic Supabase JWT Authentication & Row Level Security (RLS)

---

## 1. Authentication & Role-Based Access Boundary

### Step 1.1: Log in as Dr. Alice Morgan (Doctor)
- **Action**: Navigate to `http://localhost:5173/login`, select **Dr. Alice Morgan** (`dr.alice@clinic.org`).
- **Observed Result**: Authenticates via Supabase Auth. Displays active staff profile: `Dr. Alice Morgan (doctor)`.
- **Patient Access Boundary**: Directory displays authorized patients (**Eleanor Vane**, **Marcus Chen**, etc.).

### Step 1.2: Log in as Bob Vance (Coordinator)
- **Action**: Switch account to **Bob Vance** (`coord.bob@clinic.org`).
- **Observed Result**: Directory displays **Sophia Patel** (`33333333-3333-3333-3333-333333333333`).
- **Read-Only Enforcement**: "Upload Document" and "New Version" buttons are strictly hidden. Direct upload attempt returns `403 Forbidden`.

---

## 2. Patient History Retrieval & Visual Timeline

### Step 2.1: Patient Workspace Exploration
- **Action**: Open **Sophia Patel**'s workspace.
- **Observed Result**:
  - **Demographics Header**: Name, MRN (`MRN-441029`), DOB (`1982-11-05`), calculated age, gender.
  - **Interactive Timeline**: Chronological display of visits, baseline hormone labs, ovulation induction, oocyte retrieval, and frozen embryo transfer (FET).

### Step 2.2: Plain-Language AI Query & Grounded Citations
- **Action**: Ask question: *"What were her last two cycles, and which reports are pending?"*
- **Observed Result**:
  - **Retrieved Cycles**: Cycle 1 (May 1–28, 2026: 10 oocytes retrieved, 4 blastocysts frozen); FET Cycle 2 (July 10–Sept 1, 2026: Day 5 4AA blastocyst transfer).
  - **Explicit Pending Orders**: Identifies Karyotype & Microarray Lab Order (Sept 15, 2026) as **"Result not recorded"**.
  - **Grounding & Provenance**: Response includes clickable citation badges `[EV-1]`, `[EV-2]`.

---

## 3. Original Document Viewer & Page Provenance

### Step 3.1: Open Source Citation
- **Action**: Click citation badge `[EV-1]`.
- **Observed Result**: Opens document viewer modal streaming the original synthetic PDF file (`sophia_initial_consultation_2026-04-15.pdf`).
- **Cleanup**: Closing the modal revokes blob object URLs (`URL.revokeObjectURL`) to prevent browser memory leaks.

---

## 4. Secure Document Intake, Versioning & Audit Persistence

### Step 4.1: Authorized Document Upload
- **Action**: As Dr. Alice Morgan, upload `synthetic_text_doc_v1.pdf` for Eleanor Vane.
- **Observed Result**: Document uploaded via `multipart/form-data`, text extracted via `pdfplumber`, queued for human review as `pending_review`.

### Step 4.2: Audit Logging
- **Action**: Check Audit History.
- **Observed Result**: Displays persisted event: `OPEN_DOCUMENT_SOURCE` / `UPLOAD_DOCUMENT` with actor ID, timestamp, resource URL, and action details.
