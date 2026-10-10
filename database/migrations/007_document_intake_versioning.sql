-- Migration 007: Document Intake, Review Workflow, Content Hash Indexes, Atomic Versioning & Storage Policies
-- Executed SEVENTH in Supabase SQL Editor

-- 1. Extend patient_documents table
ALTER TABLE public.patient_documents 
    ADD COLUMN IF NOT EXISTS content_hash TEXT,
    ADD COLUMN IF NOT EXISTS review_status TEXT CHECK (review_status IN ('pending_review', 'reviewed', 'rejected')) DEFAULT 'pending_review',
    ADD COLUMN IF NOT EXISTS reviewed_by UUID REFERENCES public.staff_profiles(id),
    ADD COLUMN IF NOT EXISTS reviewed_at TIMESTAMPTZ,
    ADD COLUMN IF NOT EXISTS order_id UUID REFERENCES public.patient_timeline_events(id) ON DELETE SET NULL;

-- 2. Extend patient_document_versions table
ALTER TABLE public.patient_document_versions
    ADD COLUMN IF NOT EXISTS content_hash TEXT,
    ADD COLUMN IF NOT EXISTS uploaded_by UUID REFERENCES public.staff_profiles(id),
    ADD COLUMN IF NOT EXISTS extraction_provenance TEXT DEFAULT 'pypdf_text',
    ADD COLUMN IF NOT EXISTS error_message TEXT,
    ADD COLUMN IF NOT EXISTS metadata_suggestions JSONB DEFAULT '{}'::jsonb;

-- 3. Extend patient_document_chunks table for version tracking
ALTER TABLE public.patient_document_chunks
    ADD COLUMN IF NOT EXISTS document_version_id UUID REFERENCES public.patient_document_versions(id) ON DELETE CASCADE;

-- 4. Schema extensions complete (Backfill handled selectively in Migration 008)

-- 5. Indexes for scoped content hash duplicate detection & vector search
CREATE INDEX IF NOT EXISTS idx_documents_patient_hash ON public.patient_documents(patient_id, content_hash);
CREATE INDEX IF NOT EXISTS idx_doc_versions_hash ON public.patient_document_versions(document_id, content_hash);
CREATE INDEX IF NOT EXISTS idx_chunks_doc_ver ON public.patient_document_chunks(document_id, document_version_id);

-- 6. Database-level atomic concurrency-safe version allocation function
CREATE OR REPLACE FUNCTION public.allocate_next_document_version(p_document_id UUID)
RETURNS INTEGER
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    v_next_version INTEGER;
BEGIN
    -- Lock target document row to serialize concurrent version creation requests
    PERFORM id FROM public.patient_documents WHERE id = p_document_id FOR UPDATE;

    -- Calculate next version number
    SELECT COALESCE(MAX(version_number), 0) + 1 INTO v_next_version
    FROM public.patient_document_versions
    WHERE document_id = p_document_id;

    RETURN v_next_version;
END;
$$;

-- 7. Create Private Supabase Storage Bucket for patient documents
INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
VALUES (
    'patient-documents',
    'patient-documents',
    false, -- Private bucket (no public access)
    15728640, -- 15 MB limit
    ARRAY['application/pdf', 'image/png', 'image/jpeg']
)
ON CONFLICT (id) DO UPDATE SET public = false;

-- 8. Row Level Security Policies for Patient Documents & Versions

-- patient_documents INSERT policy (requires write or admin grant)
DROP POLICY IF EXISTS "Staff can write explicitly granted patient documents" ON public.patient_documents;
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

-- patient_documents UPDATE policy (requires write or admin grant)
DROP POLICY IF EXISTS "Staff can update explicitly granted patient documents" ON public.patient_documents;
CREATE POLICY "Staff can update explicitly granted patient documents"
    ON public.patient_documents FOR UPDATE
    USING (
        EXISTS (
            SELECT 1 FROM public.patient_access_grants
            WHERE staff_id = auth.uid()
              AND patient_id = public.patient_documents.patient_id
              AND action IN ('write', 'admin')
        )
    );

-- patient_document_versions INSERT policy (requires write or admin grant)
DROP POLICY IF EXISTS "Staff can write explicitly granted document versions" ON public.patient_document_versions;
CREATE POLICY "Staff can write explicitly granted document versions"
    ON public.patient_document_versions FOR INSERT
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM public.patient_documents pd
            JOIN public.patient_access_grants pag ON pag.patient_id = pd.patient_id
            WHERE pd.id = public.patient_document_versions.document_id
              AND pag.staff_id = auth.uid()
              AND pag.action IN ('write', 'admin')
        )
    );

-- 9. Storage RLS Policies for patient-documents bucket

DROP POLICY IF EXISTS "Staff write grant permits storage upload" ON storage.objects;
CREATE POLICY "Staff write grant permits storage upload"
    ON storage.objects FOR INSERT
    WITH CHECK (
        bucket_id = 'patient-documents'
        AND auth.uid() IS NOT NULL
        AND EXISTS (
            SELECT 1 FROM public.patient_access_grants pag
            WHERE pag.staff_id = auth.uid()
              AND pag.action IN ('write', 'admin')
        )
    );

DROP POLICY IF EXISTS "Staff read grant permits storage download" ON storage.objects;
CREATE POLICY "Staff read grant permits storage download"
    ON storage.objects FOR SELECT
    USING (
        bucket_id = 'patient-documents'
        AND auth.uid() IS NOT NULL
        AND EXISTS (
            SELECT 1 FROM public.patient_access_grants pag
            WHERE pag.staff_id = auth.uid()
              AND pag.action IN ('read', 'write', 'admin')
        )
    );
