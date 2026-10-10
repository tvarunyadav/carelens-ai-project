-- Migration 006: CareLens AI Restricted Audit Logging & Security Policies
-- Ensures immutable, non-repudiable audit telemetry derived strictly from authenticated session identity.
-- Revokes anonymous access, enforces patient access grants on clinical audit events, and blocks update/delete.

BEGIN;

-- 1. Remove legacy or overly permissive policies on audit_events
DROP POLICY IF EXISTS "Allow staff to insert audit events" ON public.audit_events;
DROP POLICY IF EXISTS "Allow staff and anon to insert audit events" ON public.audit_events;
DROP POLICY IF EXISTS "Staff can insert audit events" ON public.audit_events;
DROP POLICY IF EXISTS "Admins can view audit events" ON public.audit_events;
DROP POLICY IF EXISTS "Staff can view their own audit events" ON public.audit_events;
DROP POLICY IF EXISTS "Staff restricted insert audit events" ON public.audit_events;
DROP POLICY IF EXISTS "Staff view own audit events or admin view all" ON public.audit_events;

-- 2. Ensure Row Level Security is active
ALTER TABLE public.audit_events ENABLE ROW LEVEL SECURITY;

-- 3. Explicit Privilege Scope: Revoke all from anon, grant controlled access to authenticated staff
REVOKE ALL ON public.audit_events FROM anon;
GRANT SELECT, INSERT ON public.audit_events TO authenticated;

-- 4. INSERT Policy: Authenticated staff can insert audit events ONLY for their own verified identity
-- Enforces patient access grant verification for successful clinical access events.
CREATE POLICY "Staff restricted insert audit events"
    ON public.audit_events
    FOR INSERT
    TO authenticated
    WITH CHECK (
        -- 4a. Actor identity MUST match the cryptographically verified session (no spoofing)
        staff_id = auth.uid()
        -- 4b. Verified staff profile record MUST exist
        AND EXISTS (
            SELECT 1 FROM public.staff_profiles
            WHERE id = auth.uid()
        )
        -- 4c. Patient access boundary enforcement
        AND (
            patient_id IS NULL
            OR action = 'DENIED_ACCESS_ATTEMPT'
            OR EXISTS (
                SELECT 1 FROM public.patient_access_grants
                WHERE staff_id = auth.uid()
                  AND patient_id = public.audit_events.patient_id
                  AND action IN ('read', 'write', 'admin')
            )
        )
    );

-- 5. SELECT Policy: Staff can inspect their own access history; Admins can audit all records
CREATE POLICY "Staff view own audit events or admin view all"
    ON public.audit_events
    FOR SELECT
    TO authenticated
    USING (
        staff_id = auth.uid()
        OR EXISTS (
            SELECT 1 FROM public.staff_profiles
            WHERE id = auth.uid() AND role = 'admin'
        )
        OR EXISTS (
            SELECT 1 FROM public.patient_access_grants
            WHERE staff_id = auth.uid()
              AND patient_id = public.audit_events.patient_id
              AND action IN ('read', 'write', 'admin')
        )
    );

-- Note: No UPDATE or DELETE policies are granted. Audit records remain strictly append-only and immutable.

COMMIT;
