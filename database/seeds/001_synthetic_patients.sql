-- Seed 001: Synthetic Patients Data (10 Patients Total)
-- Executed SECOND in Supabase SQL Editor (Independent of Auth Users)

INSERT INTO public.patients (id, mrn, first_name, last_name, dob, gender, status, record_version)
VALUES 
    ('11111111-1111-1111-1111-111111111111', 'MRN-884920', 'Eleanor', 'Vane', '1968-04-12', 'Female', 'active', 1),
    ('22222222-2222-2222-2222-222222222222', 'MRN-993041', 'Marcus', 'Chen', '1975-09-28', 'Male', 'active', 1),
    ('33333333-3333-3333-3333-333333333333', 'MRN-441029', 'Sophia', 'Patel', '1982-11-05', 'Female', 'active', 1),
    ('44444444-4444-4444-4444-444444444444', 'MRN-104928', 'Priya', 'Sharma', '1988-06-15', 'Female', 'active', 1),
    ('55555555-5555-5555-5555-555555555555', 'MRN-552914', 'David', 'Kim', '1980-03-22', 'Male', 'active', 1),
    ('66666666-6666-6666-6666-666666666666', 'MRN-663819', 'Hannah', 'Abbott', '1991-09-10', 'Female', 'active', 1),
    ('77777777-7777-7777-7777-777777777777', 'MRN-771829', 'Carlos', 'Rodriguez', '1984-12-04', 'Male', 'active', 1),
    ('88888888-8888-8888-8888-888888888888', 'MRN-882941', 'Aisha', 'Khan', '1993-02-18', 'Female', 'active', 1),
    ('99999999-9999-9999-9999-999999999999', 'MRN-994812', 'James', 'Wilson', '1979-11-30', 'Male', 'active', 1),
    ('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', 'MRN-109283', 'Maya', 'Lin', '1986-07-08', 'Female', 'active', 1)
ON CONFLICT (mrn) DO NOTHING;
