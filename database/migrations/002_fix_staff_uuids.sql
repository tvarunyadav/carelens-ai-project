-- Migration 002: Correct Demo Staff Profiles and Access Grants UUID Mapping
-- Transactional, in-place update for Bob Vance and Dr. Alice Morgan without DELETE operations.

BEGIN;

-- 1. Pre-execution verification and assertion checks
DO $$
DECLARE
    v_bob_auth_id UUID;
    v_alice_auth_id UUID;
    v_bob_profile_count INTEGER;
    v_alice_profile_count INTEGER;
    v_third_party_count INTEGER;
BEGIN
    -- A. Verify auth.users matches exact email/UUID pairs
    SELECT id INTO v_bob_auth_id FROM auth.users WHERE email = 'coord.bob@clinic.org';
    SELECT id INTO v_alice_auth_id FROM auth.users WHERE email = 'dr.alice@clinic.org';

    IF v_bob_auth_id IS NULL OR v_bob_auth_id != '7b7c7b68-8c02-4081-a5a3-18b6cdcb26f7'::uuid THEN
        RAISE EXCEPTION 'Verification failed: auth.users for coord.bob@clinic.org does not match expected UUID 7b7c7b68-8c02-4081-a5a3-18b6cdcb26f7 (Found: %)', v_bob_auth_id;
    END IF;

    IF v_alice_auth_id IS NULL OR v_alice_auth_id != 'e562028e-e5d5-48be-81f1-14446243a01c'::uuid THEN
        RAISE EXCEPTION 'Verification failed: auth.users for dr.alice@clinic.org does not match expected UUID e562028e-e5d5-48be-81f1-14446243a01c (Found: %)', v_alice_auth_id;
    END IF;

    -- B. Assert both target staff_profiles rows exist
    SELECT COUNT(*) INTO v_bob_profile_count FROM public.staff_profiles WHERE id = '7b7c7b68-8c02-4081-a5a3-18b6cdcb26f7'::uuid;
    SELECT COUNT(*) INTO v_alice_profile_count FROM public.staff_profiles WHERE id = 'e562028e-e5d5-48be-81f1-14446243a01c'::uuid;

    IF v_bob_profile_count = 0 THEN
        RAISE EXCEPTION 'Assertion failed: staff_profiles row for Bob UUID 7b7c7b68-8c02-4081-a5a3-18b6cdcb26f7 does not exist';
    END IF;

    IF v_alice_profile_count = 0 THEN
        RAISE EXCEPTION 'Assertion failed: staff_profiles row for Alice UUID e562028e-e5d5-48be-81f1-14446243a01c does not exist';
    END IF;

    -- C. Abort if either intended email belongs to a third profile
    SELECT COUNT(*) INTO v_third_party_count
    FROM public.staff_profiles
    WHERE email IN ('coord.bob@clinic.org', 'dr.alice@clinic.org')
      AND id NOT IN ('7b7c7b68-8c02-4081-a5a3-18b6cdcb26f7'::uuid, 'e562028e-e5d5-48be-81f1-14446243a01c'::uuid);

    IF v_third_party_count > 0 THEN
        RAISE EXCEPTION 'Safety check failed: Intended email belongs to a third staff profile record';
    END IF;
END $$;

-- 2. Step 1: Temporarily set target profiles to distinct unused placeholder emails to prevent unique email conflict
UPDATE public.staff_profiles
SET email = 'temp_swap_7b7c7b68@clinic.temp',
    updated_at = NOW()
WHERE id = '7b7c7b68-8c02-4081-a5a3-18b6cdcb26f7'::uuid;

UPDATE public.staff_profiles
SET email = 'temp_swap_e562028e@clinic.temp',
    updated_at = NOW()
WHERE id = 'e562028e-e5d5-48be-81f1-14446243a01c'::uuid;

-- 3. Step 2: UPDATE each profile by its exact UUID to the correct email, full_name, and role
UPDATE public.staff_profiles
SET email = 'coord.bob@clinic.org',
    full_name = 'Bob Vance',
    role = 'coordinator',
    updated_at = NOW()
WHERE id = '7b7c7b68-8c02-4081-a5a3-18b6cdcb26f7'::uuid;

UPDATE public.staff_profiles
SET email = 'dr.alice@clinic.org',
    full_name = 'Dr. Alice Morgan',
    role = 'doctor',
    updated_at = NOW()
WHERE id = 'e562028e-e5d5-48be-81f1-14446243a01c'::uuid;

-- 4. Step 3: Replace access grants for these two UUIDs only
DELETE FROM public.patient_access_grants
WHERE staff_id IN ('7b7c7b68-8c02-4081-a5a3-18b6cdcb26f7'::uuid, 'e562028e-e5d5-48be-81f1-14446243a01c'::uuid);

-- Dr. Alice Morgan (doctor) -> Eleanor Vane & Marcus Chen
INSERT INTO public.patient_access_grants (staff_id, patient_id, action) VALUES
    ('e562028e-e5d5-48be-81f1-14446243a01c', '11111111-1111-1111-1111-111111111111', 'read'),
    ('e562028e-e5d5-48be-81f1-14446243a01c', '22222222-2222-2222-2222-222222222222', 'read');

-- Bob Vance (coordinator) -> Sophia Patel ONLY
INSERT INTO public.patient_access_grants (staff_id, patient_id, action) VALUES
    ('7b7c7b68-8c02-4081-a5a3-18b6cdcb26f7', '33333333-3333-3333-3333-333333333333', 'read');

COMMIT;
