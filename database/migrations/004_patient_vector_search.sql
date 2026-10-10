-- Migration 004: Patient Vector Search & Document Chunking Schema (Milestone 4)
-- Executed FOURTH in Supabase SQL Editor

BEGIN;

-- 1. Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- 2. Create patient_document_chunks table
CREATE TABLE IF NOT EXISTS public.patient_document_chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id UUID NOT NULL REFERENCES public.patients(id) ON DELETE CASCADE,
    document_id UUID NOT NULL REFERENCES public.patient_documents(id) ON DELETE CASCADE,
    document_version_id UUID REFERENCES public.patient_document_versions(id) ON DELETE SET NULL,
    page_number INT NOT NULL DEFAULT 1,
    chunk_index INT NOT NULL DEFAULT 0,
    chunk_text TEXT NOT NULL,
    embedding vector(384) NOT NULL,
    embedding_model TEXT NOT NULL DEFAULT 'all-MiniLM-L6-v2',
    metadata_json JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 3. Indexes for fast retrieval
CREATE INDEX IF NOT EXISTS idx_chunks_patient ON public.patient_document_chunks(patient_id);
CREATE INDEX IF NOT EXISTS idx_chunks_doc ON public.patient_document_chunks(document_id);

-- HNSW index for vector distance queries
CREATE INDEX IF NOT EXISTS idx_chunks_embedding_hnsw 
ON public.patient_document_chunks 
USING hnsw (embedding vector_cosine_ops);

-- 4. Enable Row Level Security (RLS)
ALTER TABLE public.patient_document_chunks ENABLE ROW LEVEL SECURITY;

-- 5. RLS Policy: Users can only view document chunks for patients they hold access grants for
DROP POLICY IF EXISTS "Staff can view document chunks for granted patients" ON public.patient_document_chunks;
CREATE POLICY "Staff can view document chunks for granted patients"
    ON public.patient_document_chunks FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.patient_access_grants
            WHERE staff_id = auth.uid()
              AND patient_id = public.patient_document_chunks.patient_id
              AND action IN ('read', 'write', 'admin')
        )
    );

-- 6. RPC Function for Vector Similarity Search with strict Patient Isolation & SECURITY INVOKER
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
