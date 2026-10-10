-- Migration 009: CareLens AI Conflict Reviews & Reconciliation Table
-- Stores explicit staff review decisions and resolution outcomes for conflicting clinical records.

BEGIN;

CREATE TABLE IF NOT EXISTS public.clinical_conflict_reviews (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id UUID NOT NULL REFERENCES public.patients(id) ON DELETE CASCADE,
    conflict_type VARCHAR(100) NOT NULL,
    original_evidence_json JSONB NOT NULL,
    resolution_status VARCHAR(50) NOT NULL DEFAULT 'under_review',
    review_reason TEXT NOT NULL,
    reviewed_by UUID NOT NULL REFERENCES public.staff_profiles(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_conflict_reviews_patient ON public.clinical_conflict_reviews(patient_id);
CREATE INDEX IF NOT EXISTS idx_conflict_reviews_staff ON public.clinical_conflict_reviews(reviewed_by);

-- 2. Enable Row Level Security

ALTER TABLE public.clinical_conflict_reviews ENABLE ROW LEVEL SECURITY;

REVOKE ALL ON public.clinical_conflict_reviews FROM anon;
GRANT SELECT, INSERT, UPDATE ON public.clinical_conflict_reviews TO authenticated;

CREATE POLICY "Staff read conflict reviews for permitted patients"
    ON public.clinical_conflict_reviews
    FOR SELECT
    TO authenticated
    USING (
        EXISTS (
            SELECT 1 FROM public.patient_access_grants
            WHERE staff_id = auth.uid()
              AND patient_id = public.clinical_conflict_reviews.patient_id
              AND action IN ('read', 'write', 'admin')
        )
    );

CREATE POLICY "Staff insert conflict reviews with write/admin access"
    ON public.clinical_conflict_reviews
    FOR INSERT
    TO authenticated
    WITH CHECK (
        reviewed_by = auth.uid()
        AND EXISTS (
            SELECT 1 FROM public.patient_access_grants
            WHERE staff_id = auth.uid()
              AND patient_id = public.clinical_conflict_reviews.patient_id
              AND action IN ('write', 'admin')
        )
    );

COMMIT;
