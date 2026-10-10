-- Seed 002: Staff Profiles & Patient Access Grants Template (Dynamic Auth UUID Resolution)
-- Executed THIRD in Supabase SQL Editor AFTER creating staff accounts in Supabase Auth

BEGIN;

-- 1. Insert/Update Staff Profiles resolving Auth UUIDs by exact email
INSERT INTO public.staff_profiles (id, email, full_name, role)
SELECT id, 'dr.alice@clinic.org', 'Dr. Alice Morgan', 'doctor'
FROM auth.users WHERE email = 'dr.alice@clinic.org'
ON CONFLICT (id) DO UPDATE SET
    email = EXCLUDED.email,
    full_name = EXCLUDED.full_name,
    role = EXCLUDED.role;

INSERT INTO public.staff_profiles (id, email, full_name, role)
SELECT id, 'coord.bob@clinic.org', 'Bob Vance', 'coordinator'
FROM auth.users WHERE email = 'coord.bob@clinic.org'
ON CONFLICT (id) DO UPDATE SET
    email = EXCLUDED.email,
    full_name = EXCLUDED.full_name,
    role = EXCLUDED.role;

-- 2. Clear old access grants for Alice and Bob only
DELETE FROM public.patient_access_grants
WHERE staff_id IN (
    SELECT id FROM public.staff_profiles WHERE email IN ('dr.alice@clinic.org', 'coord.bob@clinic.org')
);

-- 3. Grant Dr. Alice access to Eleanor Vane & Marcus Chen
INSERT INTO public.patient_access_grants (staff_id, patient_id, action)
SELECT sp.id, '11111111-1111-1111-1111-111111111111'::uuid, 'read'
FROM public.staff_profiles sp WHERE sp.email = 'dr.alice@clinic.org'
ON CONFLICT (staff_id, patient_id, action) DO NOTHING;

INSERT INTO public.patient_access_grants (staff_id, patient_id, action)
SELECT sp.id, '22222222-2222-2222-2222-222222222222'::uuid, 'read'
FROM public.staff_profiles sp WHERE sp.email = 'dr.alice@clinic.org'
ON CONFLICT (staff_id, patient_id, action) DO NOTHING;

-- 4. Grant Bob Vance access to Sophia Patel ONLY
INSERT INTO public.patient_access_grants (staff_id, patient_id, action)
SELECT sp.id, '33333333-3333-3333-3333-333333333333'::uuid, 'read'
FROM public.staff_profiles sp WHERE sp.email = 'coord.bob@clinic.org'
ON CONFLICT (staff_id, patient_id, action) DO NOTHING;

COMMIT;
