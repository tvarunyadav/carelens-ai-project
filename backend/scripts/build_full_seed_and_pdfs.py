import os
import json
import uuid
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
import pdfplumber

STORAGE_DIR = "backend/storage/patient_documents"
os.makedirs(STORAGE_DIR, exist_ok=True)

# Patient UUIDs (Preserving exact 3 existing UUIDs)
ELEANOR_ID = "11111111-1111-1111-1111-111111111111"
MARCUS_ID = "22222222-2222-2222-2222-222222222222"
SOPHIA_ID = "33333333-3333-3333-3333-333333333333"
PRIYA_ID = "44444444-4444-4444-4444-444444444444"
DAVID_ID = "55555555-5555-5555-5555-555555555555"
HANNAH_ID = "66666666-6666-6666-6666-666666666666"
CARLOS_ID = "77777777-7777-7777-7777-777777777777"
AISHA_ID = "88888888-8888-8888-8888-888888888888"
JAMES_ID = "99999999-9999-9999-9999-999999999999"
MAYA_ID = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"

SEED_NAMESPACE = uuid.UUID("6ba7b810-9dad-11d1-80b4-00c04fd430c8")

def gen_uuid(name: str) -> str:
    val = str(uuid.uuid5(SEED_NAMESPACE, f"carelens-synthetic-{name}"))
    uuid.UUID(val)
    return val

def create_synthetic_pdf(filepath: str, title: str, patient_name: str, mrn: str, clinical_date: str, paragraphs: list[str]) -> tuple[int, str, int]:
    doc = SimpleDocTemplate(filepath, pagesize=letter, leftMargin=54, rightMargin=54, topMargin=54, bottomMargin=54)
    styles = getSampleStyleSheet()
    
    header_style = ParagraphStyle('HeaderStyle', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=13, textColor=colors.HexColor('#0f766e'), spaceAfter=6)
    meta_style = ParagraphStyle('MetaStyle', parent=styles['Normal'], fontName='Helvetica', fontSize=9, textColor=colors.HexColor('#475569'), spaceAfter=12)
    body_style = ParagraphStyle('BodyStyle', parent=styles['Normal'], fontName='Helvetica', fontSize=10, leading=14, textColor=colors.HexColor('#1e293b'), spaceAfter=8)
    banner_style = ParagraphStyle('BannerStyle', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8, textColor=colors.HexColor('#dc2626'), spaceAfter=12)

    story = []
    story.append(Paragraph("SYNTHETIC DEMO DATA — NON-PHI MEDICAL RECORD — FOR CARELENS AI DEMO ONLY", banner_style))
    story.append(Paragraph(title, header_style))
    story.append(Paragraph(f"<b>Patient:</b> {patient_name} &nbsp;&nbsp; <b>MRN:</b> {mrn} &nbsp;&nbsp; <b>Date:</b> {clinical_date}", meta_style))
    story.append(Spacer(1, 8))

    for p in paragraphs:
        story.append(Paragraph(p, body_style))
    
    doc.build(story)

    file_size = os.path.getsize(filepath)
    extracted_text = ""
    page_count = 1
    with pdfplumber.open(filepath) as pdf:
        page_count = len(pdf.pages)
        for page in pdf.pages:
            t = page.extract_text()
            if t:
                extracted_text += t + "\n"
    
    return page_count, extracted_text.strip(), file_size

# Comprehensive 62 Documents across 10 Patients (~6-8 docs per patient)
def get_documents_data():
    docs = []

    def add_doc(patient_id, patient_name, mrn, key_suffix, title, doc_type, clinical_date, content, event_type, summary, status="final"):
        doc_id = gen_uuid(f"{patient_name.lower().split()[0]}-doc-{key_suffix}")
        timeline_id = gen_uuid(f"{patient_name.lower().split()[0]}-time-{key_suffix}")
        filename = f"{patient_name.lower().split()[0]}_{key_suffix}_{clinical_date}.pdf" if status != "pending" else None
        
        docs.append({
            "id": doc_id,
            "patient_id": patient_id,
            "patient_name": patient_name,
            "mrn": mrn,
            "title": title,
            "doc_type": doc_type,
            "clinical_date": clinical_date,
            "status": status,
            "filename": filename,
            "content": content,
            "timeline": {
                "id": timeline_id,
                "event_date": clinical_date,
                "event_type": event_type,
                "title": title,
                "summary": summary
            }
        })

    # --- 1. SOPHIA PATEL (8 Documents) ---
    add_doc(SOPHIA_ID, "Sophia Patel", "MRN-441029", "initial_consult", "Initial Reproductive Endocrinology Consultation", "consultation", "2026-04-15",
            ["Reason for Visit: Initial evaluation for primary infertility of 18 months duration.",
             "Clinical History: 43-year-old female, gravida 0, para 0. Regular menstrual cycles every 28-30 days.",
             "Assessment & Plan: Order baseline ovarian reserve labs (AMH, FSH, Estradiol), pelvic ultrasound, and HSG."],
            "visit", "Comprehensive fertility evaluation initiated. Baseline labs ordered.")

    add_doc(SOPHIA_ID, "Sophia Patel", "MRN-441029", "baseline_lab", "Baseline Ovarian Reserve & Hormone Panel", "lab_report", "2026-04-20",
            ["Laboratory Results - Cycle Day 3:",
             "Anti-Müllerian Hormone (AMH): 2.8 ng/mL (Reference Range: 1.0 - 3.5 ng/mL - Normal)",
             "Follicle Stimulating Hormone (FSH): 6.2 IU/L (Reference Range: 3.5 - 10.0 IU/L - Normal)",
             "Estradiol (E2): 45 pg/mL (Reference Range: 20 - 80 pg/mL - Normal)",
             "Impression: Normal age-appropriate ovarian reserve parameters."],
            "lab_result", "AMH 2.8 ng/mL, Day 3 FSH 6.2 IU/L. Normal ovarian reserve.")

    add_doc(SOPHIA_ID, "Sophia Patel", "MRN-441029", "hsg_report", "Hysterosalpingogram (HSG) Radiology Report", "radiology", "2026-04-25",
            ["Contrast Hysterosalpingogram Findings:",
             "Uterine cavity demonstrates normal contour without submucosal fibroids or polyps.",
             "Bilateral fallopian tubes are patent with prompt peritoneal contrast spill.",
             "Impression: Normal patent fallopian tubes bilaterally."],
            "procedure", "HSG shows bilateral fallopian tube patency and normal uterine contour.")

    add_doc(SOPHIA_ID, "Sophia Patel", "MRN-441029", "ivf1_meds", "Prescription & Stimulation Protocols - IVF Cycle 1", "medication_record", "2026-05-02",
            ["Controlled Ovarian Hyperstimulation Protocol (Antagonist):",
             "Gonal-F 225 IU subcutaneous daily starting Cycle Day 2 for 9 days.",
             "Menopur 75 IU subcutaneous daily starting Cycle Day 2.",
             "Ganirelix acetate 0.25 mg subcutaneous daily starting Cycle Day 7 once lead follicle reaches 14mm."],
            "medication", "Prescribed Gonal-F 225 IU, Menopur 75 IU, Ganirelix antagonist protocol.")

    add_doc(SOPHIA_ID, "Sophia Patel", "MRN-441029", "pelvic_us", "Transvaginal Pelvic Ultrasound & Antral Follicle Count", "ultrasound", "2026-05-10",
            ["Ultrasound Findings - Stimulation Day 8:",
             "Right Ovary: 7 antral follicles (12mm, 14mm, 15mm, 16mm, 11mm, 10mm, 9mm).",
             "Left Ovary: 6 antral follicles (15mm, 14mm, 13mm, 11mm, 10mm, 8mm).",
             "Endometrial Thickness: 9.4 mm triple-line pattern."],
            "procedure", "13 growing follicles (lead follicles 16mm R, 15mm L). Endometrium 9.4mm.")

    add_doc(SOPHIA_ID, "Sophia Patel", "MRN-441029", "oocyte_retrieval", "Oocyte Retrieval & Embryology Lab Summary", "procedure", "2026-05-18",
            ["Procedure Summary: Transvaginal ultrasound-guided oocyte retrieval under conscious sedation.",
             "Yield: 10 cumulus-oocyte complexes retrieved.",
             "Embryology Results: 8 MII mature oocytes fertilized via ICSI; 4 high-grade blastocysts vitrified on Day 5."],
            "procedure", "10 oocytes retrieved, 8 mature fertilized via ICSI, 4 Day-5 blastocysts vitrified.")

    add_doc(SOPHIA_ID, "Sophia Patel", "MRN-441029", "fet_meds", "Frozen Embryo Transfer (FET) Preparation Protocol", "medication_record", "2026-07-12",
            ["Programmed FET Cycle Medications:",
             "Estradiol valerate (Estrace) 2 mg oral three times daily.",
             "Progesterone in sesame oil 50 mg IM daily starting 5 days prior to planned transfer."],
            "medication", "Initiated Estrace 2mg TID and IM Progesterone in preparation for embryo transfer.")

    add_doc(SOPHIA_ID, "Sophia Patel", "MRN-441029", "karyotype_pending", "Karyotype & Chromosomal Microarray Panel (Order Pending)", "lab_report", "2026-09-15",
            [], "lab_result", "High-resolution blood karyotype requested. Lab processing underway (Result not recorded).", status="pending")

    # --- 2. ELEANOR VANE (6 Documents) ---
    add_doc(ELEANOR_ID, "Eleanor Vane", "MRN-884920", "annual_exam", "Annual Wellness & Gynecology Assessment", "consultation", "2026-03-10",
            ["Patient Profile: 58-year-old postmenopausal female presenting for annual preventive gynecologic exam.",
             "History: Menopause at age 52. Mild vasomotor symptoms managed lifestyle.",
             "Plan: Screening mammogram ordered. Routine DEXA bone density scan scheduled."],
            "visit", "Routine postmenopausal checkup. Preventive mammogram ordered.")

    add_doc(ELEANOR_ID, "Eleanor Vane", "MRN-884920", "mammogram", "Screening 3D Digital Mammogram", "ultrasound", "2026-03-15",
            ["Bilateral 3D Digital Screening Mammogram:",
             "Findings: Scattered fibroglandular densities (BI-RADS Category 2). No suspicious masses or calcifications.",
             "Recommendation: Routine annual screening in 12 months."],
            "procedure", "BI-RADS 2 - Benign findings. Annual screening recommended.")

    add_doc(ELEANOR_ID, "Eleanor Vane", "MRN-884920", "dexa_scan", "Dual-Energy X-Ray Absorptiometry (DEXA) Bone Density", "radiology", "2026-03-22",
            ["DEXA Bone Density Scan Results:",
             "Lumbar Spine (L1-L4) T-score: -1.4 (Osteopenia).",
             "Left Femoral Neck T-score: -1.2 (Osteopenia).",
             "Plan: Calcium 1200 mg daily, Vitamin D3 2000 IU daily, weight-bearing exercise."],
            "procedure", "DEXA scan demonstrates mild osteopenia (T-score -1.4). Calcium & Vitamin D recommended.")

    add_doc(ELEANOR_ID, "Eleanor Vane", "MRN-884920", "amh_v1", "Baseline Ovarian Assessment & Ultrasound (v1)", "lab_report", "2026-04-10",
            ["Baseline Ovarian Assessment:",
             "Serum AMH Level: 1.8 ng/mL.",
             "Antral Follicle Count (AFC): 11 (Right: 6, Left: 5).",
             "Uterine Cavity: Normal, Endometrium 7.2mm homogenous."],
            "lab_result", "Baseline AMH 1.8 ng/mL, AFC 11. Uterine cavity normal.")

    add_doc(ELEANOR_ID, "Eleanor Vane", "MRN-884920", "amh_v2_conflict", "Amended Baseline Ovarian Assessment (v2 - Conflict Example)", "lab_report", "2026-04-12",
            ["Amended Clinical Report (v2):",
             "Serum AMH Level: 1.2 ng/mL (Re-tested / Recalibrated value).",
             "Antral Follicle Count (AFC): 9 (Right: 5, Left: 4).",
             "Note: Supersedes preliminary report dated 2026-04-10 due to analyzer recalibration."],
            "lab_result", "Amended AMH 1.2 ng/mL (Recalibrated). Discrepancy flagged for review.")

    add_doc(ELEANOR_ID, "Eleanor Vane", "MRN-884920", "colonoscopy_pending", "Screening Colonoscopy (Order Pending)", "procedure", "2026-09-01",
            [], "procedure", "Screening colonoscopy requested for age 58. Procedure scheduled (Result not recorded).", status="pending")

    # --- 3. MARCUS CHEN (6 Documents) ---
    add_doc(MARCUS_ID, "Marcus Chen", "MRN-993041", "cardiology_consult", "Cardiology Consultation & Lipid Profile", "consultation", "2026-06-18",
            ["Reason for Visit: Cardiovascular risk assessment and hyperlipidemia management.",
             "Vitals: BP 124/78 mmHg, HR 68 bpm. Lipid Panel: Total Cholesterol 215 mg/dL, LDL 138 mg/dL, HDL 48 mg/dL.",
             "Plan: Continue Atorvastatin 10 mg daily. Mediterranean diet and aerobic exercise."],
            "visit", "LDL 138 mg/dL. Prescribed Atorvastatin 10mg daily.")

    add_doc(MARCUS_ID, "Marcus Chen", "MRN-993041", "ekg_report", "12-Lead Resting Electrocardiogram (EKG)", "lab_report", "2026-06-20",
            ["12-Lead EKG Interpretation:",
             "Normal sinus rhythm at 66 bpm. Normal axis, PR interval 152 ms, QRS 88 ms, QTc 412 ms.",
             "No ST-segment elevation or ST-T wave abnormalities."],
            "procedure", "12-lead EKG shows normal sinus rhythm without ischemia.")

    add_doc(MARCUS_ID, "Marcus Chen", "MRN-993041", "carotid_us", "Carotid Artery Duplex Ultrasound", "ultrasound", "2026-07-05",
            ["Carotid Ultrasound Findings:",
             "Bilateral carotid arteries demonstrate minimal intimal thickening (<20% stenosis).",
             "Normal peak systolic velocities bilaterally. Antegrade vertebral flow."],
            "procedure", "Minimal carotid intimal thickening (<20% stenosis). Normal flow.")

    add_doc(MARCUS_ID, "Marcus Chen", "MRN-993041", "lipid_followup", "Repeat Lipid & Liver Function Panel", "lab_report", "2026-09-10",
            ["Repeat Blood Chemistry Results:",
             "LDL Cholesterol: 92 mg/dL (Target achieved <100 mg/dL).",
             "ALT: 22 U/L, AST: 19 U/L (Normal liver enzymes)."],
            "lab_result", "LDL reduced to 92 mg/dL on Atorvastatin 10mg. Liver enzymes normal.")

    add_doc(MARCUS_ID, "Marcus Chen", "MRN-993041", "stress_test", "Exercise Stress Echocardiogram", "procedure", "2026-09-22",
            ["Treadmill Exercise Stress Test:",
             "Exercised 10 minutes 30 seconds (11.5 METs). Reached 94% predicted max heart rate.",
             "No inducible ischemia or wall motion abnormalities noted."],
            "procedure", "Normal stress echocardiogram (11.5 METs, no ischemia).")

    add_doc(MARCUS_ID, "Marcus Chen", "MRN-993041", "cac_pending", "Coronary Artery Calcium (CAC) CT Scan (Pending)", "radiology", "2026-10-01",
            [], "procedure", "CAC CT scan ordered for calcium scoring (Result not recorded).", status="pending")

    # --- 4. PRIYA SHARMA (6 Documents) ---
    add_doc(PRIYA_ID, "Priya Sharma", "MRN-104928", "pcos_consult", "Endocrine Consultation for PCOS & Cycle Irregularity", "consultation", "2026-02-14",
            ["Clinical Presentation: 37-year-old female presenting with oligomenorrhea and acne.",
             "Diagnosis: Polycystic Ovary Syndrome (PCOS) based on Rotterdam criteria.",
             "Plan: Metformin ER 500 mg daily with dinner. Lifestyle management."],
            "visit", "PCOS diagnosed. Metformin ER 500mg initiated.")

    add_doc(PRIYA_ID, "Priya Sharma", "MRN-104928", "glucose_panel", "Fasting Glucose & HbA1c Laboratory Report", "lab_report", "2026-02-20",
            ["Fasting Plasma Glucose: 98 mg/dL (Normal <100 mg/dL).",
             "Hemoglobin A1c: 5.6% (Normal <5.7%).",
             "Fasting Insulin: 14.2 uIU/mL (Mild insulin resistance)."],
            "lab_result", "HbA1c 5.6%, Fasting Glucose 98 mg/dL.")

    add_doc(PRIYA_ID, "Priya Sharma", "MRN-104928", "pelvic_ultrasound", "Pelvic Ultrasound - Polycystic Ovarian Morphology", "ultrasound", "2026-03-05",
            ["Transvaginal Ultrasound Findings:",
             "Bilateral enlarged ovaries (Right 12.4 mL, Left 11.8 mL) with >12 peripheral follicles bilaterally ('string of pearls').",
             "Endometrium: 6.8 mm, homogeneous."],
            "procedure", "Ultrasound confirms polycystic ovarian morphology bilaterally.")

    add_doc(PRIYA_ID, "Priya Sharma", "MRN-104928", "androgen_panel", "Comprehensive Serum Androgen Panel", "lab_report", "2026-03-12",
            ["Laboratory Results:",
             "Total Testosterone: 64 ng/dL (Elevated, Ref 15 - 45 ng/dL).",
             "Free Testosterone: 8.2 pg/mL (Elevated).",
             "DHEA-S: 240 ug/dL (Normal)."],
            "lab_result", "Elevated serum testosterone (64 ng/dL) consistent with hyperandrogenism.")

    add_doc(PRIYA_ID, "Priya Sharma", "MRN-104928", "letrozole_presc", "Ovulation Induction Prescription - Letrozole", "medication_record", "2026-04-01",
            ["Prescription & Protocol:",
             "Letrozole (Femara) 2.5 mg oral daily on Cycle Days 3-7.",
             "Timed intercourse protocol with LH surge monitoring."],
            "medication", "Prescribed Letrozole 2.5mg daily for ovulation induction.")

    add_doc(PRIYA_ID, "Priya Sharma", "MRN-104928", "prog_check_pending", "Day 21 Serum Progesterone (Order Pending)", "lab_report", "2026-04-22",
            [], "lab_result", "Day 21 progesterone ordered to confirm ovulation (Result not recorded).", status="pending")

    # --- 5. DAVID KIM (6 Documents) ---
    add_doc(DAVID_ID, "David Kim", "MRN-552914", "andrology_eval", "Male Reproductive Health & Andrology Evaluation", "consultation", "2026-05-10",
            ["Evaluation: 46-year-old male evaluated for couple infertility.",
             "Semen Analysis: Concentration 42 M/mL, Motility 58% progressive, Normal Morphology 4%.",
             "Impression: Normal semen parameters. No male factor infertility."],
            "visit", "Semen analysis normal (42M/mL, 58% motility).")

    add_doc(DAVID_ID, "David Kim", "MRN-552914", "hormone_panel", "Male Hormone & Endocrine Panel", "lab_report", "2026-05-15",
            ["Male Endocrine Lab Results:",
             "Serum Testosterone: 520 ng/dL (Normal range 300 - 1000 ng/dL).",
             "FSH: 4.1 IU/L, LH: 3.8 IU/L, Prolactin: 8.4 ng/mL.",
             "Impression: Normal hypothalamic-pituitary-gonadal axis."],
            "lab_result", "Serum testosterone 520 ng/dL, normal gonadotropins.")

    add_doc(DAVID_ID, "David Kim", "MRN-552914", "scrotal_us", "Scrotal Duplex Ultrasound", "ultrasound", "2026-05-28",
            ["Scrotal Ultrasound Findings:",
             "Bilateral testes normal volume and echotexture. No testicular masses.",
             "Grade I left subclinical varicocele without retrograde flow on Valsalva."],
            "procedure", "Scrotal ultrasound shows subclinical Grade I left varicocele.")

    add_doc(DAVID_ID, "David Kim", "MRN-552914", "dna_frag", "Sperm DNA Fragmentation Index (DFI) Test", "lab_report", "2026-06-12",
            ["Sperm Chromatin Structure Assay (SCSA):",
             "DNA Fragmentation Index (DFI): 12% (Excellent fertility potential <15%).",
             "High Stainable DNA (HSD): 4%."],
            "lab_result", "Sperm DFI 12% - Excellent sperm DNA integrity.")

    add_doc(DAVID_ID, "David Kim", "MRN-552914", "wellness_exam", "Annual Executive Health Physical", "consultation", "2026-08-01",
            ["Physical Exam: Vital signs stable, BMI 24.2 kg/m2.",
             "Routine Screening: Complete Blood Count, Metabolic Panel, Lipid Panel normal.",
             "Plan: Continue active lifestyle and annual preventive checkups."],
            "visit", "Annual physical normal. Metabolic & hematologic panels clear.")

    add_doc(DAVID_ID, "David Kim", "MRN-552914", "y_chrom_pending", "Y-Chromosome Microdeletion Assay (Pending)", "lab_report", "2026-09-10",
            [], "lab_result", "Y-chromosome microdeletion screen requested (Result not recorded).", status="pending")

    # --- 6. HANNAH ABBOTT (6 Documents) ---
    add_doc(HANNAH_ID, "Hannah Abbott", "MRN-663819", "first_trimester", "First Trimester Obstetrics Consultation & Ultrasound", "consultation", "2026-01-22",
            ["OB Consultation: 35-year-old G1P0 at 8 weeks 4 days estimated gestational age.",
             "Ultrasound: Single live intrauterine pregnancy with cardiac activity 164 bpm. CRL 2.1 cm.",
             "Plan: Initiate prenatal vitamins, folic acid 1 mg daily."],
            "visit", "8w4d intrauterine pregnancy confirmed with HR 164 bpm.")

    add_doc(HANNAH_ID, "Hannah Abbott", "MRN-663819", "nipt_screening", "Non-Invasive Prenatal Testing (NIPT) Screen", "lab_report", "2026-02-10",
            ["Cell-Free Fetal DNA NIPT Panel:",
             "Trisomy 21 (Down Syndrome): Low Risk (<1 in 10,000).",
             "Trisomy 18 & 13: Low Risk.",
             "Fetal Sex: Female. Fetal Fraction: 8.4%."],
            "lab_result", "NIPT low risk for Trisomies 21, 18, and 13. Fetal fraction 8.4%.")

    add_doc(HANNAH_ID, "Hannah Abbott", "MRN-663819", "anatomy_scan", "Second Trimester Fetal Anatomy Ultrasound", "ultrasound", "2026-04-18",
            ["20-Week Fetal Anatomy Ultrasound:",
             "Normal fetal anatomical survey (brain, spine, cardiac 4-chamber view, kidneys, stomach).",
             "Estimated Fetal Weight: 340g (52nd percentile). Placenta anterior, clear of os."],
            "procedure", "20-week fetal anatomy ultrasound normal. EFW 340g (52nd percentile).")

    add_doc(HANNAH_ID, "Hannah Abbott", "MRN-663819", "glucose_challenge", "1-Hour Oral Glucose Tolerance Test (OGTT)", "lab_report", "2026-05-25",
            ["1-Hour 50g Glucose Challenge Test:",
             "Serum Glucose: 118 mg/dL (Normal <140 mg/dL).",
             "Impression: Negative screen for gestational diabetes."],
            "lab_result", "1-hour OGTT 118 mg/dL - Negative for gestational diabetes.")

    add_doc(HANNAH_ID, "Hannah Abbott", "MRN-663819", "rh_antibody", "Antibody Screen & Rh Factor Report", "lab_report", "2026-06-01",
            ["Blood Typing & Antibody Screen:",
             "Blood Type: A Positive (Rh D Positive).",
             "Atypical Antibody Screen: Negative."],
            "lab_result", "Type A Positive, atypical antibody screen negative.")

    add_doc(HANNAH_ID, "Hannah Abbott", "MRN-663819", "gbs_pending", "Group B Streptococcus (GBS) Culture (Pending)", "lab_report", "2026-09-01",
            [], "lab_result", "36-week GBS vaginal-rectal swab collected (Result not recorded).", status="pending")

    # --- 7. CARLOS RODRIGUEZ (6 Documents) ---
    add_doc(CARLOS_ID, "Carlos Rodriguez", "MRN-771829", "urology_consult", "Urology Consult & Renal Ultrasound Summary", "consultation", "2026-04-05",
            ["Reason for Visit: Left flank discomfort.",
             "Renal Ultrasound: 4mm non-obstructing calculus in left lower pole. No hydronephrosis.",
             "Plan: Conservative management, aggressive oral hydration, strain urine."],
            "visit", "Left renal calculus (4mm) without hydronephrosis. Hydration advised.")

    add_doc(CARLOS_ID, "Carlos Rodriguez", "MRN-771829", "urinalysis", "Urinalysis & Microscopic Exam Report", "lab_report", "2026-04-06",
            ["Urinalysis Findings:",
             "Microscopic Hematuria: 5-10 RBC/HPF (Ref 0-2).",
             "Leukocyte Esterase: Negative, Nitrites: Negative, pH: 6.0.",
             "Impression: Microscopic hematuria consistent with renal calculus passage."],
            "lab_result", "Urinalysis shows 5-10 RBC/HPF hematuria, no infection.")

    add_doc(CARLOS_ID, "Carlos Rodriguez", "MRN-771829", "ct_kud", "Non-Contrast CT Abdomen & Pelvis (KUB)", "radiology", "2026-04-12",
            ["CT KUB Findings:",
             "3.8mm calculus located in distal left ureterovesical junction.",
             "Mild left ureterohydronephrosis."],
            "procedure", "CT KUB confirms 3.8mm distal left UVJ stone with mild hydronephrosis.")

    add_doc(CARLOS_ID, "Carlos Rodriguez", "MRN-771829", "flank_followup", "Urology Follow-up & Stone Clearance Check", "consultation", "2026-04-26",
            ["Follow-up Visit:",
             "Patient reports complete resolution of flank pain after passing small stone fragment.",
             "Repeat Renal Ultrasound: No residual left renal or ureteral calculi. Resolved hydronephrosis."],
            "visit", "Stone passed successfully. Follow-up ultrasound clear.")

    add_doc(CARLOS_ID, "Carlos Rodriguez", "MRN-771829", "metabolic_stone", "24-Hour Urine Metabolic Stone Risk Panel", "lab_report", "2026-06-15",
            ["24-Hour Urine Panel:",
             "Urine Volume: 1.8 L/day (Goal >2.5 L). Calcium: 260 mg/day (Mild hypercalciuria).",
             "Citrate: 450 mg/day (Normal). Oxalate: 32 mg/day (Normal)."],
            "lab_result", "24h urine volume 1.8L. Fluid intake expansion recommended.")

    add_doc(CARLOS_ID, "Carlos Rodriguez", "MRN-771829", "stone_analysis_pending", "Calculus Composition Analysis (Pending)", "lab_report", "2026-08-01",
            [], "lab_result", "Passed stone fragment submitted for infrared spectroscopy (Result not recorded).", status="pending")

    # --- 8. AISHA KHAN (6 Documents) ---
    add_doc(AISHA_ID, "Aisha Khan", "MRN-882941", "thyroid_panel", "Thyroid Function & Autoantibody Panel", "lab_report", "2026-03-01",
            ["Thyroid Panel Results:",
             "TSH: 4.8 mIU/L (Elevated, Ref 0.4 - 4.0 mIU/L).",
             "Free T4: 1.1 ng/dL (Normal).",
             "Anti-TPO Antibodies: Positive (145 IU/mL).",
             "Plan: Subclinical hypothyroidism secondary to Hashimoto's. Start Levothyroxine 50 mcg daily."],
            "lab_result", "TSH 4.8 mIU/L, Anti-TPO positive. Levothyroxine 50mcg daily started.")

    add_doc(AISHA_ID, "Aisha Khan", "MRN-882941", "thyroid_us", "Thyroid Ultrasound & Nodule Survey", "ultrasound", "2026-03-10",
            ["Thyroid Ultrasound Findings:",
             "Diffuse heterogeneous echotexture characteristic of chronic autoimmune thyroiditis.",
             "No focal thyroid nodules >1cm identified. Normal vascular flow."],
            "procedure", "Thyroid ultrasound shows heterogeneous parenchyma without nodules.")

    add_doc(AISHA_ID, "Aisha Khan", "MRN-882941", "tsh_followup_v1", "6-Week TSH & Free T4 Follow-up Report (v1)", "lab_report", "2026-04-15",
            ["Repeat Thyroid Panel (v1):",
             "TSH: 2.4 mIU/L (Normal target achieved).",
             "Free T4: 1.3 ng/dL (Normal).",
             "Plan: Maintain Levothyroxine 50 mcg daily."],
            "lab_result", "TSH normalized to 2.4 mIU/L on Levothyroxine 50mcg.")

    add_doc(AISHA_ID, "Aisha Khan", "MRN-882941", "tsh_followup_v2_conflict", "Amended TSH Follow-up Report (v2 - Conflict Example)", "lab_report", "2026-04-17",
            ["Amended Thyroid Panel (v2):",
             "TSH: 3.1 mIU/L (Re-assayed value).",
             "Free T4: 1.2 ng/dL.",
             "Note: Lab re-run requested by endocrinology due to baseline reagent lot shift."],
            "lab_result", "Amended TSH 3.1 mIU/L. Discrepancy logged for review.")

    add_doc(AISHA_ID, "Aisha Khan", "MRN-882941", "vit_d_level", "Serum 25-Hydroxy Vitamin D Level", "lab_report", "2026-06-05",
            ["Serum 25-OH Vitamin D:",
             "Result: 22 ng/mL (Deficient <30 ng/mL).",
             "Plan: Ergocalciferol (Vitamin D2) 50,000 IU weekly for 8 weeks."],
            "lab_result", "Vitamin D 22 ng/mL. Initiated 50,000 IU weekly supplementation.")

    add_doc(AISHA_ID, "Aisha Khan", "MRN-882941", "tsh_recheck_pending", "6-Month Repeat TSH & Vitamin D (Pending)", "lab_report", "2026-10-01",
            [], "lab_result", "Routine 6-month thyroid & Vitamin D re-check requested (Result not recorded).", status="pending")

    # --- 9. JAMES WILSON (6 Documents) ---
    add_doc(JAMES_ID, "James Wilson", "MRN-994812", "ortho_consult", "Orthopedic Knee Consultation & MRI Report", "consultation", "2026-07-02",
            ["Right Knee Evaluation: 47-year-old male with persistent right knee joint pain.",
             "MRI Findings: Grade II medial meniscus oblique tear. Intact ACL and PCL.",
             "Plan: Physical therapy twice weekly for 6 weeks, NSAIDs as needed."],
            "visit", "Grade II medial meniscus tear. Physical therapy prescribed.")

    add_doc(JAMES_ID, "James Wilson", "MRN-994812", "knee_xray", "Weight-Bearing Right Knee Radiographs", "radiology", "2026-07-03",
            ["Right Knee X-Ray (3 Views):",
             "Mild medial compartment joint space narrowing.",
             "No acute cortical fractures or dislocation."],
            "procedure", "X-ray shows mild medial joint space narrowing.")

    add_doc(JAMES_ID, "James Wilson", "MRN-994812", "pt_eval", "Physical Therapy Initial Evaluation", "consultation", "2026-07-10",
            ["PT Evaluation Notes:",
             "Right knee ROM: Flexion 115 degrees, Extension 0 degrees. Mild joint effusion.",
             "Goals: Restore full ROM to 130 deg flexion, quadriceps strengthening."],
            "visit", "PT evaluated. Baseline flexion 115 deg with mild effusion.")

    add_doc(JAMES_ID, "James Wilson", "MRN-994812", "pt_discharge", "Physical Therapy Discharge Summary", "consultation", "2026-08-22",
            ["PT Discharge Assessment:",
             "Completed 12 sessions. Right knee ROM: Flexion 132 degrees, full pain-free extension.",
             "Outcome: Able to resume light jogging without pain. Home exercise program provided."],
            "visit", "PT completed. Flexion improved to 132 deg, pain resolved.")

    add_doc(JAMES_ID, "James Wilson", "MRN-994812", "hyaluronic_inj", "Intra-Articular Hyaluronic Acid Injection", "procedure", "2026-09-15",
            ["Procedure Summary:",
             "Right knee intra-articular injection of High Molecular Weight Hyaluronan (Synvisc-One 6 mL).",
             "Procedure performed under sterile technique with ultrasound guidance without complication."],
            "procedure", "Administered right knee Synvisc-One 6mL injection under ultrasound guidance.")

    add_doc(JAMES_ID, "James Wilson", "MRN-994812", "mri_followup_pending", "6-Month Follow-up Knee MRI (Pending)", "radiology", "2026-10-02",
            [], "procedure", "Follow-up right knee MRI requested for healing evaluation (Result not recorded).", status="pending")

    # --- 10. MAYA LIN (6 Documents) ---
    add_doc(MAYA_ID, "Maya Lin", "MRN-109283", "dermatology_exam", "Dermatology Skin Examination & Biopsy Summary", "consultation", "2026-08-11",
            ["Skin Exam: 40-year-old female for routine full-body cutaneous examination.",
             "Biopsy Result (Right forearm lesion): Seborrheic keratosis, benign. No dysplastic features.",
             "Plan: Reassurance provided. Re-evaluate annually."],
            "visit", "Benign seborrheic keratosis confirmed on biopsy.")

    add_doc(MAYA_ID, "Maya Lin", "MRN-109283", "derm_pathology", "Histopathology Biopsy Pathology Report", "lab_report", "2026-08-15",
            ["Surgical Pathology Report:",
             "Specimen: 3mm punch biopsy right forearm lesion.",
             "Microscopic Description: Hyperkeratosis, acanthosis, and intraepidermal horn cysts.",
             "Diagnosis: Benign Seborrheic Keratosis."],
            "lab_result", "Pathology confirms benign Seborrheic Keratosis.")

    add_doc(MAYA_ID, "Maya Lin", "MRN-109283", "annual_blood", "Routine Annual Comprehensive Blood Panel", "lab_report", "2026-08-20",
            ["Annual Lab Panel Results:",
             "CBC: WBC 6.2 k/uL, Hemoglobin 13.4 g/dL, Platelets 245 k/uL.",
             "CMP: Sodium 140 mEq/L, Potassium 4.2 mEq/L, Creatinine 0.75 mg/dL.",
             "Lipid Panel: Total Cholesterol 175 mg/dL, LDL 98 mg/dL."],
            "lab_result", "CBC, CMP, and Lipid Panel normal.")

    add_doc(MAYA_ID, "Maya Lin", "MRN-109283", "allergy_eval", "Allergy & Environmental Sensitization Evaluation", "consultation", "2026-09-02",
            ["Allergy Evaluation:",
             "History: Seasonal allergic rhinitis in spring months.",
             "Skin Prick Test: Positive reaction to Timothy grass and birch pollen. Negative to dust mites.",
             "Plan: Fluticasone propionate nasal spray 50 mcg/actuation daily."],
            "visit", "Positive skin prick test for grass/birch pollen. Fluticasone spray started.")

    add_doc(MAYA_ID, "Maya Lin", "MRN-109283", "optometry_exam", "Comprehensive Ophthalmic & Vision Exam", "consultation", "2026-09-18",
            ["Vision Exam Findings:",
             "Visual Acuity: 20/20 OD, 20/20 OS with mild refractive correction.",
             "Intraocular Pressure: 14 mmHg OD, 15 mmHg OS (Normal). Slit lamp exam clear."],
            "visit", "Vision 20/20 corrected, IOP normal. No glaucoma or cataracts.")

    add_doc(MAYA_ID, "Maya Lin", "MRN-109283", "ige_panel_pending", "Serum Total IgE & Specific Allergen Panel (Pending)", "lab_report", "2026-10-01",
            [], "lab_result", "Serum total IgE and specific RAST allergen panel ordered (Result not recorded).", status="pending")

    return docs

documents_data = get_documents_data()

# Fertility Cycles Data for Sophia Patel
cycles_data = [
    {
        "id": gen_uuid("sophia-cycle-1"),
        "patient_id": SOPHIA_ID,
        "cycle_name": "IVF Cycle 1 - Antagonist Ovulation Induction",
        "start_date": "2026-05-01",
        "end_date": "2026-05-28",
        "status": "completed",
        "notes_json": json.dumps({"oocytes_retrieved": 10, "mature": 8, "blastocysts_frozen": 4})
    },
    {
        "id": gen_uuid("sophia-cycle-2"),
        "patient_id": SOPHIA_ID,
        "cycle_name": "IVF Cycle 2 - Frozen Embryo Transfer (FET)",
        "start_date": "2026-07-10",
        "end_date": "2026-09-01",
        "status": "completed",
        "notes_json": json.dumps({"embryo_transferred": "Day 5 4AA Blastocyst", "outcome": "Positive Serum Beta-hCG"})
    }
]

def validate_all_uuids():
    print("Validating generated UUIDs and references across 10 patients...")
    valid_patient_ids = {SOPHIA_ID, ELEANOR_ID, MARCUS_ID, PRIYA_ID, DAVID_ID, HANNAH_ID, CARLOS_ID, AISHA_ID, JAMES_ID, MAYA_ID}
    valid_doc_ids = set()

    for d in documents_data:
        uuid.UUID(d["id"])
        uuid.UUID(d["patient_id"])
        uuid.UUID(d["timeline"]["id"])
        assert d["patient_id"] in valid_patient_ids, f"Invalid patient FK: {d['patient_id']}"
        valid_doc_ids.add(d["id"])

    for c in cycles_data:
        uuid.UUID(c["id"])
        uuid.UUID(c["patient_id"])
        assert c["patient_id"] in valid_patient_ids, f"Invalid patient FK in cycle: {c['patient_id']}"

    print(f"Validation passed cleanly: {len(documents_data)} documents across 10 synthetic patients.")

def build_seed_and_pdfs():
    validate_all_uuids()

    sql_statements = [
        "-- Seed 003: Synthetic Patient History Records (Documents, Versions, Timeline Events, Fertility Cycles)",
        "-- Executed FIFTH in Supabase SQL Editor\n",
        "BEGIN;\n"
    ]

    sql_statements.append("-- 1. Insert Fertility Cycles")
    for c in cycles_data:
        sql = f"""INSERT INTO public.fertility_cycles (id, patient_id, cycle_name, start_date, end_date, status, notes_json)
VALUES ('{c['id']}', '{c['patient_id']}', '{c['cycle_name']}', '{c['start_date']}', '{c['end_date']}', '{c['status']}', '{c['notes_json']}'::jsonb)
ON CONFLICT (id) DO NOTHING;"""
        sql_statements.append(sql)

    sql_statements.append("\n-- 2. Insert Patient Documents & Document Versions")
    for d in documents_data:
        filename = d["filename"]
        storage_path = f"patient-documents/{filename}" if filename else None
        file_size = 0
        extracted_text = None
        page_count = 1
        extraction_status = "pending"

        if filename:
            filepath = os.path.join(STORAGE_DIR, filename)
            page_count, extracted_text, file_size = create_synthetic_pdf(
                filepath, d["title"], d["patient_name"], d["mrn"], d["clinical_date"], d["content"]
            )
            extraction_status = "processed"

        escaped_text = extracted_text.replace("'", "''") if extracted_text else ""
        escaped_title = d["title"].replace("'", "''")
        storage_sql = f"'{storage_path}'" if storage_path else "NULL"

        sql_doc = f"""INSERT INTO public.patient_documents (id, patient_id, title, doc_type, clinical_date, status, storage_path, mime_type, file_size, current_version)
VALUES ('{d['id']}', '{d['patient_id']}', '{escaped_title}', '{d['doc_type']}', '{d['clinical_date']}', '{d['status']}', {storage_sql}, 'application/pdf', {file_size}, 1)
ON CONFLICT (id) DO NOTHING;"""
        sql_statements.append(sql_doc)

        if storage_path:
            sql_ver = f"""INSERT INTO public.patient_document_versions (document_id, version_number, storage_path, extracted_text, page_count, extraction_status)
VALUES ('{d['id']}', 1, '{storage_path}', '{escaped_text}', {page_count}, '{extraction_status}')
ON CONFLICT (document_id, version_number) DO NOTHING;"""
            sql_statements.append(sql_ver)

    sql_statements.append("\n-- 3. Insert Patient Timeline Events")
    for d in documents_data:
        t = d["timeline"]
        doc_id_sql = f"'{d['id']}'" if d["filename"] or d["status"] == "pending" else "NULL"
        escaped_t_title = t["title"].replace("'", "''")
        escaped_t_summary = t["summary"].replace("'", "''")

        sql_time = f"""INSERT INTO public.patient_timeline_events (id, patient_id, event_date, event_type, title, summary, document_id)
VALUES ('{t['id']}', '{d['patient_id']}', '{t['event_date']}', '{t['event_type']}', '{escaped_t_title}', '{escaped_t_summary}', {doc_id_sql})
ON CONFLICT (id) DO NOTHING;"""
        sql_statements.append(sql_time)

    sql_statements.append("\nCOMMIT;\n")

    seed_sql_path = "database/seeds/003_synthetic_history_seed.sql"
    with open(seed_sql_path, "w", encoding="utf-8") as f:
        f.write("\n".join(sql_statements))
    
    print(f"Successfully generated synthetic PDFs in '{STORAGE_DIR}' and seed SQL at '{seed_sql_path}'")

if __name__ == "__main__":
    build_seed_and_pdfs()
