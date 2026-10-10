-- Migration 008: Secure Atomic Version Allocation & Insertion RPC, Unique Version Constraint, & Exact Seed Review Backfill
-- Executed EIGHTH in Supabase SQL Editor

BEGIN;

-- 1. Drop any obsolete/overloaded versions of create_atomic_document_version function
DROP FUNCTION IF EXISTS public.create_atomic_document_version(UUID, TEXT, TEXT, UUID, TEXT, TEXT);
DROP FUNCTION IF EXISTS public.create_atomic_document_version(UUID, TEXT, TEXT, UUID);
DROP FUNCTION IF EXISTS public.create_atomic_document_version(UUID, TEXT, TEXT);

-- 2. Add database-level unique constraint on patient_document_versions(document_id, version_number)
ALTER TABLE public.patient_document_versions
    DROP CONSTRAINT IF EXISTS uq_doc_version_number;

ALTER TABLE public.patient_document_versions
    ADD CONSTRAINT uq_doc_version_number UNIQUE (document_id, version_number);

-- 3. Add per-version review_status tracking column if not present
ALTER TABLE public.patient_document_versions
    ADD COLUMN IF NOT EXISTS review_status TEXT CHECK (review_status IN ('pending_review', 'reviewed', 'rejected')) DEFAULT 'pending_review';

-- 4. Secure Atomic Version Allocation AND Insertion RPC Function
-- Parameters: ONLY p_document_id, p_storage_path, p_content_hash, and optional p_extraction_provenance.
-- Column mapping verified against schema:
--   - storage_path (TEXT NOT NULL)
--   - extraction_status (TEXT NOT NULL CHECK IN ('pending', 'processed', 'failed'))
--   - review_status (TEXT CHECK IN ('pending_review', 'reviewed', 'rejected'))
-- Uploader identity is derived EXCLUSIVELY from auth.uid().
-- Review state is forced to 'pending_review' (caller CANNOT spoof uploader or review_status).
CREATE OR REPLACE FUNCTION public.create_atomic_document_version(
    p_document_id UUID,
    p_storage_path TEXT,
    p_content_hash TEXT,
    p_extraction_provenance TEXT DEFAULT 'pypdf_text'
)
RETURNS TABLE (
    id UUID,
    document_id UUID,
    version_number INT,
    storage_path TEXT,
    content_hash TEXT,
    uploaded_by UUID,
    review_status TEXT,
    extraction_status TEXT,
    created_at TIMESTAMPTZ
)
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public, pg_temp
AS $$
DECLARE
    v_patient_id UUID;
    v_next_version INT;
    v_caller_id UUID;
    v_staff_exists BOOLEAN;
    v_has_write BOOLEAN;
    v_new_version_id UUID;
BEGIN
    -- Derive caller identity exclusively from verified session JWT
    v_caller_id := auth.uid();
    IF v_caller_id IS NULL THEN
        RAISE EXCEPTION 'Unauthenticated: Caller session token missing or invalid.';
    END IF;

    -- Enforce staff profile record existence in public.staff_profiles
    SELECT EXISTS (
        SELECT 1 FROM public.staff_profiles
        WHERE id = v_caller_id
    ) INTO v_staff_exists;

    IF NOT v_staff_exists THEN
        RAISE EXCEPTION 'Access denied: Staff profile record not found for user %.', v_caller_id;
    END IF;

    -- Lock target parent document row to serialize concurrent version allocation requests
    SELECT patient_id INTO v_patient_id
    FROM public.patient_documents
    WHERE public.patient_documents.id = p_document_id
    FOR UPDATE;

    IF v_patient_id IS NULL THEN
        RAISE EXCEPTION 'Target document record % not found.', p_document_id;
    END IF;

    -- Enforce explicit patient write or admin access grant
    SELECT EXISTS (
        SELECT 1 FROM public.patient_access_grants
        WHERE staff_id = v_caller_id
          AND patient_id = v_patient_id
          AND action IN ('write', 'admin')
    ) INTO v_has_write;

    IF NOT v_has_write THEN
        RAISE EXCEPTION 'Access denied: Explicit write or admin access grant required for patient %.', v_patient_id;
    END IF;

    -- Calculate next sequential version number atomically
    SELECT COALESCE(MAX(v.version_number), 0) + 1 INTO v_next_version
    FROM public.patient_document_versions v
    WHERE v.document_id = p_document_id;

    -- Reserve and insert new version row inside the exact same database transaction
    -- Force review_status = 'pending_review', extraction_status = 'pending', and uploaded_by = v_caller_id
    INSERT INTO public.patient_document_versions (
        document_id,
        version_number,
        storage_path,
        content_hash,
        uploaded_by,
        extraction_provenance,
        review_status,
        extraction_status
    ) VALUES (
        p_document_id,
        v_next_version,
        p_storage_path,
        p_content_hash,
        v_caller_id,
        p_extraction_provenance,
        'pending_review',
        'pending'
    )
    RETURNING public.patient_document_versions.id INTO v_new_version_id;

    RETURN QUERY
    SELECT 
        v.id,
        v.document_id,
        v.version_number,
        v.storage_path,
        v.content_hash,
        v.uploaded_by,
        v.review_status,
        v.extraction_status,
        v.created_at
    FROM public.patient_document_versions v
    WHERE v.id = v_new_version_id;
END;
$$;

-- Restrict function execution permissions to authenticated role
REVOKE EXECUTE ON FUNCTION public.create_atomic_document_version(UUID, TEXT, TEXT, TEXT) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION public.create_atomic_document_version(UUID, TEXT, TEXT, TEXT) TO authenticated;

-- 5. Safe Review Backfill: Approve ONLY explicitly identified synthetic seed document versions by ID
-- Preserves pending lab order 'ab391481-b0aa-50b6-8b67-7d45e93fefc5' as status = 'pending'

UPDATE public.patient_documents
SET review_status = 'reviewed'
WHERE id IN (
    'af9f7471-a2d7-5201-9be0-941dade5425f',
    '9ad6e8a2-35c0-5341-94c2-668c278b4a2f',
    '578cce82-30fc-5664-ae03-4db7c6b3e5d3',
    'f3f6693c-c7c9-5e57-996c-2905ad3d0ac6',
    'a9ab0d19-4792-551e-91cb-b189d18a7ad3',
    '20a807f0-9ebd-5d8d-a2f6-d88349517bae',
    'f6183083-8b99-555e-878d-f0b7b6193a0e',
    '851458f0-e752-507a-b2d1-c9fb058b0f6e',
    '74e7a0de-90dd-57bd-b6db-9a35d85360bc',
    'dc8ca327-bcca-5cf3-b302-01b4b5b2b7c6',
    '27f43378-7d46-5137-b1b7-b9e1d07cf15b'
);

UPDATE public.patient_document_versions
SET review_status = 'reviewed'
WHERE document_id IN (
    'af9f7471-a2d7-5201-9be0-941dade5425f',
    '9ad6e8a2-35c0-5341-94c2-668c278b4a2f',
    '578cce82-30fc-5664-ae03-4db7c6b3e5d3',
    'f3f6693c-c7c9-5e57-996c-2905ad3d0ac6',
    'a9ab0d19-4792-551e-91cb-b189d18a7ad3',
    '20a807f0-9ebd-5d8d-a2f6-d88349517bae',
    'f6183083-8b99-555e-878d-f0b7b6193a0e',
    '851458f0-e752-507a-b2d1-c9fb058b0f6e',
    '74e7a0de-90dd-57bd-b6db-9a35d85360bc',
    'dc8ca327-bcca-5cf3-b302-01b4b5b2b7c6',
    '27f43378-7d46-5137-b1b7-b9e1d07cf15b'
) AND version_number = 1;

COMMIT;
