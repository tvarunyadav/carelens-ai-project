-- Seed 005: Optional Demo Grants for Expanded 10-Patient Dataset
-- Grants Dr. Alice Morgan read access to additional synthetic patients for demo evaluation.
-- Executed ONLY when authorized by clinic admin.

BEGIN;

-- Dr. Alice Morgan (doctor) -> Read access for expanded patients
INSERT INTO public.patient_access_grants (staff_id, patient_id, action)
SELECT sp.id, p.id, 'read'
FROM public.staff_profiles sp
CROSS JOIN (
    SELECT id FROM public.patients WHERE id IN (
        '44444444-4444-4444-4444-444444444444', -- Priya Sharma
        '55555555-5555-5555-5555-555555555555', -- David Kim
        '66666666-6666-6666-6666-666666666666', -- Hannah Abbott
        '77777777-7777-7777-7777-777777777777', -- Carlos Rodriguez
        '88888888-8888-8888-8888-888888888888', -- Aisha Khan
        '99999999-9999-9999-9999-999999999999', -- James Wilson
        'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa'  -- Maya Lin
    )
) p
WHERE sp.email = 'dr.alice@clinic.org'
ON CONFLICT (staff_id, patient_id, action) DO NOTHING;

COMMIT;
