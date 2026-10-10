-- Migration 005: Patient Vector Search Repair & Model Alignment (Milestone 4 Repair)
-- Executed FIFTH (or incremental) in Supabase SQL Editor AFTER Migration 004

BEGIN;

-- 1. Update default embedding_model on patient_document_chunks
ALTER TABLE public.patient_document_chunks 
    ALTER COLUMN embedding_model SET DEFAULT 'BAAI/bge-small-en-v1.5';

-- 2. Add write policy to allow document chunk insertion/upsertion
DROP POLICY IF EXISTS "Allow document chunk write for backend service" ON public.patient_document_chunks;
CREATE POLICY "Allow document chunk write for backend service"
    ON public.patient_document_chunks FOR ALL
    USING (true)
    WITH CHECK (true);

-- 3. Cleanup stale non-semantic hash vectors (if any exist in live table)
DELETE FROM public.patient_document_chunks 
WHERE embedding_model IS NULL 
   OR embedding_model != 'BAAI/bge-small-en-v1.5';

-- 4. Re-verify RPC function for vector similarity search using BAAI/bge-small-en-v1.5
CREATE OR REPLACE FUNCTION match_patient_document_chunks(
    target_patient_id UUID,
    query_embedding vector(384),
    match_threshold FLOAT DEFAULT 0.0,
    match_count INT DEFAULT 10
)
RETURNS TABLE (
    id UUID,
    patient_id UUID,
    document_id UUID,
    document_version_id UUID,
    page_number INT,
    chunk_index INT,
    chunk_text TEXT,
    similarity FLOAT,
    metadata_json JSONB
)
LANGUAGE plpgsql
SECURITY INVOKER
AS $$
BEGIN
    RETURN QUERY
    SELECT
        c.id,
        c.patient_id,
        c.document_id,
        c.document_version_id,
        c.page_number,
        c.chunk_index,
        c.chunk_text,
        (1.0 - (c.embedding <=> query_embedding))::FLOAT AS similarity,
        c.metadata_json
    FROM public.patient_document_chunks c
    WHERE c.patient_id = target_patient_id
      AND (1.0 - (c.embedding <=> query_embedding)) >= match_threshold
    ORDER BY c.embedding <=> query_embedding ASC
    LIMIT match_count;
END;
$$;

COMMIT;
