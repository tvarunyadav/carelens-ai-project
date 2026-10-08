-- Seed 002: Staff Profiles & Patient Access Grants Template
-- Executed THIRD in Supabase SQL Editor AFTER creating staff accounts in Supabase Auth

-- Replace '<STAFF_UUID_ALICE>' and '<STAFF_UUID_BOB>' with actual Auth User IDs from Supabase Dashboard

-- 1. Insert Staff Profiles linked to Supabase Auth UUIDs
-- INSERT INTO public.staff_profiles (id, email, full_name, role) VALUES
--     ('<STAFF_UUID_ALICE>', 'dr.alice@clinic.org', 'Dr. Alice Morgan', 'doctor'),
--     ('<STAFF_UUID_BOB>', 'coord.bob@clinic.org', 'Bob Vance', 'coordinator');

-- 2. Grant Dr. Alice access to Eleanor Vane & Marcus Chen
-- INSERT INTO public.patient_access_grants (staff_id, patient_id, action) VALUES
--     ('<STAFF_UUID_ALICE>', '11111111-1111-1111-1111-111111111111', 'read'),
--     ('<STAFF_UUID_ALICE>', '22222222-2222-2222-2222-222222222222', 'read');

-- 3. Grant Bob access to Sophia Patel ONLY
-- INSERT INTO public.patient_access_grants (staff_id, patient_id, action) VALUES
--     ('<STAFF_UUID_BOB>', '33333333-3333-3333-3333-333333333333', 'read');
