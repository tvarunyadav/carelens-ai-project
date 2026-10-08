-- Seed 001: Synthetic Patients Data
-- Executed SECOND in Supabase SQL Editor (Independent of Auth Users)

INSERT INTO public.patients (id, mrn, first_name, last_name, dob, gender, status, record_version)
VALUES 
    ('11111111-1111-1111-1111-111111111111', 'MRN-884920', 'Eleanor', 'Vane', '1968-04-12', 'Female', 'active', 1),
    ('22222222-2222-2222-2222-222222222222', 'MRN-993041', 'Marcus', 'Chen', '1975-09-28', 'Male', 'active', 1),
    ('33333333-3333-3333-3333-333333333333', 'MRN-441029', 'Sophia', 'Patel', '1982-11-05', 'Female', 'active', 1)
ON CONFLICT (mrn) DO UPDATE 
SET first_name = EXCLUDED.first_name,
    last_name = EXCLUDED.last_name,
    dob = EXCLUDED.dob,
    gender = EXCLUDED.gender,
    status = EXCLUDED.status;
