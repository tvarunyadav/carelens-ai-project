# CareLens AI Architecture Specification

CareLens AI is a clinical insight engine built for authorized clinic staff to explore and analyze synthetic patient electronic health records (EHR).

## High-Level System Architecture

```mermaid
graph TD
    subgraph Frontend ["Frontend (React 19 + Vite + TypeScript)"]
        UI["CareLens Setup & Insight UI"]
        APIClient["API Client (Fetch + Timeout)"]
        PDFViewer["PDF.js Evidence Viewer (Milestone 5)"]
    end

    subgraph Backend ["Backend (FastAPI + Python 3.11)"]
        CORS["CORS Middleware"]
        AuthMiddleware["Auth & Patient Grant Checks (Milestone 2)"]
        APIRoutes["FastAPI HTTP Router (/health, /patients, /qa)"]
        
        subgraph Modules ["Application Modules"]
            CoreMod["core (Settings & DB Pool)"]
            AuthMod["auth (Role & Patient Grants)"]
            PatientsMod["patients (Directory & Timeline)"]
            IngestionMod["ingestion (pdfplumber & Chunks)"]
            RetrievalMod["retrieval (Sentence Transformers)"]
            ProvidersMod["providers (Gemini SDK & Groq Fallback)"]
            ReconciliationMod["reconciliation (Test Matching & Diffs)"]
            AuditMod["audit (Telemetry & Redacted Access Logs)"]
        end
    end

    subgraph DataStore ["Data & Cloud Tier (Milestone 2+)"]
        SupaDB[("Supabase PostgreSQL + pgvector")]
        SupaStorage[("Supabase Private Storage")]
        GeminiAPI["Google Gemini LLM (google-genai)"]
        GroqAPI["Groq LLM (groq SDK)"]
    end

    UI --> APIClient
    APIClient -->|HTTP / REST| CORS
    CORS --> AuthMiddleware
    AuthMiddleware --> APIRoutes
    APIRoutes --> Modules
    RetrievalMod --> SupaDB
    IngestionMod --> SupaStorage
    ProvidersMod --> GeminiAPI
    ProvidersMod --> GroqAPI
```

## Module Boundaries & Descriptions

| Module | Responsibility Boundary | Milestone |
| :--- | :--- | :--- |
| `core` | Environment settings management (`pydantic-settings`) and database connection pooling. | M1 (Foundations) |
| `auth` | JWT token validation, clinic staff role verification, and patient-level access grants. | M2 |
| `api` | FastAPI route endpoints and request validation. Authorization occurs before any service execution. | M1 + M2 |
| `schemas` | Single source of truth for shared Pydantic data contracts and TypeScript interfaces. | M1 |
| `patients` | Patient directory lookups, timeline compilation, and dynamic patient case brief construction. | M2 & M5 |
| `documents` | Private storage file uploads, signed URL generation, and ingestion state orchestration. | M3 |
| `ingestion` | PDF page extraction (`pdfplumber`), text chunking, bounding box provenance, and candidate facts. | M3 |
| `retrieval` | Patient-scoped vector search using local Sentence Transformers (`all-MiniLM-L6-v2`) and `pgvector`. | M4 |
| `providers` | LLM completion adapter wrapping primary Gemini (`google-genai`) and fallback Groq (`groq`). | M4 & M7 |
| `reconciliation`| Test/result matching, treatment cycle comparison, and versioned report delta tracking. | M6 |
| `audit` | Access and query telemetry logging without exposing credentials or PHI secrets. | M2+ |
