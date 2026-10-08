-- Seed script for CareLens AI Synthetic Patient Records & Initial Staff Configuration

-- Insert Synthetic Patients
INSERT INTO public.patients (id, mrn, first_name, last_name, dob, gender, status, record_version)
VALUES 
    ('11111111-1111-1111-1111-111111111111', 'MRN-884920', 'Eleanor', 'Vane', '1968-04-12', 'Female', 'active', 1),
    ('22222222-2222-2222-2222-222222222222', 'MRN-993041', 'Marcus', 'Chen', '1975-09-28', 'Male', 'active', 1),
    ('33333333-3333-3333-3333-333333333333', 'MRN-441029', 'Sophia', 'Patel', '1982-11-05', 'Female', 'active', 1)
ON CONFLICT (mrn) DO UPDATE 
SET first_name = EXCLUDED.first_name,
    last_name = EXCLUDED.last_name,
    dob = EXCLUDED.dob,
    gender = EXCLUDED.gender;

-- NOTE: Staff Accounts & Grants
-- After creating staff accounts in Supabase Auth (e.g. via Dashboard or Auth API),
-- populate public.staff_profiles and public.patient_access_grants as follows:
--
-- EXAMPLE SQL (Replace <STAFF_UUID_ALICE> and <STAFF_UUID_BOB> with real Supabase Auth user IDs):
--
-- INSERT INTO public.staff_profiles (id, email, full_name, role) VALUES
--   ('<STAFF_UUID_ALICE>', 'dr.alice@clinic.org', 'Dr. Alice Morgan', 'doctor'),
--   ('<STAFF_UUID_BOB>', 'coord.bob@clinic.org', 'Bob Vance', 'coordinator');
--
-- -- Grant Dr. Alice access to Eleanor Vane & Marcus Chen
-- INSERT INTO public.patient_access_grants (staff_id, patient_id, action) VALUES
--   ('<STAFF_UUID_ALICE>', '11111111-1111-1111-1111-111111111111', 'read'),
--   ('<STAFF_UUID_ALICE>', '22222222-2222-2222-2222-222222222222', 'read');
--
-- -- Grant Bob access to Sophia Patel only
-- INSERT INTO public.patient_access_grants (staff_id, patient_id, action) VALUES
--   ('<STAFF_UUID_BOB>', '33333333-3333-3333-3333-333333333333', 'read');
