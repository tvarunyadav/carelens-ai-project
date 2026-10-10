-- Seed 003: Synthetic Patient History Records (Documents, Versions, Timeline Events, Fertility Cycles)
-- Executed FIFTH in Supabase SQL Editor

BEGIN;

-- 1. Insert Fertility Cycles
INSERT INTO public.fertility_cycles (id, patient_id, cycle_name, start_date, end_date, status, notes_json)
VALUES ('c1eccbe6-8868-585f-beb8-b910e2daff99', '33333333-3333-3333-3333-333333333333', 'IVF Cycle 1 - Antagonist Ovulation Induction', '2026-05-01', '2026-05-28', 'completed', '{"oocytes_retrieved": 10, "mature": 8, "blastocysts_frozen": 4}'::jsonb)
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.fertility_cycles (id, patient_id, cycle_name, start_date, end_date, status, notes_json)
VALUES ('5e81e667-fa9f-5cb2-a348-8fc4d2ee2283', '33333333-3333-3333-3333-333333333333', 'IVF Cycle 2 - Frozen Embryo Transfer (FET)', '2026-07-10', '2026-09-01', 'completed', '{"embryo_transferred": "Day 5 4AA Blastocyst", "outcome": "Positive Serum Beta-hCG"}'::jsonb)
ON CONFLICT (id) DO NOTHING;

-- 2. Insert Patient Documents & Document Versions
INSERT INTO public.patient_documents (id, patient_id, title, doc_type, clinical_date, status, storage_path, mime_type, file_size, current_version)
VALUES ('8f5e6af6-338e-5d7f-92d7-ba87cf609268', '33333333-3333-3333-3333-333333333333', 'Initial Reproductive Endocrinology Consultation', 'consultation', '2026-04-15', 'final', 'patient-documents/sophia_initial_consult_2026-04-15.pdf', 'application/pdf', 2143, 1)
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.patient_document_versions (document_id, version_number, storage_path, extracted_text, page_count, extraction_status)
VALUES ('8f5e6af6-338e-5d7f-92d7-ba87cf609268', 1, 'patient-documents/sophia_initial_consult_2026-04-15.pdf', 'SYNTHETIC DEMO DATA — NON-PHI MEDICAL RECORD — FOR CARELENS AI DEMO ONLY
Initial Reproductive Endocrinology Consultation
Patient: Sophia Patel MRN: MRN-441029 Date: 2026-04-15
Reason for Visit: Initial evaluation for primary infertility of 18 months duration.
Clinical History: 43-year-old female, gravida 0, para 0. Regular menstrual cycles every 28-30 days.
Assessment & Plan: Order baseline ovarian reserve labs (AMH, FSH, Estradiol), pelvic ultrasound, and HSG.', 1, 'processed')
ON CONFLICT (document_id, version_number) DO NOTHING;
INSERT INTO public.patient_documents (id, patient_id, title, doc_type, clinical_date, status, storage_path, mime_type, file_size, current_version)
VALUES ('895375c0-333c-5d2e-bdf4-dc29897627f1', '33333333-3333-3333-3333-333333333333', 'Baseline Ovarian Reserve & Hormone Panel', 'lab_report', '2026-04-20', 'final', 'patient-documents/sophia_baseline_lab_2026-04-20.pdf', 'application/pdf', 2121, 1)
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.patient_document_versions (document_id, version_number, storage_path, extracted_text, page_count, extraction_status)
VALUES ('895375c0-333c-5d2e-bdf4-dc29897627f1', 1, 'patient-documents/sophia_baseline_lab_2026-04-20.pdf', 'SYNTHETIC DEMO DATA — NON-PHI MEDICAL RECORD — FOR CARELENS AI DEMO ONLY
Baseline Ovarian Reserve & Hormone Panel
Patient: Sophia Patel MRN: MRN-441029 Date: 2026-04-20
Laboratory Results - Cycle Day 3:
Anti-Müllerian Hormone (AMH): 2.8 ng/mL (Reference Range: 1.0 - 3.5 ng/mL - Normal)
Follicle Stimulating Hormone (FSH): 6.2 IU/L (Reference Range: 3.5 - 10.0 IU/L - Normal)
Estradiol (E2): 45 pg/mL (Reference Range: 20 - 80 pg/mL - Normal)
Impression: Normal age-appropriate ovarian reserve parameters.', 1, 'processed')
ON CONFLICT (document_id, version_number) DO NOTHING;
INSERT INTO public.patient_documents (id, patient_id, title, doc_type, clinical_date, status, storage_path, mime_type, file_size, current_version)
VALUES ('b5ef734e-51ae-5869-82eb-13476fe7a99c', '33333333-3333-3333-3333-333333333333', 'Hysterosalpingogram (HSG) Radiology Report', 'radiology', '2026-04-25', 'final', 'patient-documents/sophia_hsg_report_2026-04-25.pdf', 'application/pdf', 2068, 1)
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.patient_document_versions (document_id, version_number, storage_path, extracted_text, page_count, extraction_status)
VALUES ('b5ef734e-51ae-5869-82eb-13476fe7a99c', 1, 'patient-documents/sophia_hsg_report_2026-04-25.pdf', 'SYNTHETIC DEMO DATA — NON-PHI MEDICAL RECORD — FOR CARELENS AI DEMO ONLY
Hysterosalpingogram (HSG) Radiology Report
Patient: Sophia Patel MRN: MRN-441029 Date: 2026-04-25
Contrast Hysterosalpingogram Findings:
Uterine cavity demonstrates normal contour without submucosal fibroids or polyps.
Bilateral fallopian tubes are patent with prompt peritoneal contrast spill.
Impression: Normal patent fallopian tubes bilaterally.', 1, 'processed')
ON CONFLICT (document_id, version_number) DO NOTHING;
INSERT INTO public.patient_documents (id, patient_id, title, doc_type, clinical_date, status, storage_path, mime_type, file_size, current_version)
VALUES ('c0da59bc-7e51-58a6-b19d-28f08613eaa6', '33333333-3333-3333-3333-333333333333', 'Prescription & Stimulation Protocols - IVF Cycle 1', 'medication_record', '2026-05-02', 'final', 'patient-documents/sophia_ivf1_meds_2026-05-02.pdf', 'application/pdf', 2061, 1)
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.patient_document_versions (document_id, version_number, storage_path, extracted_text, page_count, extraction_status)
VALUES ('c0da59bc-7e51-58a6-b19d-28f08613eaa6', 1, 'patient-documents/sophia_ivf1_meds_2026-05-02.pdf', 'SYNTHETIC DEMO DATA — NON-PHI MEDICAL RECORD — FOR CARELENS AI DEMO ONLY
Prescription & Stimulation Protocols - IVF Cycle 1
Patient: Sophia Patel MRN: MRN-441029 Date: 2026-05-02
Controlled Ovarian Hyperstimulation Protocol (Antagonist):
Gonal-F 225 IU subcutaneous daily starting Cycle Day 2 for 9 days.
Menopur 75 IU subcutaneous daily starting Cycle Day 2.
Ganirelix acetate 0.25 mg subcutaneous daily starting Cycle Day 7 once lead follicle reaches 14mm.', 1, 'processed')
ON CONFLICT (document_id, version_number) DO NOTHING;
INSERT INTO public.patient_documents (id, patient_id, title, doc_type, clinical_date, status, storage_path, mime_type, file_size, current_version)
VALUES ('8fc6299f-b3e5-510c-bc6f-edde039c295c', '33333333-3333-3333-3333-333333333333', 'Transvaginal Pelvic Ultrasound & Antral Follicle Count', 'ultrasound', '2026-05-10', 'final', 'patient-documents/sophia_pelvic_us_2026-05-10.pdf', 'application/pdf', 2046, 1)
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.patient_document_versions (document_id, version_number, storage_path, extracted_text, page_count, extraction_status)
VALUES ('8fc6299f-b3e5-510c-bc6f-edde039c295c', 1, 'patient-documents/sophia_pelvic_us_2026-05-10.pdf', 'SYNTHETIC DEMO DATA — NON-PHI MEDICAL RECORD — FOR CARELENS AI DEMO ONLY
Transvaginal Pelvic Ultrasound & Antral Follicle Count
Patient: Sophia Patel MRN: MRN-441029 Date: 2026-05-10
Ultrasound Findings - Stimulation Day 8:
Right Ovary: 7 antral follicles (12mm, 14mm, 15mm, 16mm, 11mm, 10mm, 9mm).
Left Ovary: 6 antral follicles (15mm, 14mm, 13mm, 11mm, 10mm, 8mm).
Endometrial Thickness: 9.4 mm triple-line pattern.', 1, 'processed')
ON CONFLICT (document_id, version_number) DO NOTHING;
INSERT INTO public.patient_documents (id, patient_id, title, doc_type, clinical_date, status, storage_path, mime_type, file_size, current_version)
VALUES ('f62e5fa8-25f2-5ddc-af89-fc8b5dc40b2a', '33333333-3333-3333-3333-333333333333', 'Oocyte Retrieval & Embryology Lab Summary', 'procedure', '2026-05-18', 'final', 'patient-documents/sophia_oocyte_retrieval_2026-05-18.pdf', 'application/pdf', 2077, 1)
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.patient_document_versions (document_id, version_number, storage_path, extracted_text, page_count, extraction_status)
VALUES ('f62e5fa8-25f2-5ddc-af89-fc8b5dc40b2a', 1, 'patient-documents/sophia_oocyte_retrieval_2026-05-18.pdf', 'SYNTHETIC DEMO DATA — NON-PHI MEDICAL RECORD — FOR CARELENS AI DEMO ONLY
Oocyte Retrieval & Embryology Lab Summary
Patient: Sophia Patel MRN: MRN-441029 Date: 2026-05-18
Procedure Summary: Transvaginal ultrasound-guided oocyte retrieval under conscious sedation.
Yield: 10 cumulus-oocyte complexes retrieved.
Embryology Results: 8 MII mature oocytes fertilized via ICSI; 4 high-grade blastocysts vitrified on Day 5.', 1, 'processed')
ON CONFLICT (document_id, version_number) DO NOTHING;
INSERT INTO public.patient_documents (id, patient_id, title, doc_type, clinical_date, status, storage_path, mime_type, file_size, current_version)
VALUES ('19acecf0-f7c9-5b1f-976d-9aae451e7ebd', '33333333-3333-3333-3333-333333333333', 'Frozen Embryo Transfer (FET) Preparation Protocol', 'medication_record', '2026-07-12', 'final', 'patient-documents/sophia_fet_meds_2026-07-12.pdf', 'application/pdf', 2031, 1)
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.patient_document_versions (document_id, version_number, storage_path, extracted_text, page_count, extraction_status)
VALUES ('19acecf0-f7c9-5b1f-976d-9aae451e7ebd', 1, 'patient-documents/sophia_fet_meds_2026-07-12.pdf', 'SYNTHETIC DEMO DATA — NON-PHI MEDICAL RECORD — FOR CARELENS AI DEMO ONLY
Frozen Embryo Transfer (FET) Preparation Protocol
Patient: Sophia Patel MRN: MRN-441029 Date: 2026-07-12
Programmed FET Cycle Medications:
Estradiol valerate (Estrace) 2 mg oral three times daily.
Progesterone in sesame oil 50 mg IM daily starting 5 days prior to planned transfer.', 1, 'processed')
ON CONFLICT (document_id, version_number) DO NOTHING;
INSERT INTO public.patient_documents (id, patient_id, title, doc_type, clinical_date, status, storage_path, mime_type, file_size, current_version)
VALUES ('6baa0540-4c45-599b-855d-ea1a2193a3ab', '33333333-3333-3333-3333-333333333333', 'Karyotype & Chromosomal Microarray Panel (Order Pending)', 'lab_report', '2026-09-15', 'pending', NULL, 'application/pdf', 0, 1)
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.patient_documents (id, patient_id, title, doc_type, clinical_date, status, storage_path, mime_type, file_size, current_version)
VALUES ('cea1f0cb-d9ae-5332-8693-cb545efa2ee6', '11111111-1111-1111-1111-111111111111', 'Annual Wellness & Gynecology Assessment', 'consultation', '2026-03-10', 'final', 'patient-documents/eleanor_annual_exam_2026-03-10.pdf', 'application/pdf', 2088, 1)
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.patient_document_versions (document_id, version_number, storage_path, extracted_text, page_count, extraction_status)
VALUES ('cea1f0cb-d9ae-5332-8693-cb545efa2ee6', 1, 'patient-documents/eleanor_annual_exam_2026-03-10.pdf', 'SYNTHETIC DEMO DATA — NON-PHI MEDICAL RECORD — FOR CARELENS AI DEMO ONLY
Annual Wellness & Gynecology Assessment
Patient: Eleanor Vane MRN: MRN-884920 Date: 2026-03-10
Patient Profile: 58-year-old postmenopausal female presenting for annual preventive gynecologic exam.
History: Menopause at age 52. Mild vasomotor symptoms managed lifestyle.
Plan: Screening mammogram ordered. Routine DEXA bone density scan scheduled.', 1, 'processed')
ON CONFLICT (document_id, version_number) DO NOTHING;
INSERT INTO public.patient_documents (id, patient_id, title, doc_type, clinical_date, status, storage_path, mime_type, file_size, current_version)
VALUES ('dc8ca327-bcca-5cf3-b302-01b4b5b2b7c6', '11111111-1111-1111-1111-111111111111', 'Screening 3D Digital Mammogram', 'ultrasound', '2026-03-15', 'final', 'patient-documents/eleanor_mammogram_2026-03-15.pdf', 'application/pdf', 2029, 1)
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.patient_document_versions (document_id, version_number, storage_path, extracted_text, page_count, extraction_status)
VALUES ('dc8ca327-bcca-5cf3-b302-01b4b5b2b7c6', 1, 'patient-documents/eleanor_mammogram_2026-03-15.pdf', 'SYNTHETIC DEMO DATA — NON-PHI MEDICAL RECORD — FOR CARELENS AI DEMO ONLY
Screening 3D Digital Mammogram
Patient: Eleanor Vane MRN: MRN-884920 Date: 2026-03-15
Bilateral 3D Digital Screening Mammogram:
Findings: Scattered fibroglandular densities (BI-RADS Category 2). No suspicious masses or calcifications.
Recommendation: Routine annual screening in 12 months.', 1, 'processed')
ON CONFLICT (document_id, version_number) DO NOTHING;
INSERT INTO public.patient_documents (id, patient_id, title, doc_type, clinical_date, status, storage_path, mime_type, file_size, current_version)
VALUES ('1a447a6d-80e5-5b58-a457-67858f89421a', '11111111-1111-1111-1111-111111111111', 'Dual-Energy X-Ray Absorptiometry (DEXA) Bone Density', 'radiology', '2026-03-22', 'final', 'patient-documents/eleanor_dexa_scan_2026-03-22.pdf', 'application/pdf', 2058, 1)
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.patient_document_versions (document_id, version_number, storage_path, extracted_text, page_count, extraction_status)
VALUES ('1a447a6d-80e5-5b58-a457-67858f89421a', 1, 'patient-documents/eleanor_dexa_scan_2026-03-22.pdf', 'SYNTHETIC DEMO DATA — NON-PHI MEDICAL RECORD — FOR CARELENS AI DEMO ONLY
Dual-Energy X-Ray Absorptiometry (DEXA) Bone Density
Patient: Eleanor Vane MRN: MRN-884920 Date: 2026-03-22
DEXA Bone Density Scan Results:
Lumbar Spine (L1-L4) T-score: -1.4 (Osteopenia).
Left Femoral Neck T-score: -1.2 (Osteopenia).
Plan: Calcium 1200 mg daily, Vitamin D3 2000 IU daily, weight-bearing exercise.', 1, 'processed')
ON CONFLICT (document_id, version_number) DO NOTHING;
INSERT INTO public.patient_documents (id, patient_id, title, doc_type, clinical_date, status, storage_path, mime_type, file_size, current_version)
VALUES ('3e113271-77f3-5e3e-ad5e-51a94595ebae', '11111111-1111-1111-1111-111111111111', 'Baseline Ovarian Assessment & Ultrasound (v1)', 'lab_report', '2026-04-10', 'final', 'patient-documents/eleanor_amh_v1_2026-04-10.pdf', 'application/pdf', 2024, 1)
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.patient_document_versions (document_id, version_number, storage_path, extracted_text, page_count, extraction_status)
VALUES ('3e113271-77f3-5e3e-ad5e-51a94595ebae', 1, 'patient-documents/eleanor_amh_v1_2026-04-10.pdf', 'SYNTHETIC DEMO DATA — NON-PHI MEDICAL RECORD — FOR CARELENS AI DEMO ONLY
Baseline Ovarian Assessment & Ultrasound (v1)
Patient: Eleanor Vane MRN: MRN-884920 Date: 2026-04-10
Baseline Ovarian Assessment:
Serum AMH Level: 1.8 ng/mL.
Antral Follicle Count (AFC): 11 (Right: 6, Left: 5).
Uterine Cavity: Normal, Endometrium 7.2mm homogenous.', 1, 'processed')
ON CONFLICT (document_id, version_number) DO NOTHING;
INSERT INTO public.patient_documents (id, patient_id, title, doc_type, clinical_date, status, storage_path, mime_type, file_size, current_version)
VALUES ('26216910-8e58-5193-846b-d87ae6c662d4', '11111111-1111-1111-1111-111111111111', 'Amended Baseline Ovarian Assessment (v2 - Conflict Example)', 'lab_report', '2026-04-12', 'final', 'patient-documents/eleanor_amh_v2_conflict_2026-04-12.pdf', 'application/pdf', 2086, 1)
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.patient_document_versions (document_id, version_number, storage_path, extracted_text, page_count, extraction_status)
VALUES ('26216910-8e58-5193-846b-d87ae6c662d4', 1, 'patient-documents/eleanor_amh_v2_conflict_2026-04-12.pdf', 'SYNTHETIC DEMO DATA — NON-PHI MEDICAL RECORD — FOR CARELENS AI DEMO ONLY
Amended Baseline Ovarian Assessment (v2 - Conflict Example)
Patient: Eleanor Vane MRN: MRN-884920 Date: 2026-04-12
Amended Clinical Report (v2):
Serum AMH Level: 1.2 ng/mL (Re-tested / Recalibrated value).
Antral Follicle Count (AFC): 9 (Right: 5, Left: 4).
Note: Supersedes preliminary report dated 2026-04-10 due to analyzer recalibration.', 1, 'processed')
ON CONFLICT (document_id, version_number) DO NOTHING;
INSERT INTO public.patient_documents (id, patient_id, title, doc_type, clinical_date, status, storage_path, mime_type, file_size, current_version)
VALUES ('2316a25f-7180-5d3a-9640-cab2af425621', '11111111-1111-1111-1111-111111111111', 'Screening Colonoscopy (Order Pending)', 'procedure', '2026-09-01', 'pending', NULL, 'application/pdf', 0, 1)
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.patient_documents (id, patient_id, title, doc_type, clinical_date, status, storage_path, mime_type, file_size, current_version)
VALUES ('7f586f70-9c7d-55b8-9c7e-871924c06736', '22222222-2222-2222-2222-222222222222', 'Cardiology Consultation & Lipid Profile', 'consultation', '2026-06-18', 'final', 'patient-documents/marcus_cardiology_consult_2026-06-18.pdf', 'application/pdf', 2106, 1)
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.patient_document_versions (document_id, version_number, storage_path, extracted_text, page_count, extraction_status)
VALUES ('7f586f70-9c7d-55b8-9c7e-871924c06736', 1, 'patient-documents/marcus_cardiology_consult_2026-06-18.pdf', 'SYNTHETIC DEMO DATA — NON-PHI MEDICAL RECORD — FOR CARELENS AI DEMO ONLY
Cardiology Consultation & Lipid Profile
Patient: Marcus Chen MRN: MRN-993041 Date: 2026-06-18
Reason for Visit: Cardiovascular risk assessment and hyperlipidemia management.
Vitals: BP 124/78 mmHg, HR 68 bpm. Lipid Panel: Total Cholesterol 215 mg/dL, LDL 138 mg/dL, HDL 48
mg/dL.
Plan: Continue Atorvastatin 10 mg daily. Mediterranean diet and aerobic exercise.', 1, 'processed')
ON CONFLICT (document_id, version_number) DO NOTHING;
INSERT INTO public.patient_documents (id, patient_id, title, doc_type, clinical_date, status, storage_path, mime_type, file_size, current_version)
VALUES ('24f8837d-f0b4-5ee3-ac9a-1da1e38d0421', '22222222-2222-2222-2222-222222222222', '12-Lead Resting Electrocardiogram (EKG)', 'lab_report', '2026-06-20', 'final', 'patient-documents/marcus_ekg_report_2026-06-20.pdf', 'application/pdf', 2007, 1)
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.patient_document_versions (document_id, version_number, storage_path, extracted_text, page_count, extraction_status)
VALUES ('24f8837d-f0b4-5ee3-ac9a-1da1e38d0421', 1, 'patient-documents/marcus_ekg_report_2026-06-20.pdf', 'SYNTHETIC DEMO DATA — NON-PHI MEDICAL RECORD — FOR CARELENS AI DEMO ONLY
12-Lead Resting Electrocardiogram (EKG)
Patient: Marcus Chen MRN: MRN-993041 Date: 2026-06-20
12-Lead EKG Interpretation:
Normal sinus rhythm at 66 bpm. Normal axis, PR interval 152 ms, QRS 88 ms, QTc 412 ms.
No ST-segment elevation or ST-T wave abnormalities.', 1, 'processed')
ON CONFLICT (document_id, version_number) DO NOTHING;
INSERT INTO public.patient_documents (id, patient_id, title, doc_type, clinical_date, status, storage_path, mime_type, file_size, current_version)
VALUES ('084cfb01-799f-57cb-b957-e7d5ae2a469d', '22222222-2222-2222-2222-222222222222', 'Carotid Artery Duplex Ultrasound', 'ultrasound', '2026-07-05', 'final', 'patient-documents/marcus_carotid_us_2026-07-05.pdf', 'application/pdf', 2034, 1)
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.patient_document_versions (document_id, version_number, storage_path, extracted_text, page_count, extraction_status)
VALUES ('084cfb01-799f-57cb-b957-e7d5ae2a469d', 1, 'patient-documents/marcus_carotid_us_2026-07-05.pdf', 'SYNTHETIC DEMO DATA — NON-PHI MEDICAL RECORD — FOR CARELENS AI DEMO ONLY
Carotid Artery Duplex Ultrasound
Patient: Marcus Chen MRN: MRN-993041 Date: 2026-07-05
Carotid Ultrasound Findings:
Bilateral carotid arteries demonstrate minimal intimal thickening (<20% stenosis).
Normal peak systolic velocities bilaterally. Antegrade vertebral flow.', 1, 'processed')
ON CONFLICT (document_id, version_number) DO NOTHING;
INSERT INTO public.patient_documents (id, patient_id, title, doc_type, clinical_date, status, storage_path, mime_type, file_size, current_version)
VALUES ('3ec41607-1472-5bb8-8d97-b08caa8a9cb1', '22222222-2222-2222-2222-222222222222', 'Repeat Lipid & Liver Function Panel', 'lab_report', '2026-09-10', 'final', 'patient-documents/marcus_lipid_followup_2026-09-10.pdf', 'application/pdf', 2011, 1)
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.patient_document_versions (document_id, version_number, storage_path, extracted_text, page_count, extraction_status)
VALUES ('3ec41607-1472-5bb8-8d97-b08caa8a9cb1', 1, 'patient-documents/marcus_lipid_followup_2026-09-10.pdf', 'SYNTHETIC DEMO DATA — NON-PHI MEDICAL RECORD — FOR CARELENS AI DEMO ONLY
Repeat Lipid & Liver Function Panel
Patient: Marcus Chen MRN: MRN-993041 Date: 2026-09-10
Repeat Blood Chemistry Results:
LDL Cholesterol: 92 mg/dL (Target achieved <100 mg/dL).
ALT: 22 U/L, AST: 19 U/L (Normal liver enzymes).', 1, 'processed')
ON CONFLICT (document_id, version_number) DO NOTHING;
INSERT INTO public.patient_documents (id, patient_id, title, doc_type, clinical_date, status, storage_path, mime_type, file_size, current_version)
VALUES ('5100402b-be93-5e44-8629-9bba03d9fa4d', '22222222-2222-2222-2222-222222222222', 'Exercise Stress Echocardiogram', 'procedure', '2026-09-22', 'final', 'patient-documents/marcus_stress_test_2026-09-22.pdf', 'application/pdf', 2009, 1)
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.patient_document_versions (document_id, version_number, storage_path, extracted_text, page_count, extraction_status)
VALUES ('5100402b-be93-5e44-8629-9bba03d9fa4d', 1, 'patient-documents/marcus_stress_test_2026-09-22.pdf', 'SYNTHETIC DEMO DATA — NON-PHI MEDICAL RECORD — FOR CARELENS AI DEMO ONLY
Exercise Stress Echocardiogram
Patient: Marcus Chen MRN: MRN-993041 Date: 2026-09-22
Treadmill Exercise Stress Test:
Exercised 10 minutes 30 seconds (11.5 METs). Reached 94% predicted max heart rate.
No inducible ischemia or wall motion abnormalities noted.', 1, 'processed')
ON CONFLICT (document_id, version_number) DO NOTHING;
INSERT INTO public.patient_documents (id, patient_id, title, doc_type, clinical_date, status, storage_path, mime_type, file_size, current_version)
VALUES ('3b47721c-eced-5a5c-a204-297038e9bbfb', '22222222-2222-2222-2222-222222222222', 'Coronary Artery Calcium (CAC) CT Scan (Pending)', 'radiology', '2026-10-01', 'pending', NULL, 'application/pdf', 0, 1)
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.patient_documents (id, patient_id, title, doc_type, clinical_date, status, storage_path, mime_type, file_size, current_version)
VALUES ('a7de7c7e-ec61-5964-a12d-d28bbf9ab18c', '44444444-4444-4444-4444-444444444444', 'Endocrine Consultation for PCOS & Cycle Irregularity', 'consultation', '2026-02-14', 'final', 'patient-documents/priya_pcos_consult_2026-02-14.pdf', 'application/pdf', 2081, 1)
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.patient_document_versions (document_id, version_number, storage_path, extracted_text, page_count, extraction_status)
VALUES ('a7de7c7e-ec61-5964-a12d-d28bbf9ab18c', 1, 'patient-documents/priya_pcos_consult_2026-02-14.pdf', 'SYNTHETIC DEMO DATA — NON-PHI MEDICAL RECORD — FOR CARELENS AI DEMO ONLY
Endocrine Consultation for PCOS & Cycle Irregularity
Patient: Priya Sharma MRN: MRN-104928 Date: 2026-02-14
Clinical Presentation: 37-year-old female presenting with oligomenorrhea and acne.
Diagnosis: Polycystic Ovary Syndrome (PCOS) based on Rotterdam criteria.
Plan: Metformin ER 500 mg daily with dinner. Lifestyle management.', 1, 'processed')
ON CONFLICT (document_id, version_number) DO NOTHING;
INSERT INTO public.patient_documents (id, patient_id, title, doc_type, clinical_date, status, storage_path, mime_type, file_size, current_version)
VALUES ('24af8997-69b8-5764-ab3c-68d27dee7722', '44444444-4444-4444-4444-444444444444', 'Fasting Glucose & HbA1c Laboratory Report', 'lab_report', '2026-02-20', 'final', 'patient-documents/priya_glucose_panel_2026-02-20.pdf', 'application/pdf', 2001, 1)
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.patient_document_versions (document_id, version_number, storage_path, extracted_text, page_count, extraction_status)
VALUES ('24af8997-69b8-5764-ab3c-68d27dee7722', 1, 'patient-documents/priya_glucose_panel_2026-02-20.pdf', 'SYNTHETIC DEMO DATA — NON-PHI MEDICAL RECORD — FOR CARELENS AI DEMO ONLY
Fasting Glucose & HbA1c Laboratory Report
Patient: Priya Sharma MRN: MRN-104928 Date: 2026-02-20
Fasting Plasma Glucose: 98 mg/dL (Normal <100 mg/dL).
Hemoglobin A1c: 5.6% (Normal <5.7%).
Fasting Insulin: 14.2 uIU/mL (Mild insulin resistance).', 1, 'processed')
ON CONFLICT (document_id, version_number) DO NOTHING;
INSERT INTO public.patient_documents (id, patient_id, title, doc_type, clinical_date, status, storage_path, mime_type, file_size, current_version)
VALUES ('b07feccc-9760-5f64-9881-5e30c2f9c682', '44444444-4444-4444-4444-444444444444', 'Pelvic Ultrasound - Polycystic Ovarian Morphology', 'ultrasound', '2026-03-05', 'final', 'patient-documents/priya_pelvic_ultrasound_2026-03-05.pdf', 'application/pdf', 2064, 1)
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.patient_document_versions (document_id, version_number, storage_path, extracted_text, page_count, extraction_status)
VALUES ('b07feccc-9760-5f64-9881-5e30c2f9c682', 1, 'patient-documents/priya_pelvic_ultrasound_2026-03-05.pdf', 'SYNTHETIC DEMO DATA — NON-PHI MEDICAL RECORD — FOR CARELENS AI DEMO ONLY
Pelvic Ultrasound - Polycystic Ovarian Morphology
Patient: Priya Sharma MRN: MRN-104928 Date: 2026-03-05
Transvaginal Ultrasound Findings:
Bilateral enlarged ovaries (Right 12.4 mL, Left 11.8 mL) with >12 peripheral follicles bilaterally (''string of
pearls'').
Endometrium: 6.8 mm, homogeneous.', 1, 'processed')
ON CONFLICT (document_id, version_number) DO NOTHING;
INSERT INTO public.patient_documents (id, patient_id, title, doc_type, clinical_date, status, storage_path, mime_type, file_size, current_version)
VALUES ('36febc98-cb0b-5d1b-b1ff-b990265fab2f', '44444444-4444-4444-4444-444444444444', 'Comprehensive Serum Androgen Panel', 'lab_report', '2026-03-12', 'final', 'patient-documents/priya_androgen_panel_2026-03-12.pdf', 'application/pdf', 1996, 1)
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.patient_document_versions (document_id, version_number, storage_path, extracted_text, page_count, extraction_status)
VALUES ('36febc98-cb0b-5d1b-b1ff-b990265fab2f', 1, 'patient-documents/priya_androgen_panel_2026-03-12.pdf', 'SYNTHETIC DEMO DATA — NON-PHI MEDICAL RECORD — FOR CARELENS AI DEMO ONLY
Comprehensive Serum Androgen Panel
Patient: Priya Sharma MRN: MRN-104928 Date: 2026-03-12
Laboratory Results:
Total Testosterone: 64 ng/dL (Elevated, Ref 15 - 45 ng/dL).
Free Testosterone: 8.2 pg/mL (Elevated).
DHEA-S: 240 ug/dL (Normal).', 1, 'processed')
ON CONFLICT (document_id, version_number) DO NOTHING;
INSERT INTO public.patient_documents (id, patient_id, title, doc_type, clinical_date, status, storage_path, mime_type, file_size, current_version)
VALUES ('a4f4b8ab-c128-59e1-8755-a64222279109', '44444444-4444-4444-4444-444444444444', 'Ovulation Induction Prescription - Letrozole', 'medication_record', '2026-04-01', 'final', 'patient-documents/priya_letrozole_presc_2026-04-01.pdf', 'application/pdf', 2002, 1)
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.patient_document_versions (document_id, version_number, storage_path, extracted_text, page_count, extraction_status)
VALUES ('a4f4b8ab-c128-59e1-8755-a64222279109', 1, 'patient-documents/priya_letrozole_presc_2026-04-01.pdf', 'SYNTHETIC DEMO DATA — NON-PHI MEDICAL RECORD — FOR CARELENS AI DEMO ONLY
Ovulation Induction Prescription - Letrozole
Patient: Priya Sharma MRN: MRN-104928 Date: 2026-04-01
Prescription & Protocol:
Letrozole (Femara) 2.5 mg oral daily on Cycle Days 3-7.
Timed intercourse protocol with LH surge monitoring.', 1, 'processed')
ON CONFLICT (document_id, version_number) DO NOTHING;
INSERT INTO public.patient_documents (id, patient_id, title, doc_type, clinical_date, status, storage_path, mime_type, file_size, current_version)
VALUES ('a12f5d50-bd12-565e-a22e-528df2c8d279', '44444444-4444-4444-4444-444444444444', 'Day 21 Serum Progesterone (Order Pending)', 'lab_report', '2026-04-22', 'pending', NULL, 'application/pdf', 0, 1)
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.patient_documents (id, patient_id, title, doc_type, clinical_date, status, storage_path, mime_type, file_size, current_version)
VALUES ('4bc6d1e1-1450-5e99-af01-0aa5ab42ec30', '55555555-5555-5555-5555-555555555555', 'Male Reproductive Health & Andrology Evaluation', 'consultation', '2026-05-10', 'final', 'patient-documents/david_andrology_eval_2026-05-10.pdf', 'application/pdf', 2041, 1)
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.patient_document_versions (document_id, version_number, storage_path, extracted_text, page_count, extraction_status)
VALUES ('4bc6d1e1-1450-5e99-af01-0aa5ab42ec30', 1, 'patient-documents/david_andrology_eval_2026-05-10.pdf', 'SYNTHETIC DEMO DATA — NON-PHI MEDICAL RECORD — FOR CARELENS AI DEMO ONLY
Male Reproductive Health & Andrology Evaluation
Patient: David Kim MRN: MRN-552914 Date: 2026-05-10
Evaluation: 46-year-old male evaluated for couple infertility.
Semen Analysis: Concentration 42 M/mL, Motility 58% progressive, Normal Morphology 4%.
Impression: Normal semen parameters. No male factor infertility.', 1, 'processed')
ON CONFLICT (document_id, version_number) DO NOTHING;
INSERT INTO public.patient_documents (id, patient_id, title, doc_type, clinical_date, status, storage_path, mime_type, file_size, current_version)
VALUES ('0f010ce9-e812-5862-aa29-90e606473ea5', '55555555-5555-5555-5555-555555555555', 'Male Hormone & Endocrine Panel', 'lab_report', '2026-05-15', 'final', 'patient-documents/david_hormone_panel_2026-05-15.pdf', 'application/pdf', 2039, 1)
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.patient_document_versions (document_id, version_number, storage_path, extracted_text, page_count, extraction_status)
VALUES ('0f010ce9-e812-5862-aa29-90e606473ea5', 1, 'patient-documents/david_hormone_panel_2026-05-15.pdf', 'SYNTHETIC DEMO DATA — NON-PHI MEDICAL RECORD — FOR CARELENS AI DEMO ONLY
Male Hormone & Endocrine Panel
Patient: David Kim MRN: MRN-552914 Date: 2026-05-15
Male Endocrine Lab Results:
Serum Testosterone: 520 ng/dL (Normal range 300 - 1000 ng/dL).
FSH: 4.1 IU/L, LH: 3.8 IU/L, Prolactin: 8.4 ng/mL.
Impression: Normal hypothalamic-pituitary-gonadal axis.', 1, 'processed')
ON CONFLICT (document_id, version_number) DO NOTHING;
INSERT INTO public.patient_documents (id, patient_id, title, doc_type, clinical_date, status, storage_path, mime_type, file_size, current_version)
VALUES ('adb1e704-c2bc-5024-9ea4-dc473bdf1668', '55555555-5555-5555-5555-555555555555', 'Scrotal Duplex Ultrasound', 'ultrasound', '2026-05-28', 'final', 'patient-documents/david_scrotal_us_2026-05-28.pdf', 'application/pdf', 2003, 1)
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.patient_document_versions (document_id, version_number, storage_path, extracted_text, page_count, extraction_status)
VALUES ('adb1e704-c2bc-5024-9ea4-dc473bdf1668', 1, 'patient-documents/david_scrotal_us_2026-05-28.pdf', 'SYNTHETIC DEMO DATA — NON-PHI MEDICAL RECORD — FOR CARELENS AI DEMO ONLY
Scrotal Duplex Ultrasound
Patient: David Kim MRN: MRN-552914 Date: 2026-05-28
Scrotal Ultrasound Findings:
Bilateral testes normal volume and echotexture. No testicular masses.
Grade I left subclinical varicocele without retrograde flow on Valsalva.', 1, 'processed')
ON CONFLICT (document_id, version_number) DO NOTHING;
INSERT INTO public.patient_documents (id, patient_id, title, doc_type, clinical_date, status, storage_path, mime_type, file_size, current_version)
VALUES ('331eb917-be9b-5cdf-995a-453b70033d74', '55555555-5555-5555-5555-555555555555', 'Sperm DNA Fragmentation Index (DFI) Test', 'lab_report', '2026-06-12', 'final', 'patient-documents/david_dna_frag_2026-06-12.pdf', 'application/pdf', 2006, 1)
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.patient_document_versions (document_id, version_number, storage_path, extracted_text, page_count, extraction_status)
VALUES ('331eb917-be9b-5cdf-995a-453b70033d74', 1, 'patient-documents/david_dna_frag_2026-06-12.pdf', 'SYNTHETIC DEMO DATA — NON-PHI MEDICAL RECORD — FOR CARELENS AI DEMO ONLY
Sperm DNA Fragmentation Index (DFI) Test
Patient: David Kim MRN: MRN-552914 Date: 2026-06-12
Sperm Chromatin Structure Assay (SCSA):
DNA Fragmentation Index (DFI): 12% (Excellent fertility potential <15%).
High Stainable DNA (HSD): 4%.', 1, 'processed')
ON CONFLICT (document_id, version_number) DO NOTHING;
INSERT INTO public.patient_documents (id, patient_id, title, doc_type, clinical_date, status, storage_path, mime_type, file_size, current_version)
VALUES ('e3c877e6-9b8a-5183-9724-b1726b5285e5', '55555555-5555-5555-5555-555555555555', 'Annual Executive Health Physical', 'consultation', '2026-08-01', 'final', 'patient-documents/david_wellness_exam_2026-08-01.pdf', 'application/pdf', 2032, 1)
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.patient_document_versions (document_id, version_number, storage_path, extracted_text, page_count, extraction_status)
VALUES ('e3c877e6-9b8a-5183-9724-b1726b5285e5', 1, 'patient-documents/david_wellness_exam_2026-08-01.pdf', 'SYNTHETIC DEMO DATA — NON-PHI MEDICAL RECORD — FOR CARELENS AI DEMO ONLY
Annual Executive Health Physical
Patient: David Kim MRN: MRN-552914 Date: 2026-08-01
Physical Exam: Vital signs stable, BMI 24.2 kg/m2.
Routine Screening: Complete Blood Count, Metabolic Panel, Lipid Panel normal.
Plan: Continue active lifestyle and annual preventive checkups.', 1, 'processed')
ON CONFLICT (document_id, version_number) DO NOTHING;
INSERT INTO public.patient_documents (id, patient_id, title, doc_type, clinical_date, status, storage_path, mime_type, file_size, current_version)
VALUES ('c2e51d72-333b-5404-ae7d-8bcd1aabc417', '55555555-5555-5555-5555-555555555555', 'Y-Chromosome Microdeletion Assay (Pending)', 'lab_report', '2026-09-10', 'pending', NULL, 'application/pdf', 0, 1)
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.patient_documents (id, patient_id, title, doc_type, clinical_date, status, storage_path, mime_type, file_size, current_version)
VALUES ('3fa8c198-f48a-57ec-b008-757d5d5217b8', '66666666-6666-6666-6666-666666666666', 'First Trimester Obstetrics Consultation & Ultrasound', 'consultation', '2026-01-22', 'final', 'patient-documents/hannah_first_trimester_2026-01-22.pdf', 'application/pdf', 2073, 1)
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.patient_document_versions (document_id, version_number, storage_path, extracted_text, page_count, extraction_status)
VALUES ('3fa8c198-f48a-57ec-b008-757d5d5217b8', 1, 'patient-documents/hannah_first_trimester_2026-01-22.pdf', 'SYNTHETIC DEMO DATA — NON-PHI MEDICAL RECORD — FOR CARELENS AI DEMO ONLY
First Trimester Obstetrics Consultation & Ultrasound
Patient: Hannah Abbott MRN: MRN-663819 Date: 2026-01-22
OB Consultation: 35-year-old G1P0 at 8 weeks 4 days estimated gestational age.
Ultrasound: Single live intrauterine pregnancy with cardiac activity 164 bpm. CRL 2.1 cm.
Plan: Initiate prenatal vitamins, folic acid 1 mg daily.', 1, 'processed')
ON CONFLICT (document_id, version_number) DO NOTHING;
INSERT INTO public.patient_documents (id, patient_id, title, doc_type, clinical_date, status, storage_path, mime_type, file_size, current_version)
VALUES ('57c5f5e6-95ec-5329-881b-ef8e3ba23e56', '66666666-6666-6666-6666-666666666666', 'Non-Invasive Prenatal Testing (NIPT) Screen', 'lab_report', '2026-02-10', 'final', 'patient-documents/hannah_nipt_screening_2026-02-10.pdf', 'application/pdf', 2032, 1)
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.patient_document_versions (document_id, version_number, storage_path, extracted_text, page_count, extraction_status)
VALUES ('57c5f5e6-95ec-5329-881b-ef8e3ba23e56', 1, 'patient-documents/hannah_nipt_screening_2026-02-10.pdf', 'SYNTHETIC DEMO DATA — NON-PHI MEDICAL RECORD — FOR CARELENS AI DEMO ONLY
Non-Invasive Prenatal Testing (NIPT) Screen
Patient: Hannah Abbott MRN: MRN-663819 Date: 2026-02-10
Cell-Free Fetal DNA NIPT Panel:
Trisomy 21 (Down Syndrome): Low Risk (<1 in 10,000).
Trisomy 18 & 13: Low Risk.
Fetal Sex: Female. Fetal Fraction: 8.4%.', 1, 'processed')
ON CONFLICT (document_id, version_number) DO NOTHING;
INSERT INTO public.patient_documents (id, patient_id, title, doc_type, clinical_date, status, storage_path, mime_type, file_size, current_version)
VALUES ('25a76a85-43fd-5c9d-b22d-4ae279dea4dd', '66666666-6666-6666-6666-666666666666', 'Second Trimester Fetal Anatomy Ultrasound', 'ultrasound', '2026-04-18', 'final', 'patient-documents/hannah_anatomy_scan_2026-04-18.pdf', 'application/pdf', 2044, 1)
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.patient_document_versions (document_id, version_number, storage_path, extracted_text, page_count, extraction_status)
VALUES ('25a76a85-43fd-5c9d-b22d-4ae279dea4dd', 1, 'patient-documents/hannah_anatomy_scan_2026-04-18.pdf', 'SYNTHETIC DEMO DATA — NON-PHI MEDICAL RECORD — FOR CARELENS AI DEMO ONLY
Second Trimester Fetal Anatomy Ultrasound
Patient: Hannah Abbott MRN: MRN-663819 Date: 2026-04-18
20-Week Fetal Anatomy Ultrasound:
Normal fetal anatomical survey (brain, spine, cardiac 4-chamber view, kidneys, stomach).
Estimated Fetal Weight: 340g (52nd percentile). Placenta anterior, clear of os.', 1, 'processed')
ON CONFLICT (document_id, version_number) DO NOTHING;
INSERT INTO public.patient_documents (id, patient_id, title, doc_type, clinical_date, status, storage_path, mime_type, file_size, current_version)
VALUES ('f34aa832-cbc2-535d-9da2-310aa12ba268', '66666666-6666-6666-6666-666666666666', '1-Hour Oral Glucose Tolerance Test (OGTT)', 'lab_report', '2026-05-25', 'final', 'patient-documents/hannah_glucose_challenge_2026-05-25.pdf', 'application/pdf', 2002, 1)
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.patient_document_versions (document_id, version_number, storage_path, extracted_text, page_count, extraction_status)
VALUES ('f34aa832-cbc2-535d-9da2-310aa12ba268', 1, 'patient-documents/hannah_glucose_challenge_2026-05-25.pdf', 'SYNTHETIC DEMO DATA — NON-PHI MEDICAL RECORD — FOR CARELENS AI DEMO ONLY
1-Hour Oral Glucose Tolerance Test (OGTT)
Patient: Hannah Abbott MRN: MRN-663819 Date: 2026-05-25
1-Hour 50g Glucose Challenge Test:
Serum Glucose: 118 mg/dL (Normal <140 mg/dL).
Impression: Negative screen for gestational diabetes.', 1, 'processed')
ON CONFLICT (document_id, version_number) DO NOTHING;
INSERT INTO public.patient_documents (id, patient_id, title, doc_type, clinical_date, status, storage_path, mime_type, file_size, current_version)
VALUES ('b199b566-b88b-5b26-ae6e-1cede86e64d5', '66666666-6666-6666-6666-666666666666', 'Antibody Screen & Rh Factor Report', 'lab_report', '2026-06-01', 'final', 'patient-documents/hannah_rh_antibody_2026-06-01.pdf', 'application/pdf', 1951, 1)
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.patient_document_versions (document_id, version_number, storage_path, extracted_text, page_count, extraction_status)
VALUES ('b199b566-b88b-5b26-ae6e-1cede86e64d5', 1, 'patient-documents/hannah_rh_antibody_2026-06-01.pdf', 'SYNTHETIC DEMO DATA — NON-PHI MEDICAL RECORD — FOR CARELENS AI DEMO ONLY
Antibody Screen & Rh Factor Report
Patient: Hannah Abbott MRN: MRN-663819 Date: 2026-06-01
Blood Typing & Antibody Screen:
Blood Type: A Positive (Rh D Positive).
Atypical Antibody Screen: Negative.', 1, 'processed')
ON CONFLICT (document_id, version_number) DO NOTHING;
INSERT INTO public.patient_documents (id, patient_id, title, doc_type, clinical_date, status, storage_path, mime_type, file_size, current_version)
VALUES ('895364ec-6b73-5344-a879-f6bf86c09bc4', '66666666-6666-6666-6666-666666666666', 'Group B Streptococcus (GBS) Culture (Pending)', 'lab_report', '2026-09-01', 'pending', NULL, 'application/pdf', 0, 1)
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.patient_documents (id, patient_id, title, doc_type, clinical_date, status, storage_path, mime_type, file_size, current_version)
VALUES ('ea91cb26-b709-5b1f-b12f-efef9f3087b9', '77777777-7777-7777-7777-777777777777', 'Urology Consult & Renal Ultrasound Summary', 'consultation', '2026-04-05', 'final', 'patient-documents/carlos_urology_consult_2026-04-05.pdf', 'application/pdf', 2051, 1)
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.patient_document_versions (document_id, version_number, storage_path, extracted_text, page_count, extraction_status)
VALUES ('ea91cb26-b709-5b1f-b12f-efef9f3087b9', 1, 'patient-documents/carlos_urology_consult_2026-04-05.pdf', 'SYNTHETIC DEMO DATA — NON-PHI MEDICAL RECORD — FOR CARELENS AI DEMO ONLY
Urology Consult & Renal Ultrasound Summary
Patient: Carlos Rodriguez MRN: MRN-771829 Date: 2026-04-05
Reason for Visit: Left flank discomfort.
Renal Ultrasound: 4mm non-obstructing calculus in left lower pole. No hydronephrosis.
Plan: Conservative management, aggressive oral hydration, strain urine.', 1, 'processed')
ON CONFLICT (document_id, version_number) DO NOTHING;
INSERT INTO public.patient_documents (id, patient_id, title, doc_type, clinical_date, status, storage_path, mime_type, file_size, current_version)
VALUES ('45ff8d1b-3b45-5248-9886-0fd39e1010bc', '77777777-7777-7777-7777-777777777777', 'Urinalysis & Microscopic Exam Report', 'lab_report', '2026-04-06', 'final', 'patient-documents/carlos_urinalysis_2026-04-06.pdf', 'application/pdf', 2042, 1)
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.patient_document_versions (document_id, version_number, storage_path, extracted_text, page_count, extraction_status)
VALUES ('45ff8d1b-3b45-5248-9886-0fd39e1010bc', 1, 'patient-documents/carlos_urinalysis_2026-04-06.pdf', 'SYNTHETIC DEMO DATA — NON-PHI MEDICAL RECORD — FOR CARELENS AI DEMO ONLY
Urinalysis & Microscopic Exam Report
Patient: Carlos Rodriguez MRN: MRN-771829 Date: 2026-04-06
Urinalysis Findings:
Microscopic Hematuria: 5-10 RBC/HPF (Ref 0-2).
Leukocyte Esterase: Negative, Nitrites: Negative, pH: 6.0.
Impression: Microscopic hematuria consistent with renal calculus passage.', 1, 'processed')
ON CONFLICT (document_id, version_number) DO NOTHING;
INSERT INTO public.patient_documents (id, patient_id, title, doc_type, clinical_date, status, storage_path, mime_type, file_size, current_version)
VALUES ('848def71-fd7b-5180-a425-9f9ab1f978e4', '77777777-7777-7777-7777-777777777777', 'Non-Contrast CT Abdomen & Pelvis (KUB)', 'radiology', '2026-04-12', 'final', 'patient-documents/carlos_ct_kud_2026-04-12.pdf', 'application/pdf', 1986, 1)
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.patient_document_versions (document_id, version_number, storage_path, extracted_text, page_count, extraction_status)
VALUES ('848def71-fd7b-5180-a425-9f9ab1f978e4', 1, 'patient-documents/carlos_ct_kud_2026-04-12.pdf', 'SYNTHETIC DEMO DATA — NON-PHI MEDICAL RECORD — FOR CARELENS AI DEMO ONLY
Non-Contrast CT Abdomen & Pelvis (KUB)
Patient: Carlos Rodriguez MRN: MRN-771829 Date: 2026-04-12
CT KUB Findings:
3.8mm calculus located in distal left ureterovesical junction.
Mild left ureterohydronephrosis.', 1, 'processed')
ON CONFLICT (document_id, version_number) DO NOTHING;
INSERT INTO public.patient_documents (id, patient_id, title, doc_type, clinical_date, status, storage_path, mime_type, file_size, current_version)
VALUES ('73200609-2274-51f0-b173-21a821174b47', '77777777-7777-7777-7777-777777777777', 'Urology Follow-up & Stone Clearance Check', 'consultation', '2026-04-26', 'final', 'patient-documents/carlos_flank_followup_2026-04-26.pdf', 'application/pdf', 2049, 1)
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.patient_document_versions (document_id, version_number, storage_path, extracted_text, page_count, extraction_status)
VALUES ('73200609-2274-51f0-b173-21a821174b47', 1, 'patient-documents/carlos_flank_followup_2026-04-26.pdf', 'SYNTHETIC DEMO DATA — NON-PHI MEDICAL RECORD — FOR CARELENS AI DEMO ONLY
Urology Follow-up & Stone Clearance Check
Patient: Carlos Rodriguez MRN: MRN-771829 Date: 2026-04-26
Follow-up Visit:
Patient reports complete resolution of flank pain after passing small stone fragment.
Repeat Renal Ultrasound: No residual left renal or ureteral calculi. Resolved hydronephrosis.', 1, 'processed')
ON CONFLICT (document_id, version_number) DO NOTHING;
INSERT INTO public.patient_documents (id, patient_id, title, doc_type, clinical_date, status, storage_path, mime_type, file_size, current_version)
VALUES ('4df2f29e-990a-50fb-83e0-df3e0846155f', '77777777-7777-7777-7777-777777777777', '24-Hour Urine Metabolic Stone Risk Panel', 'lab_report', '2026-06-15', 'final', 'patient-documents/carlos_metabolic_stone_2026-06-15.pdf', 'application/pdf', 1993, 1)
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.patient_document_versions (document_id, version_number, storage_path, extracted_text, page_count, extraction_status)
VALUES ('4df2f29e-990a-50fb-83e0-df3e0846155f', 1, 'patient-documents/carlos_metabolic_stone_2026-06-15.pdf', 'SYNTHETIC DEMO DATA — NON-PHI MEDICAL RECORD — FOR CARELENS AI DEMO ONLY
24-Hour Urine Metabolic Stone Risk Panel
Patient: Carlos Rodriguez MRN: MRN-771829 Date: 2026-06-15
24-Hour Urine Panel:
Urine Volume: 1.8 L/day (Goal >2.5 L). Calcium: 260 mg/day (Mild hypercalciuria).
Citrate: 450 mg/day (Normal). Oxalate: 32 mg/day (Normal).', 1, 'processed')
ON CONFLICT (document_id, version_number) DO NOTHING;
INSERT INTO public.patient_documents (id, patient_id, title, doc_type, clinical_date, status, storage_path, mime_type, file_size, current_version)
VALUES ('4305d7ce-f14f-5cdf-a058-8251339417e3', '77777777-7777-7777-7777-777777777777', 'Calculus Composition Analysis (Pending)', 'lab_report', '2026-08-01', 'pending', NULL, 'application/pdf', 0, 1)
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.patient_documents (id, patient_id, title, doc_type, clinical_date, status, storage_path, mime_type, file_size, current_version)
VALUES ('86d0cb3b-b4d6-5bc4-b96b-26509c548578', '88888888-8888-8888-8888-888888888888', 'Thyroid Function & Autoantibody Panel', 'lab_report', '2026-03-01', 'final', 'patient-documents/aisha_thyroid_panel_2026-03-01.pdf', 'application/pdf', 2092, 1)
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.patient_document_versions (document_id, version_number, storage_path, extracted_text, page_count, extraction_status)
VALUES ('86d0cb3b-b4d6-5bc4-b96b-26509c548578', 1, 'patient-documents/aisha_thyroid_panel_2026-03-01.pdf', 'SYNTHETIC DEMO DATA — NON-PHI MEDICAL RECORD — FOR CARELENS AI DEMO ONLY
Thyroid Function & Autoantibody Panel
Patient: Aisha Khan MRN: MRN-882941 Date: 2026-03-01
Thyroid Panel Results:
TSH: 4.8 mIU/L (Elevated, Ref 0.4 - 4.0 mIU/L).
Free T4: 1.1 ng/dL (Normal).
Anti-TPO Antibodies: Positive (145 IU/mL).
Plan: Subclinical hypothyroidism secondary to Hashimoto''s. Start Levothyroxine 50 mcg daily.', 1, 'processed')
ON CONFLICT (document_id, version_number) DO NOTHING;
INSERT INTO public.patient_documents (id, patient_id, title, doc_type, clinical_date, status, storage_path, mime_type, file_size, current_version)
VALUES ('6d2768e2-4d48-50e5-b824-e8afe5f860d0', '88888888-8888-8888-8888-888888888888', 'Thyroid Ultrasound & Nodule Survey', 'ultrasound', '2026-03-10', 'final', 'patient-documents/aisha_thyroid_us_2026-03-10.pdf', 'application/pdf', 2014, 1)
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.patient_document_versions (document_id, version_number, storage_path, extracted_text, page_count, extraction_status)
VALUES ('6d2768e2-4d48-50e5-b824-e8afe5f860d0', 1, 'patient-documents/aisha_thyroid_us_2026-03-10.pdf', 'SYNTHETIC DEMO DATA — NON-PHI MEDICAL RECORD — FOR CARELENS AI DEMO ONLY
Thyroid Ultrasound & Nodule Survey
Patient: Aisha Khan MRN: MRN-882941 Date: 2026-03-10
Thyroid Ultrasound Findings:
Diffuse heterogeneous echotexture characteristic of chronic autoimmune thyroiditis.
No focal thyroid nodules >1cm identified. Normal vascular flow.', 1, 'processed')
ON CONFLICT (document_id, version_number) DO NOTHING;
INSERT INTO public.patient_documents (id, patient_id, title, doc_type, clinical_date, status, storage_path, mime_type, file_size, current_version)
VALUES ('78027725-9646-5cf2-a9e9-2d1a54ebc620', '88888888-8888-8888-8888-888888888888', '6-Week TSH & Free T4 Follow-up Report (v1)', 'lab_report', '2026-04-15', 'final', 'patient-documents/aisha_tsh_followup_v1_2026-04-15.pdf', 'application/pdf', 2011, 1)
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.patient_document_versions (document_id, version_number, storage_path, extracted_text, page_count, extraction_status)
VALUES ('78027725-9646-5cf2-a9e9-2d1a54ebc620', 1, 'patient-documents/aisha_tsh_followup_v1_2026-04-15.pdf', 'SYNTHETIC DEMO DATA — NON-PHI MEDICAL RECORD — FOR CARELENS AI DEMO ONLY
6-Week TSH & Free T4 Follow-up Report (v1)
Patient: Aisha Khan MRN: MRN-882941 Date: 2026-04-15
Repeat Thyroid Panel (v1):
TSH: 2.4 mIU/L (Normal target achieved).
Free T4: 1.3 ng/dL (Normal).
Plan: Maintain Levothyroxine 50 mcg daily.', 1, 'processed')
ON CONFLICT (document_id, version_number) DO NOTHING;
INSERT INTO public.patient_documents (id, patient_id, title, doc_type, clinical_date, status, storage_path, mime_type, file_size, current_version)
VALUES ('7c215bdb-9cb0-57aa-8430-e90cb5616afd', '88888888-8888-8888-8888-888888888888', 'Amended TSH Follow-up Report (v2 - Conflict Example)', 'lab_report', '2026-04-17', 'final', 'patient-documents/aisha_tsh_followup_v2_conflict_2026-04-17.pdf', 'application/pdf', 2038, 1)
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.patient_document_versions (document_id, version_number, storage_path, extracted_text, page_count, extraction_status)
VALUES ('7c215bdb-9cb0-57aa-8430-e90cb5616afd', 1, 'patient-documents/aisha_tsh_followup_v2_conflict_2026-04-17.pdf', 'SYNTHETIC DEMO DATA — NON-PHI MEDICAL RECORD — FOR CARELENS AI DEMO ONLY
Amended TSH Follow-up Report (v2 - Conflict Example)
Patient: Aisha Khan MRN: MRN-882941 Date: 2026-04-17
Amended Thyroid Panel (v2):
TSH: 3.1 mIU/L (Re-assayed value).
Free T4: 1.2 ng/dL.
Note: Lab re-run requested by endocrinology due to baseline reagent lot shift.', 1, 'processed')
ON CONFLICT (document_id, version_number) DO NOTHING;
INSERT INTO public.patient_documents (id, patient_id, title, doc_type, clinical_date, status, storage_path, mime_type, file_size, current_version)
VALUES ('ec4dcdf4-8910-50fd-95e2-c408c749af41', '88888888-8888-8888-8888-888888888888', 'Serum 25-Hydroxy Vitamin D Level', 'lab_report', '2026-06-05', 'final', 'patient-documents/aisha_vit_d_level_2026-06-05.pdf', 'application/pdf', 1984, 1)
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.patient_document_versions (document_id, version_number, storage_path, extracted_text, page_count, extraction_status)
VALUES ('ec4dcdf4-8910-50fd-95e2-c408c749af41', 1, 'patient-documents/aisha_vit_d_level_2026-06-05.pdf', 'SYNTHETIC DEMO DATA — NON-PHI MEDICAL RECORD — FOR CARELENS AI DEMO ONLY
Serum 25-Hydroxy Vitamin D Level
Patient: Aisha Khan MRN: MRN-882941 Date: 2026-06-05
Serum 25-OH Vitamin D:
Result: 22 ng/mL (Deficient <30 ng/mL).
Plan: Ergocalciferol (Vitamin D2) 50,000 IU weekly for 8 weeks.', 1, 'processed')
ON CONFLICT (document_id, version_number) DO NOTHING;
INSERT INTO public.patient_documents (id, patient_id, title, doc_type, clinical_date, status, storage_path, mime_type, file_size, current_version)
VALUES ('7fb00b76-89ba-513d-b169-c9aa3d1e4501', '88888888-8888-8888-8888-888888888888', '6-Month Repeat TSH & Vitamin D (Pending)', 'lab_report', '2026-10-01', 'pending', NULL, 'application/pdf', 0, 1)
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.patient_documents (id, patient_id, title, doc_type, clinical_date, status, storage_path, mime_type, file_size, current_version)
VALUES ('3c6d5c25-8a44-5d75-ada2-62fdc2d0a554', '99999999-9999-9999-9999-999999999999', 'Orthopedic Knee Consultation & MRI Report', 'consultation', '2026-07-02', 'final', 'patient-documents/james_ortho_consult_2026-07-02.pdf', 'application/pdf', 2072, 1)
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.patient_document_versions (document_id, version_number, storage_path, extracted_text, page_count, extraction_status)
VALUES ('3c6d5c25-8a44-5d75-ada2-62fdc2d0a554', 1, 'patient-documents/james_ortho_consult_2026-07-02.pdf', 'SYNTHETIC DEMO DATA — NON-PHI MEDICAL RECORD — FOR CARELENS AI DEMO ONLY
Orthopedic Knee Consultation & MRI Report
Patient: James Wilson MRN: MRN-994812 Date: 2026-07-02
Right Knee Evaluation: 47-year-old male with persistent right knee joint pain.
MRI Findings: Grade II medial meniscus oblique tear. Intact ACL and PCL.
Plan: Physical therapy twice weekly for 6 weeks, NSAIDs as needed.', 1, 'processed')
ON CONFLICT (document_id, version_number) DO NOTHING;
INSERT INTO public.patient_documents (id, patient_id, title, doc_type, clinical_date, status, storage_path, mime_type, file_size, current_version)
VALUES ('cadeb2b9-b4db-5cb9-8e17-8851496c6299', '99999999-9999-9999-9999-999999999999', 'Weight-Bearing Right Knee Radiographs', 'radiology', '2026-07-03', 'final', 'patient-documents/james_knee_xray_2026-07-03.pdf', 'application/pdf', 1983, 1)
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.patient_document_versions (document_id, version_number, storage_path, extracted_text, page_count, extraction_status)
VALUES ('cadeb2b9-b4db-5cb9-8e17-8851496c6299', 1, 'patient-documents/james_knee_xray_2026-07-03.pdf', 'SYNTHETIC DEMO DATA — NON-PHI MEDICAL RECORD — FOR CARELENS AI DEMO ONLY
Weight-Bearing Right Knee Radiographs
Patient: James Wilson MRN: MRN-994812 Date: 2026-07-03
Right Knee X-Ray (3 Views):
Mild medial compartment joint space narrowing.
No acute cortical fractures or dislocation.', 1, 'processed')
ON CONFLICT (document_id, version_number) DO NOTHING;
INSERT INTO public.patient_documents (id, patient_id, title, doc_type, clinical_date, status, storage_path, mime_type, file_size, current_version)
VALUES ('88ce8635-64c0-527f-8429-672061490cde', '99999999-9999-9999-9999-999999999999', 'Physical Therapy Initial Evaluation', 'consultation', '2026-07-10', 'final', 'patient-documents/james_pt_eval_2026-07-10.pdf', 'application/pdf', 2009, 1)
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.patient_document_versions (document_id, version_number, storage_path, extracted_text, page_count, extraction_status)
VALUES ('88ce8635-64c0-527f-8429-672061490cde', 1, 'patient-documents/james_pt_eval_2026-07-10.pdf', 'SYNTHETIC DEMO DATA — NON-PHI MEDICAL RECORD — FOR CARELENS AI DEMO ONLY
Physical Therapy Initial Evaluation
Patient: James Wilson MRN: MRN-994812 Date: 2026-07-10
PT Evaluation Notes:
Right knee ROM: Flexion 115 degrees, Extension 0 degrees. Mild joint effusion.
Goals: Restore full ROM to 130 deg flexion, quadriceps strengthening.', 1, 'processed')
ON CONFLICT (document_id, version_number) DO NOTHING;
INSERT INTO public.patient_documents (id, patient_id, title, doc_type, clinical_date, status, storage_path, mime_type, file_size, current_version)
VALUES ('2cb34e8a-bfa1-5b22-be2c-6d3cbef0211e', '99999999-9999-9999-9999-999999999999', 'Physical Therapy Discharge Summary', 'consultation', '2026-08-22', 'final', 'patient-documents/james_pt_discharge_2026-08-22.pdf', 'application/pdf', 2036, 1)
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.patient_document_versions (document_id, version_number, storage_path, extracted_text, page_count, extraction_status)
VALUES ('2cb34e8a-bfa1-5b22-be2c-6d3cbef0211e', 1, 'patient-documents/james_pt_discharge_2026-08-22.pdf', 'SYNTHETIC DEMO DATA — NON-PHI MEDICAL RECORD — FOR CARELENS AI DEMO ONLY
Physical Therapy Discharge Summary
Patient: James Wilson MRN: MRN-994812 Date: 2026-08-22
PT Discharge Assessment:
Completed 12 sessions. Right knee ROM: Flexion 132 degrees, full pain-free extension.
Outcome: Able to resume light jogging without pain. Home exercise program provided.', 1, 'processed')
ON CONFLICT (document_id, version_number) DO NOTHING;
INSERT INTO public.patient_documents (id, patient_id, title, doc_type, clinical_date, status, storage_path, mime_type, file_size, current_version)
VALUES ('1e3a7cc9-b278-5ab3-ad43-8d80bcfbd84d', '99999999-9999-9999-9999-999999999999', 'Intra-Articular Hyaluronic Acid Injection', 'procedure', '2026-09-15', 'final', 'patient-documents/james_hyaluronic_inj_2026-09-15.pdf', 'application/pdf', 2037, 1)
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.patient_document_versions (document_id, version_number, storage_path, extracted_text, page_count, extraction_status)
VALUES ('1e3a7cc9-b278-5ab3-ad43-8d80bcfbd84d', 1, 'patient-documents/james_hyaluronic_inj_2026-09-15.pdf', 'SYNTHETIC DEMO DATA — NON-PHI MEDICAL RECORD — FOR CARELENS AI DEMO ONLY
Intra-Articular Hyaluronic Acid Injection
Patient: James Wilson MRN: MRN-994812 Date: 2026-09-15
Procedure Summary:
Right knee intra-articular injection of High Molecular Weight Hyaluronan (Synvisc-One 6 mL).
Procedure performed under sterile technique with ultrasound guidance without complication.', 1, 'processed')
ON CONFLICT (document_id, version_number) DO NOTHING;
INSERT INTO public.patient_documents (id, patient_id, title, doc_type, clinical_date, status, storage_path, mime_type, file_size, current_version)
VALUES ('2453e767-81ef-536d-bd2c-e326df7986c7', '99999999-9999-9999-9999-999999999999', '6-Month Follow-up Knee MRI (Pending)', 'radiology', '2026-10-02', 'pending', NULL, 'application/pdf', 0, 1)
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.patient_documents (id, patient_id, title, doc_type, clinical_date, status, storage_path, mime_type, file_size, current_version)
VALUES ('4febb6dc-7d9a-52db-8acc-ae1e7262316a', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', 'Dermatology Skin Examination & Biopsy Summary', 'consultation', '2026-08-11', 'final', 'patient-documents/maya_dermatology_exam_2026-08-11.pdf', 'application/pdf', 2066, 1)
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.patient_document_versions (document_id, version_number, storage_path, extracted_text, page_count, extraction_status)
VALUES ('4febb6dc-7d9a-52db-8acc-ae1e7262316a', 1, 'patient-documents/maya_dermatology_exam_2026-08-11.pdf', 'SYNTHETIC DEMO DATA — NON-PHI MEDICAL RECORD — FOR CARELENS AI DEMO ONLY
Dermatology Skin Examination & Biopsy Summary
Patient: Maya Lin MRN: MRN-109283 Date: 2026-08-11
Skin Exam: 40-year-old female for routine full-body cutaneous examination.
Biopsy Result (Right forearm lesion): Seborrheic keratosis, benign. No dysplastic features.
Plan: Reassurance provided. Re-evaluate annually.', 1, 'processed')
ON CONFLICT (document_id, version_number) DO NOTHING;
INSERT INTO public.patient_documents (id, patient_id, title, doc_type, clinical_date, status, storage_path, mime_type, file_size, current_version)
VALUES ('c020ab79-72d9-5247-a429-44642943dc72', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', 'Histopathology Biopsy Pathology Report', 'lab_report', '2026-08-15', 'final', 'patient-documents/maya_derm_pathology_2026-08-15.pdf', 'application/pdf', 2028, 1)
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.patient_document_versions (document_id, version_number, storage_path, extracted_text, page_count, extraction_status)
VALUES ('c020ab79-72d9-5247-a429-44642943dc72', 1, 'patient-documents/maya_derm_pathology_2026-08-15.pdf', 'SYNTHETIC DEMO DATA — NON-PHI MEDICAL RECORD — FOR CARELENS AI DEMO ONLY
Histopathology Biopsy Pathology Report
Patient: Maya Lin MRN: MRN-109283 Date: 2026-08-15
Surgical Pathology Report:
Specimen: 3mm punch biopsy right forearm lesion.
Microscopic Description: Hyperkeratosis, acanthosis, and intraepidermal horn cysts.
Diagnosis: Benign Seborrheic Keratosis.', 1, 'processed')
ON CONFLICT (document_id, version_number) DO NOTHING;
INSERT INTO public.patient_documents (id, patient_id, title, doc_type, clinical_date, status, storage_path, mime_type, file_size, current_version)
VALUES ('11b9d2f1-80db-59b5-b3f4-bd3340f14d0b', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', 'Routine Annual Comprehensive Blood Panel', 'lab_report', '2026-08-20', 'final', 'patient-documents/maya_annual_blood_2026-08-20.pdf', 'application/pdf', 2037, 1)
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.patient_document_versions (document_id, version_number, storage_path, extracted_text, page_count, extraction_status)
VALUES ('11b9d2f1-80db-59b5-b3f4-bd3340f14d0b', 1, 'patient-documents/maya_annual_blood_2026-08-20.pdf', 'SYNTHETIC DEMO DATA — NON-PHI MEDICAL RECORD — FOR CARELENS AI DEMO ONLY
Routine Annual Comprehensive Blood Panel
Patient: Maya Lin MRN: MRN-109283 Date: 2026-08-20
Annual Lab Panel Results:
CBC: WBC 6.2 k/uL, Hemoglobin 13.4 g/dL, Platelets 245 k/uL.
CMP: Sodium 140 mEq/L, Potassium 4.2 mEq/L, Creatinine 0.75 mg/dL.
Lipid Panel: Total Cholesterol 175 mg/dL, LDL 98 mg/dL.', 1, 'processed')
ON CONFLICT (document_id, version_number) DO NOTHING;
INSERT INTO public.patient_documents (id, patient_id, title, doc_type, clinical_date, status, storage_path, mime_type, file_size, current_version)
VALUES ('93bbea5f-fca1-50ab-8c59-7b5cd624c1f2', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', 'Allergy & Environmental Sensitization Evaluation', 'consultation', '2026-09-02', 'final', 'patient-documents/maya_allergy_eval_2026-09-02.pdf', 'application/pdf', 2072, 1)
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.patient_document_versions (document_id, version_number, storage_path, extracted_text, page_count, extraction_status)
VALUES ('93bbea5f-fca1-50ab-8c59-7b5cd624c1f2', 1, 'patient-documents/maya_allergy_eval_2026-09-02.pdf', 'SYNTHETIC DEMO DATA — NON-PHI MEDICAL RECORD — FOR CARELENS AI DEMO ONLY
Allergy & Environmental Sensitization Evaluation
Patient: Maya Lin MRN: MRN-109283 Date: 2026-09-02
Allergy Evaluation:
History: Seasonal allergic rhinitis in spring months.
Skin Prick Test: Positive reaction to Timothy grass and birch pollen. Negative to dust mites.
Plan: Fluticasone propionate nasal spray 50 mcg/actuation daily.', 1, 'processed')
ON CONFLICT (document_id, version_number) DO NOTHING;
INSERT INTO public.patient_documents (id, patient_id, title, doc_type, clinical_date, status, storage_path, mime_type, file_size, current_version)
VALUES ('e5ab39d6-712b-5e4b-8184-0bacb4a485bf', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', 'Comprehensive Ophthalmic & Vision Exam', 'consultation', '2026-09-18', 'final', 'patient-documents/maya_optometry_exam_2026-09-18.pdf', 'application/pdf', 2009, 1)
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.patient_document_versions (document_id, version_number, storage_path, extracted_text, page_count, extraction_status)
VALUES ('e5ab39d6-712b-5e4b-8184-0bacb4a485bf', 1, 'patient-documents/maya_optometry_exam_2026-09-18.pdf', 'SYNTHETIC DEMO DATA — NON-PHI MEDICAL RECORD — FOR CARELENS AI DEMO ONLY
Comprehensive Ophthalmic & Vision Exam
Patient: Maya Lin MRN: MRN-109283 Date: 2026-09-18
Vision Exam Findings:
Visual Acuity: 20/20 OD, 20/20 OS with mild refractive correction.
Intraocular Pressure: 14 mmHg OD, 15 mmHg OS (Normal). Slit lamp exam clear.', 1, 'processed')
ON CONFLICT (document_id, version_number) DO NOTHING;
INSERT INTO public.patient_documents (id, patient_id, title, doc_type, clinical_date, status, storage_path, mime_type, file_size, current_version)
VALUES ('691881f5-fbdc-5080-a673-7e60d1395e1a', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', 'Serum Total IgE & Specific Allergen Panel (Pending)', 'lab_report', '2026-10-01', 'pending', NULL, 'application/pdf', 0, 1)
ON CONFLICT (id) DO NOTHING;

-- 3. Insert Patient Timeline Events
INSERT INTO public.patient_timeline_events (id, patient_id, event_date, event_type, title, summary, document_id)
VALUES ('56fb1931-519a-564b-918b-4b9c5ec5425e', '33333333-3333-3333-3333-333333333333', '2026-04-15', 'visit', 'Initial Reproductive Endocrinology Consultation', 'Comprehensive fertility evaluation initiated. Baseline labs ordered.', '8f5e6af6-338e-5d7f-92d7-ba87cf609268')
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.patient_timeline_events (id, patient_id, event_date, event_type, title, summary, document_id)
VALUES ('aacf7af0-9b52-5a6b-aa6b-98fb8ca88e7b', '33333333-3333-3333-3333-333333333333', '2026-04-20', 'lab_result', 'Baseline Ovarian Reserve & Hormone Panel', 'AMH 2.8 ng/mL, Day 3 FSH 6.2 IU/L. Normal ovarian reserve.', '895375c0-333c-5d2e-bdf4-dc29897627f1')
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.patient_timeline_events (id, patient_id, event_date, event_type, title, summary, document_id)
VALUES ('3cdbb159-a8b0-55e9-81c7-db9ba2da7991', '33333333-3333-3333-3333-333333333333', '2026-04-25', 'procedure', 'Hysterosalpingogram (HSG) Radiology Report', 'HSG shows bilateral fallopian tube patency and normal uterine contour.', 'b5ef734e-51ae-5869-82eb-13476fe7a99c')
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.patient_timeline_events (id, patient_id, event_date, event_type, title, summary, document_id)
VALUES ('001b1ad4-a66b-5d97-b767-b31f356e8910', '33333333-3333-3333-3333-333333333333', '2026-05-02', 'medication', 'Prescription & Stimulation Protocols - IVF Cycle 1', 'Prescribed Gonal-F 225 IU, Menopur 75 IU, Ganirelix antagonist protocol.', 'c0da59bc-7e51-58a6-b19d-28f08613eaa6')
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.patient_timeline_events (id, patient_id, event_date, event_type, title, summary, document_id)
VALUES ('cfec80f7-973a-5eda-9b9b-9bc8926a38a6', '33333333-3333-3333-3333-333333333333', '2026-05-10', 'procedure', 'Transvaginal Pelvic Ultrasound & Antral Follicle Count', '13 growing follicles (lead follicles 16mm R, 15mm L). Endometrium 9.4mm.', '8fc6299f-b3e5-510c-bc6f-edde039c295c')
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.patient_timeline_events (id, patient_id, event_date, event_type, title, summary, document_id)
VALUES ('3b004d22-c641-5205-96fd-80e6f4fdacd7', '33333333-3333-3333-3333-333333333333', '2026-05-18', 'procedure', 'Oocyte Retrieval & Embryology Lab Summary', '10 oocytes retrieved, 8 mature fertilized via ICSI, 4 Day-5 blastocysts vitrified.', 'f62e5fa8-25f2-5ddc-af89-fc8b5dc40b2a')
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.patient_timeline_events (id, patient_id, event_date, event_type, title, summary, document_id)
VALUES ('63635c16-6c5b-516c-b8e2-c79bb723c79c', '33333333-3333-3333-3333-333333333333', '2026-07-12', 'medication', 'Frozen Embryo Transfer (FET) Preparation Protocol', 'Initiated Estrace 2mg TID and IM Progesterone in preparation for embryo transfer.', '19acecf0-f7c9-5b1f-976d-9aae451e7ebd')
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.patient_timeline_events (id, patient_id, event_date, event_type, title, summary, document_id)
VALUES ('b4b7e0f5-d9b1-5887-a06c-efdfe30b2768', '33333333-3333-3333-3333-333333333333', '2026-09-15', 'lab_result', 'Karyotype & Chromosomal Microarray Panel (Order Pending)', 'High-resolution blood karyotype requested. Lab processing underway (Result not recorded).', '6baa0540-4c45-599b-855d-ea1a2193a3ab')
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.patient_timeline_events (id, patient_id, event_date, event_type, title, summary, document_id)
VALUES ('9f4c3d23-5bdc-5063-af2c-7275ba8f3223', '11111111-1111-1111-1111-111111111111', '2026-03-10', 'visit', 'Annual Wellness & Gynecology Assessment', 'Routine postmenopausal checkup. Preventive mammogram ordered.', 'cea1f0cb-d9ae-5332-8693-cb545efa2ee6')
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.patient_timeline_events (id, patient_id, event_date, event_type, title, summary, document_id)
VALUES ('b1253563-caf7-5797-8169-9efb09a2fcb1', '11111111-1111-1111-1111-111111111111', '2026-03-15', 'procedure', 'Screening 3D Digital Mammogram', 'BI-RADS 2 - Benign findings. Annual screening recommended.', 'dc8ca327-bcca-5cf3-b302-01b4b5b2b7c6')
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.patient_timeline_events (id, patient_id, event_date, event_type, title, summary, document_id)
VALUES ('5e2d1849-7f55-5805-9ec5-3e6c3422af30', '11111111-1111-1111-1111-111111111111', '2026-03-22', 'procedure', 'Dual-Energy X-Ray Absorptiometry (DEXA) Bone Density', 'DEXA scan demonstrates mild osteopenia (T-score -1.4). Calcium & Vitamin D recommended.', '1a447a6d-80e5-5b58-a457-67858f89421a')
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.patient_timeline_events (id, patient_id, event_date, event_type, title, summary, document_id)
VALUES ('df8bce96-849f-5e9c-b726-70cb1695689d', '11111111-1111-1111-1111-111111111111', '2026-04-10', 'lab_result', 'Baseline Ovarian Assessment & Ultrasound (v1)', 'Baseline AMH 1.8 ng/mL, AFC 11. Uterine cavity normal.', '3e113271-77f3-5e3e-ad5e-51a94595ebae')
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.patient_timeline_events (id, patient_id, event_date, event_type, title, summary, document_id)
VALUES ('a8eaa802-ade4-536d-86b0-57e78478df9c', '11111111-1111-1111-1111-111111111111', '2026-04-12', 'lab_result', 'Amended Baseline Ovarian Assessment (v2 - Conflict Example)', 'Amended AMH 1.2 ng/mL (Recalibrated). Discrepancy flagged for review.', '26216910-8e58-5193-846b-d87ae6c662d4')
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.patient_timeline_events (id, patient_id, event_date, event_type, title, summary, document_id)
VALUES ('c5049b76-75f2-5213-a175-e8ab796b55f8', '11111111-1111-1111-1111-111111111111', '2026-09-01', 'procedure', 'Screening Colonoscopy (Order Pending)', 'Screening colonoscopy requested for age 58. Procedure scheduled (Result not recorded).', '2316a25f-7180-5d3a-9640-cab2af425621')
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.patient_timeline_events (id, patient_id, event_date, event_type, title, summary, document_id)
VALUES ('760cc627-d330-50cb-a381-5758a9d1d8ff', '22222222-2222-2222-2222-222222222222', '2026-06-18', 'visit', 'Cardiology Consultation & Lipid Profile', 'LDL 138 mg/dL. Prescribed Atorvastatin 10mg daily.', '7f586f70-9c7d-55b8-9c7e-871924c06736')
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.patient_timeline_events (id, patient_id, event_date, event_type, title, summary, document_id)
VALUES ('eedc97dd-3650-577d-b533-a195e058f3c6', '22222222-2222-2222-2222-222222222222', '2026-06-20', 'procedure', '12-Lead Resting Electrocardiogram (EKG)', '12-lead EKG shows normal sinus rhythm without ischemia.', '24f8837d-f0b4-5ee3-ac9a-1da1e38d0421')
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.patient_timeline_events (id, patient_id, event_date, event_type, title, summary, document_id)
VALUES ('d0ae7283-b415-5dd5-ae71-129a69392d16', '22222222-2222-2222-2222-222222222222', '2026-07-05', 'procedure', 'Carotid Artery Duplex Ultrasound', 'Minimal carotid intimal thickening (<20% stenosis). Normal flow.', '084cfb01-799f-57cb-b957-e7d5ae2a469d')
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.patient_timeline_events (id, patient_id, event_date, event_type, title, summary, document_id)
VALUES ('51da5458-d6d6-526a-ab48-f45f7649bd26', '22222222-2222-2222-2222-222222222222', '2026-09-10', 'lab_result', 'Repeat Lipid & Liver Function Panel', 'LDL reduced to 92 mg/dL on Atorvastatin 10mg. Liver enzymes normal.', '3ec41607-1472-5bb8-8d97-b08caa8a9cb1')
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.patient_timeline_events (id, patient_id, event_date, event_type, title, summary, document_id)
VALUES ('66c038cb-a874-5b09-a6cf-1fe6e3e17949', '22222222-2222-2222-2222-222222222222', '2026-09-22', 'procedure', 'Exercise Stress Echocardiogram', 'Normal stress echocardiogram (11.5 METs, no ischemia).', '5100402b-be93-5e44-8629-9bba03d9fa4d')
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.patient_timeline_events (id, patient_id, event_date, event_type, title, summary, document_id)
VALUES ('d2b1f3b3-ceea-542f-9de9-a28dc1ffb2ab', '22222222-2222-2222-2222-222222222222', '2026-10-01', 'procedure', 'Coronary Artery Calcium (CAC) CT Scan (Pending)', 'CAC CT scan ordered for calcium scoring (Result not recorded).', '3b47721c-eced-5a5c-a204-297038e9bbfb')
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.patient_timeline_events (id, patient_id, event_date, event_type, title, summary, document_id)
VALUES ('f75452cd-8a11-5cd3-99d2-4fccb21f46ae', '44444444-4444-4444-4444-444444444444', '2026-02-14', 'visit', 'Endocrine Consultation for PCOS & Cycle Irregularity', 'PCOS diagnosed. Metformin ER 500mg initiated.', 'a7de7c7e-ec61-5964-a12d-d28bbf9ab18c')
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.patient_timeline_events (id, patient_id, event_date, event_type, title, summary, document_id)
VALUES ('89a69734-3276-5672-b661-519dbe2488ba', '44444444-4444-4444-4444-444444444444', '2026-02-20', 'lab_result', 'Fasting Glucose & HbA1c Laboratory Report', 'HbA1c 5.6%, Fasting Glucose 98 mg/dL.', '24af8997-69b8-5764-ab3c-68d27dee7722')
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.patient_timeline_events (id, patient_id, event_date, event_type, title, summary, document_id)
VALUES ('e90d3e1b-df96-53ce-aedc-2c1de4bd26ba', '44444444-4444-4444-4444-444444444444', '2026-03-05', 'procedure', 'Pelvic Ultrasound - Polycystic Ovarian Morphology', 'Ultrasound confirms polycystic ovarian morphology bilaterally.', 'b07feccc-9760-5f64-9881-5e30c2f9c682')
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.patient_timeline_events (id, patient_id, event_date, event_type, title, summary, document_id)
VALUES ('12fa539d-26ad-5a39-bc66-c1878a0b37b5', '44444444-4444-4444-4444-444444444444', '2026-03-12', 'lab_result', 'Comprehensive Serum Androgen Panel', 'Elevated serum testosterone (64 ng/dL) consistent with hyperandrogenism.', '36febc98-cb0b-5d1b-b1ff-b990265fab2f')
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.patient_timeline_events (id, patient_id, event_date, event_type, title, summary, document_id)
VALUES ('60e09ed5-8dca-5aff-a4ca-813c3363fdc9', '44444444-4444-4444-4444-444444444444', '2026-04-01', 'medication', 'Ovulation Induction Prescription - Letrozole', 'Prescribed Letrozole 2.5mg daily for ovulation induction.', 'a4f4b8ab-c128-59e1-8755-a64222279109')
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.patient_timeline_events (id, patient_id, event_date, event_type, title, summary, document_id)
VALUES ('5c4179e4-dc06-5026-b0e8-398da1a80fd7', '44444444-4444-4444-4444-444444444444', '2026-04-22', 'lab_result', 'Day 21 Serum Progesterone (Order Pending)', 'Day 21 progesterone ordered to confirm ovulation (Result not recorded).', 'a12f5d50-bd12-565e-a22e-528df2c8d279')
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.patient_timeline_events (id, patient_id, event_date, event_type, title, summary, document_id)
VALUES ('9c77f5b5-68f3-5dc1-afee-936c0f18cb05', '55555555-5555-5555-5555-555555555555', '2026-05-10', 'visit', 'Male Reproductive Health & Andrology Evaluation', 'Semen analysis normal (42M/mL, 58% motility).', '4bc6d1e1-1450-5e99-af01-0aa5ab42ec30')
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.patient_timeline_events (id, patient_id, event_date, event_type, title, summary, document_id)
VALUES ('dbbaaca1-044d-51ea-956e-e6b5ab73c2dd', '55555555-5555-5555-5555-555555555555', '2026-05-15', 'lab_result', 'Male Hormone & Endocrine Panel', 'Serum testosterone 520 ng/dL, normal gonadotropins.', '0f010ce9-e812-5862-aa29-90e606473ea5')
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.patient_timeline_events (id, patient_id, event_date, event_type, title, summary, document_id)
VALUES ('003a5638-8f51-5b88-8df9-7e7eadf45e3a', '55555555-5555-5555-5555-555555555555', '2026-05-28', 'procedure', 'Scrotal Duplex Ultrasound', 'Scrotal ultrasound shows subclinical Grade I left varicocele.', 'adb1e704-c2bc-5024-9ea4-dc473bdf1668')
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.patient_timeline_events (id, patient_id, event_date, event_type, title, summary, document_id)
VALUES ('fc9d0a86-b021-554b-9984-35b01cbb7047', '55555555-5555-5555-5555-555555555555', '2026-06-12', 'lab_result', 'Sperm DNA Fragmentation Index (DFI) Test', 'Sperm DFI 12% - Excellent sperm DNA integrity.', '331eb917-be9b-5cdf-995a-453b70033d74')
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.patient_timeline_events (id, patient_id, event_date, event_type, title, summary, document_id)
VALUES ('572a7c6b-c824-55f6-8b67-b9c126359b79', '55555555-5555-5555-5555-555555555555', '2026-08-01', 'visit', 'Annual Executive Health Physical', 'Annual physical normal. Metabolic & hematologic panels clear.', 'e3c877e6-9b8a-5183-9724-b1726b5285e5')
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.patient_timeline_events (id, patient_id, event_date, event_type, title, summary, document_id)
VALUES ('702eab98-4353-586b-8433-187ae29093ed', '55555555-5555-5555-5555-555555555555', '2026-09-10', 'lab_result', 'Y-Chromosome Microdeletion Assay (Pending)', 'Y-chromosome microdeletion screen requested (Result not recorded).', 'c2e51d72-333b-5404-ae7d-8bcd1aabc417')
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.patient_timeline_events (id, patient_id, event_date, event_type, title, summary, document_id)
VALUES ('62653704-7bdf-59f6-be63-400dd398a23e', '66666666-6666-6666-6666-666666666666', '2026-01-22', 'visit', 'First Trimester Obstetrics Consultation & Ultrasound', '8w4d intrauterine pregnancy confirmed with HR 164 bpm.', '3fa8c198-f48a-57ec-b008-757d5d5217b8')
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.patient_timeline_events (id, patient_id, event_date, event_type, title, summary, document_id)
VALUES ('57ca5fa2-76db-536a-be1a-263b11ef110c', '66666666-6666-6666-6666-666666666666', '2026-02-10', 'lab_result', 'Non-Invasive Prenatal Testing (NIPT) Screen', 'NIPT low risk for Trisomies 21, 18, and 13. Fetal fraction 8.4%.', '57c5f5e6-95ec-5329-881b-ef8e3ba23e56')
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.patient_timeline_events (id, patient_id, event_date, event_type, title, summary, document_id)
VALUES ('11b9c175-16ad-5ae5-a95d-56e6d9b822a1', '66666666-6666-6666-6666-666666666666', '2026-04-18', 'procedure', 'Second Trimester Fetal Anatomy Ultrasound', '20-week fetal anatomy ultrasound normal. EFW 340g (52nd percentile).', '25a76a85-43fd-5c9d-b22d-4ae279dea4dd')
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.patient_timeline_events (id, patient_id, event_date, event_type, title, summary, document_id)
VALUES ('05b83722-1583-53b4-a572-49701388c6a3', '66666666-6666-6666-6666-666666666666', '2026-05-25', 'lab_result', '1-Hour Oral Glucose Tolerance Test (OGTT)', '1-hour OGTT 118 mg/dL - Negative for gestational diabetes.', 'f34aa832-cbc2-535d-9da2-310aa12ba268')
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.patient_timeline_events (id, patient_id, event_date, event_type, title, summary, document_id)
VALUES ('94a21803-cc80-5b6b-a4f8-7ec1814b909e', '66666666-6666-6666-6666-666666666666', '2026-06-01', 'lab_result', 'Antibody Screen & Rh Factor Report', 'Type A Positive, atypical antibody screen negative.', 'b199b566-b88b-5b26-ae6e-1cede86e64d5')
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.patient_timeline_events (id, patient_id, event_date, event_type, title, summary, document_id)
VALUES ('a90ef040-aeb6-5c2f-99bd-e97c5addd469', '66666666-6666-6666-6666-666666666666', '2026-09-01', 'lab_result', 'Group B Streptococcus (GBS) Culture (Pending)', '36-week GBS vaginal-rectal swab collected (Result not recorded).', '895364ec-6b73-5344-a879-f6bf86c09bc4')
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.patient_timeline_events (id, patient_id, event_date, event_type, title, summary, document_id)
VALUES ('2dc72fe3-6b74-5656-9661-eafe545d1433', '77777777-7777-7777-7777-777777777777', '2026-04-05', 'visit', 'Urology Consult & Renal Ultrasound Summary', 'Left renal calculus (4mm) without hydronephrosis. Hydration advised.', 'ea91cb26-b709-5b1f-b12f-efef9f3087b9')
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.patient_timeline_events (id, patient_id, event_date, event_type, title, summary, document_id)
VALUES ('d6799e67-6ca6-5d90-809d-656467c8cd23', '77777777-7777-7777-7777-777777777777', '2026-04-06', 'lab_result', 'Urinalysis & Microscopic Exam Report', 'Urinalysis shows 5-10 RBC/HPF hematuria, no infection.', '45ff8d1b-3b45-5248-9886-0fd39e1010bc')
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.patient_timeline_events (id, patient_id, event_date, event_type, title, summary, document_id)
VALUES ('f58dab26-0d12-53d5-9c37-f2c61095eb13', '77777777-7777-7777-7777-777777777777', '2026-04-12', 'procedure', 'Non-Contrast CT Abdomen & Pelvis (KUB)', 'CT KUB confirms 3.8mm distal left UVJ stone with mild hydronephrosis.', '848def71-fd7b-5180-a425-9f9ab1f978e4')
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.patient_timeline_events (id, patient_id, event_date, event_type, title, summary, document_id)
VALUES ('8018d822-7aa4-501d-8f61-dce1b0da19fe', '77777777-7777-7777-7777-777777777777', '2026-04-26', 'visit', 'Urology Follow-up & Stone Clearance Check', 'Stone passed successfully. Follow-up ultrasound clear.', '73200609-2274-51f0-b173-21a821174b47')
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.patient_timeline_events (id, patient_id, event_date, event_type, title, summary, document_id)
VALUES ('30afc6e7-102a-559d-80d9-6443a107fa35', '77777777-7777-7777-7777-777777777777', '2026-06-15', 'lab_result', '24-Hour Urine Metabolic Stone Risk Panel', '24h urine volume 1.8L. Fluid intake expansion recommended.', '4df2f29e-990a-50fb-83e0-df3e0846155f')
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.patient_timeline_events (id, patient_id, event_date, event_type, title, summary, document_id)
VALUES ('22a37710-534b-5d41-b50d-defc1cc747b0', '77777777-7777-7777-7777-777777777777', '2026-08-01', 'lab_result', 'Calculus Composition Analysis (Pending)', 'Passed stone fragment submitted for infrared spectroscopy (Result not recorded).', '4305d7ce-f14f-5cdf-a058-8251339417e3')
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.patient_timeline_events (id, patient_id, event_date, event_type, title, summary, document_id)
VALUES ('b6cc9620-3b75-548c-bcb7-ba8fea24a3fd', '88888888-8888-8888-8888-888888888888', '2026-03-01', 'lab_result', 'Thyroid Function & Autoantibody Panel', 'TSH 4.8 mIU/L, Anti-TPO positive. Levothyroxine 50mcg daily started.', '86d0cb3b-b4d6-5bc4-b96b-26509c548578')
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.patient_timeline_events (id, patient_id, event_date, event_type, title, summary, document_id)
VALUES ('82ca30ba-7602-5ca0-8aba-d32aa69a4858', '88888888-8888-8888-8888-888888888888', '2026-03-10', 'procedure', 'Thyroid Ultrasound & Nodule Survey', 'Thyroid ultrasound shows heterogeneous parenchyma without nodules.', '6d2768e2-4d48-50e5-b824-e8afe5f860d0')
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.patient_timeline_events (id, patient_id, event_date, event_type, title, summary, document_id)
VALUES ('959aceef-dd48-53e4-9935-ade11bec9cfb', '88888888-8888-8888-8888-888888888888', '2026-04-15', 'lab_result', '6-Week TSH & Free T4 Follow-up Report (v1)', 'TSH normalized to 2.4 mIU/L on Levothyroxine 50mcg.', '78027725-9646-5cf2-a9e9-2d1a54ebc620')
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.patient_timeline_events (id, patient_id, event_date, event_type, title, summary, document_id)
VALUES ('44316add-ccf8-5841-9cb2-402784e15352', '88888888-8888-8888-8888-888888888888', '2026-04-17', 'lab_result', 'Amended TSH Follow-up Report (v2 - Conflict Example)', 'Amended TSH 3.1 mIU/L. Discrepancy logged for review.', '7c215bdb-9cb0-57aa-8430-e90cb5616afd')
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.patient_timeline_events (id, patient_id, event_date, event_type, title, summary, document_id)
VALUES ('83ed3606-023a-5c70-a5ab-b22b80fad998', '88888888-8888-8888-8888-888888888888', '2026-06-05', 'lab_result', 'Serum 25-Hydroxy Vitamin D Level', 'Vitamin D 22 ng/mL. Initiated 50,000 IU weekly supplementation.', 'ec4dcdf4-8910-50fd-95e2-c408c749af41')
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.patient_timeline_events (id, patient_id, event_date, event_type, title, summary, document_id)
VALUES ('2d6e6e41-d091-5e69-b8e3-d46cda52f22d', '88888888-8888-8888-8888-888888888888', '2026-10-01', 'lab_result', '6-Month Repeat TSH & Vitamin D (Pending)', 'Routine 6-month thyroid & Vitamin D re-check requested (Result not recorded).', '7fb00b76-89ba-513d-b169-c9aa3d1e4501')
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.patient_timeline_events (id, patient_id, event_date, event_type, title, summary, document_id)
VALUES ('8e504a9a-c94c-594c-8082-036ecff49946', '99999999-9999-9999-9999-999999999999', '2026-07-02', 'visit', 'Orthopedic Knee Consultation & MRI Report', 'Grade II medial meniscus tear. Physical therapy prescribed.', '3c6d5c25-8a44-5d75-ada2-62fdc2d0a554')
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.patient_timeline_events (id, patient_id, event_date, event_type, title, summary, document_id)
VALUES ('a5d1b79f-b838-51b1-8e47-e7f19526b167', '99999999-9999-9999-9999-999999999999', '2026-07-03', 'procedure', 'Weight-Bearing Right Knee Radiographs', 'X-ray shows mild medial joint space narrowing.', 'cadeb2b9-b4db-5cb9-8e17-8851496c6299')
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.patient_timeline_events (id, patient_id, event_date, event_type, title, summary, document_id)
VALUES ('e0b57e31-3286-5a85-a2c4-c77699a55dc3', '99999999-9999-9999-9999-999999999999', '2026-07-10', 'visit', 'Physical Therapy Initial Evaluation', 'PT evaluated. Baseline flexion 115 deg with mild effusion.', '88ce8635-64c0-527f-8429-672061490cde')
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.patient_timeline_events (id, patient_id, event_date, event_type, title, summary, document_id)
VALUES ('9738c0fa-04c3-5efa-bf22-54feaf8f865d', '99999999-9999-9999-9999-999999999999', '2026-08-22', 'visit', 'Physical Therapy Discharge Summary', 'PT completed. Flexion improved to 132 deg, pain resolved.', '2cb34e8a-bfa1-5b22-be2c-6d3cbef0211e')
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.patient_timeline_events (id, patient_id, event_date, event_type, title, summary, document_id)
VALUES ('d5b0d039-6c16-5244-9075-cc69ca9b80ef', '99999999-9999-9999-9999-999999999999', '2026-09-15', 'procedure', 'Intra-Articular Hyaluronic Acid Injection', 'Administered right knee Synvisc-One 6mL injection under ultrasound guidance.', '1e3a7cc9-b278-5ab3-ad43-8d80bcfbd84d')
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.patient_timeline_events (id, patient_id, event_date, event_type, title, summary, document_id)
VALUES ('b01d9e22-04a5-5aaa-8e10-803f09893342', '99999999-9999-9999-9999-999999999999', '2026-10-02', 'procedure', '6-Month Follow-up Knee MRI (Pending)', 'Follow-up right knee MRI requested for healing evaluation (Result not recorded).', '2453e767-81ef-536d-bd2c-e326df7986c7')
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.patient_timeline_events (id, patient_id, event_date, event_type, title, summary, document_id)
VALUES ('3587fe93-81a2-58f0-a18a-d0cb77981455', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', '2026-08-11', 'visit', 'Dermatology Skin Examination & Biopsy Summary', 'Benign seborrheic keratosis confirmed on biopsy.', '4febb6dc-7d9a-52db-8acc-ae1e7262316a')
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.patient_timeline_events (id, patient_id, event_date, event_type, title, summary, document_id)
VALUES ('36cdf301-a045-58d5-aaa4-20a1c3f908e6', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', '2026-08-15', 'lab_result', 'Histopathology Biopsy Pathology Report', 'Pathology confirms benign Seborrheic Keratosis.', 'c020ab79-72d9-5247-a429-44642943dc72')
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.patient_timeline_events (id, patient_id, event_date, event_type, title, summary, document_id)
VALUES ('1e0d9034-d4ec-5cf4-8e50-6046fab198b9', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', '2026-08-20', 'lab_result', 'Routine Annual Comprehensive Blood Panel', 'CBC, CMP, and Lipid Panel normal.', '11b9d2f1-80db-59b5-b3f4-bd3340f14d0b')
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.patient_timeline_events (id, patient_id, event_date, event_type, title, summary, document_id)
VALUES ('424fab50-6df1-55ea-b9de-df5b10e85692', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', '2026-09-02', 'visit', 'Allergy & Environmental Sensitization Evaluation', 'Positive skin prick test for grass/birch pollen. Fluticasone spray started.', '93bbea5f-fca1-50ab-8c59-7b5cd624c1f2')
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.patient_timeline_events (id, patient_id, event_date, event_type, title, summary, document_id)
VALUES ('15604ae0-4c70-58cd-b526-435717756307', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', '2026-09-18', 'visit', 'Comprehensive Ophthalmic & Vision Exam', 'Vision 20/20 corrected, IOP normal. No glaucoma or cataracts.', 'e5ab39d6-712b-5e4b-8184-0bacb4a485bf')
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.patient_timeline_events (id, patient_id, event_date, event_type, title, summary, document_id)
VALUES ('bf55582a-b224-599c-b174-e1c657dc571e', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', '2026-10-01', 'lab_result', 'Serum Total IgE & Specific Allergen Panel (Pending)', 'Serum total IgE and specific RAST allergen panel ordered (Result not recorded).', '691881f5-fbdc-5080-a673-7e60d1395e1a')
ON CONFLICT (id) DO NOTHING;

COMMIT;
