-- Migration 001: CareLens AI Milestone 2 Schema - Staff Profiles, Patients, Patient Access Grants, Audit Events

-- 1. Create Staff Profiles table linked to Supabase Auth users
CREATE TABLE IF NOT EXISTS public.staff_profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email TEXT NOT NULL,
    full_name TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('doctor', 'coordinator', 'admin')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 2. Create Synthetic Patients table
CREATE TABLE IF NOT EXISTS public.patients (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    mrn TEXT UNIQUE NOT NULL,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    dob DATE NOT NULL,
    gender TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'archived')),
    record_version INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 3. Create Patient Access Grants table
CREATE TABLE IF NOT EXISTS public.patient_access_grants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    staff_id UUID NOT NULL REFERENCES public.staff_profiles(id) ON DELETE CASCADE,
    patient_id UUID NOT NULL REFERENCES public.patients(id) ON DELETE CASCADE,
    action TEXT NOT NULL CHECK (action IN ('read', 'write', 'admin')),
    granted_by UUID REFERENCES public.staff_profiles(id),
    granted_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_staff_patient_action UNIQUE (staff_id, patient_id, action)
);

-- 4. Create Audit Events table for access telemetry (no secret logging)
CREATE TABLE IF NOT EXISTS public.audit_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    staff_id UUID REFERENCES public.staff_profiles(id) ON DELETE SET NULL,
    patient_id UUID REFERENCES public.patients(id) ON DELETE SET NULL,
    action TEXT NOT NULL,
    resource TEXT NOT NULL,
    details_json JSONB NOT NULL DEFAULT '{}'::jsonb
);

-- 5. Indexes for fast access control and isolation queries
CREATE INDEX IF NOT EXISTS idx_staff_profiles_role ON public.staff_profiles(role);
CREATE INDEX IF NOT EXISTS idx_patients_mrn ON public.patients(mrn);
CREATE INDEX IF NOT EXISTS idx_grants_staff ON public.patient_access_grants(staff_id);
CREATE INDEX IF NOT EXISTS idx_grants_patient ON public.patient_access_grants(patient_id);
CREATE INDEX IF NOT EXISTS idx_audit_staff ON public.audit_events(staff_id);

-- 6. Enable Row Level Security (RLS) on all tables
ALTER TABLE public.staff_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.patients ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.patient_access_grants ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.audit_events ENABLE ROW LEVEL SECURITY;

-- 7. RLS Policies

-- Staff Profiles: Staff can read their own profile
CREATE POLICY "Staff can view their own profile"
    ON public.staff_profiles
    FOR SELECT
    USING (auth.uid() = id);

-- Staff Profiles: Users cannot update their own role
CREATE POLICY "Admins can update staff profiles"
    ON public.staff_profiles
    FOR UPDATE
    USING (
        EXISTS (
            SELECT 1 FROM public.staff_profiles
            WHERE id = auth.uid() AND role = 'admin'
        )
    );

-- Patients: Staff can ONLY view patients for which they hold an explicit access grant
CREATE POLICY "Staff can view explicitly granted patients"
    ON public.patients
    FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.patient_access_grants
            WHERE staff_id = auth.uid()
              AND patient_id = public.patients.id
              AND action IN ('read', 'write', 'admin')
        )
    );

-- Patient Access Grants: Staff can view their own assigned grants
CREATE POLICY "Staff can view their own access grants"
    ON public.patient_access_grants
    FOR SELECT
    USING (staff_id = auth.uid());

-- Patient Access Grants: Only explicit admin or coordinator with grant rights can insert/modify grants
CREATE POLICY "Admins and Coordinators can insert access grants"
    ON public.patient_access_grants
    FOR INSERT
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM public.staff_profiles
            WHERE id = auth.uid() AND role IN ('admin', 'coordinator')
        )
    );

-- Audit Events: Staff can insert audit logs for their own actions
CREATE POLICY "Staff can insert audit events"
    ON public.audit_events
    FOR INSERT
    WITH CHECK (staff_id = auth.uid());

CREATE POLICY "Admins can view audit events"
    ON public.audit_events
    FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.staff_profiles
            WHERE id = auth.uid() AND role = 'admin'
        )
    );
