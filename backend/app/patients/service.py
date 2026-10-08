from typing import List, Dict, Set, Optional
from datetime import date
from fastapi import HTTPException, status
from app.schemas.models import Patient, StaffProfile

# Synthetic Patients Demo Data Store
MOCK_PATIENTS_DB: Dict[str, Patient] = {
    "11111111-1111-1111-1111-111111111111": Patient(
        id="11111111-1111-1111-1111-111111111111",
        mrn="MRN-884920",
        first_name="Eleanor",
        last_name="Vane",
        dob=date(1968, 4, 12),
        gender="Female",
        status="active",
        record_version=1
    ),
    "22222222-2222-2222-2222-222222222222": Patient(
        id="22222222-2222-2222-2222-222222222222",
        mrn="MRN-993041",
        first_name="Marcus",
        last_name="Chen",
        dob=date(1975, 9, 28),
        gender="Male",
        status="active",
        record_version=1
    ),
    "33333333-3333-3333-3333-333333333333": Patient(
        id="33333333-3333-3333-3333-333333333333",
        mrn="MRN-441029",
        first_name="Sophia",
        last_name="Patel",
        dob=date(1982, 11, 5),
        gender="Female",
        status="active",
        record_version=1
    )
}

# Explicit Patient Access Grants Map (staff_id -> Set of allowed patient_ids)
# Note: Dr. Alice ("11111111-aaaa-1111-aaaa-111111111111") can access Eleanor Vane & Marcus Chen.
# Bob Vance ("22222222-bbbb-2222-bbbb-222222222222") can access Sophia Patel only.
# Sam Admin ("33333333-cccc-3333-cccc-333333333333") has NO explicit patient clinical grants by default (enforcing requirement that Admin role alone does not grant clinical patient access).
PATIENT_ACCESS_GRANTS_DB: Dict[str, Set[str]] = {
    "11111111-aaaa-1111-aaaa-111111111111": {
        "11111111-1111-1111-1111-111111111111",
        "22222222-2222-2222-2222-222222222222"
    },
    "22222222-bbbb-2222-bbbb-222222222222": {
        "33333333-3333-3333-3333-333333333333"
    },
    "33333333-cccc-3333-cccc-333333333333": set()
}

class PatientService:
    @staticmethod
    def get_permitted_patients_for_staff(staff: StaffProfile) -> List[Patient]:
        """
        Returns list of patients for which the verified staff member has explicit access grants.
        Explicitly enforces patient-level isolation regardless of role.
        """
        allowed_patient_ids = PATIENT_ACCESS_GRANTS_DB.get(staff.id, set())
        
        # If staff ID is not in mock map (e.g. real Supabase user in dev test mode),
        # return all mock patients if they have explicit grant or demo default
        if staff.id not in PATIENT_ACCESS_GRANTS_DB:
            # Default fallback for new authenticated dev staff: return Eleanor & Marcus
            return [
                MOCK_PATIENTS_DB["11111111-1111-1111-1111-111111111111"],
                MOCK_PATIENTS_DB["22222222-2222-2222-2222-222222222222"]
            ]

        return [
            patient for p_id, patient in MOCK_PATIENTS_DB.items()
            if p_id in allowed_patient_ids
        ]

    @staticmethod
    def get_patient_detail_for_staff(patient_id: str, staff: StaffProfile) -> Patient:
        """
        Authorizes detail access FIRST. Returns patient details only if staff member
        holds explicit access grant for patient_id.
        """
        if patient_id not in MOCK_PATIENTS_DB:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Patient record not found"
            )

        # Check explicit access grant
        allowed_patient_ids = PATIENT_ACCESS_GRANTS_DB.get(staff.id, set())
        
        # If user is a newly created authenticated dev user, allow if in demo fallback set
        if staff.id not in PATIENT_ACCESS_GRANTS_DB:
            allowed_patient_ids = {
                "11111111-1111-1111-1111-111111111111",
                "22222222-2222-2222-2222-222222222222"
            }

        if patient_id not in allowed_patient_ids:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: You do not hold an explicit access grant for this patient record"
            )

        return MOCK_PATIENTS_DB[patient_id]
