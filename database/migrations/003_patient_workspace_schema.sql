-- Migration 003: Patient Workspace Schema - Documents, Versions, Timeline Events, Fertility Cycles
-- Executed FOURTH in Supabase SQL Editor

-- 1. Create Patient Documents table
CREATE TABLE IF NOT EXISTS public.patient_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id UUID NOT NULL REFERENCES public.patients(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    doc_type TEXT NOT NULL CHECK (doc_type IN (
        'consultation', 'lab_report', 'procedure', 'ultrasound', 
        'discharge_summary', 'medication_record', 'pending_lab_order'
    )),
    clinical_date DATE NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('final', 'pending', 'archived', 'draft')) DEFAULT 'final',
    storage_path TEXT,
    mime_type TEXT DEFAULT 'application/pdf',
    file_size INTEGER DEFAULT 0,
    current_version INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 2. Create Patient Document Versions table for version control and provenance
CREATE TABLE IF NOT EXISTS public.patient_document_versions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL REFERENCES public.patient_documents(id) ON DELETE CASCADE,
    version_number INTEGER NOT NULL DEFAULT 1,
    storage_path TEXT NOT NULL,
    extracted_text TEXT,
    page_count INTEGER DEFAULT 1,
    extraction_status TEXT NOT NULL CHECK (extraction_status IN ('pending', 'processed', 'failed')) DEFAULT 'pending',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_document_version UNIQUE (document_id, version_number)
);

-- 3. Create Patient Timeline Events table
CREATE TABLE IF NOT EXISTS public.patient_timeline_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id UUID NOT NULL REFERENCES public.patients(id) ON DELETE CASCADE,
    event_date DATE NOT NULL,
    event_type TEXT NOT NULL CHECK (event_type IN (
        'visit', 'lab_result', 'procedure', 'medication', 
        'fertility_cycle', 'follow_up', 'pending_order'
    )),
    title TEXT NOT NULL,
    summary TEXT NOT NULL,
    document_id UUID REFERENCES public.patient_documents(id) ON DELETE SET NULL,
    metadata_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 4. Create Fertility Cycles table
CREATE TABLE IF NOT EXISTS public.fertility_cycles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id UUID NOT NULL REFERENCES public.patients(id) ON DELETE CASCADE,
    cycle_name TEXT NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE,
    status TEXT NOT NULL CHECK (status IN ('active', 'completed', 'cancelled')) DEFAULT 'completed',
    notes_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 5. Performance Indexes
CREATE INDEX IF NOT EXISTS idx_documents_patient ON public.patient_documents(patient_id);
CREATE INDEX IF NOT EXISTS idx_documents_type ON public.patient_documents(doc_type);
CREATE INDEX IF NOT EXISTS idx_documents_date ON public.patient_documents(clinical_date);
CREATE INDEX IF NOT EXISTS idx_doc_versions_doc ON public.patient_document_versions(document_id);
CREATE INDEX IF NOT EXISTS idx_timeline_patient ON public.patient_timeline_events(patient_id);
CREATE INDEX IF NOT EXISTS idx_timeline_date ON public.patient_timeline_events(event_date);
CREATE INDEX IF NOT EXISTS idx_timeline_type ON public.patient_timeline_events(event_type);
CREATE INDEX IF NOT EXISTS idx_cycles_patient ON public.fertility_cycles(patient_id);

-- 6. Enable Row Level Security (RLS)
ALTER TABLE public.patient_documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.patient_document_versions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.patient_timeline_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.fertility_cycles ENABLE ROW LEVEL SECURITY;

-- 7. Row Level Security Policies (Enforce explicit access grants; no auto admin clinical bypass)

-- patient_documents
CREATE POLICY "Staff can view explicitly granted patient documents"
    ON public.patient_documents FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.patient_access_grants
            WHERE staff_id = auth.uid()
              AND patient_id = public.patient_documents.patient_id
              AND action IN ('read', 'write', 'admin')
        )
    );

CREATE POLICY "Staff can write explicitly granted patient documents"
    ON public.patient_documents FOR INSERT
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM public.patient_access_grants
            WHERE staff_id = auth.uid()
              AND patient_id = public.patient_documents.patient_id
              AND action IN ('write', 'admin')
        )
    );

-- patient_document_versions
CREATE POLICY "Staff can view explicitly granted document versions"
    ON public.patient_document_versions FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.patient_documents pd
            JOIN public.patient_access_grants pag ON pag.patient_id = pd.patient_id
            WHERE pd.id = public.patient_document_versions.document_id
              AND pag.staff_id = auth.uid()
              AND pag.action IN ('read', 'write', 'admin')
        )
    );

-- patient_timeline_events
CREATE POLICY "Staff can view explicitly granted timeline events"
    ON public.patient_timeline_events FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.patient_access_grants
            WHERE staff_id = auth.uid()
              AND patient_id = public.patient_timeline_events.patient_id
              AND action IN ('read', 'write', 'admin')
        )
    );

CREATE POLICY "Staff can write explicitly granted timeline events"
    ON public.patient_timeline_events FOR INSERT
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM public.patient_access_grants
            WHERE staff_id = auth.uid()
              AND patient_id = public.patient_timeline_events.patient_id
              AND action IN ('write', 'admin')
        )
    );

-- fertility_cycles
CREATE POLICY "Staff can view explicitly granted fertility cycles"
    ON public.fertility_cycles FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.patient_access_grants
            WHERE staff_id = auth.uid()
              AND patient_id = public.fertility_cycles.patient_id
              AND action IN ('read', 'write', 'admin')
        )
    );
