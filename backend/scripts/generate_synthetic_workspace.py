import os
import json
import uuid
from datetime import date
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
import pdfplumber

STORAGE_DIR = "backend/storage/patient_documents"
os.makedirs(STORAGE_DIR, exist_ok=True)

# Synthetic Patient UUIDs
SOPHIA_ID = "33333333-3333-3333-3333-333333333333"
ELEANOR_ID = "11111111-1111-1111-1111-111111111111"
MARCUS_ID = "22222222-2222-2222-2222-222222222222"

def create_synthetic_pdf(filepath: str, title: str, patient_name: str, mrn: str, clinical_date: str, content_paragraphs: list[str]) -> tuple[int, str]:
    """Generates a text-based synthetic PDF and extracts its text using pdfplumber."""
    doc = SimpleDocTemplate(filepath, pagesize=letter, leftMargin=54, rightMargin=54, topMargin=54, bottomMargin=54)
    styles = getSampleStyleSheet()
    
    header_style = ParagraphStyle(
        'HeaderStyle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=14,
        textColor=colors.HexColor('#0f766e'), # Teal
        spaceAfter=6
    )
    meta_style = ParagraphStyle(
        'MetaStyle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        textColor=colors.HexColor('#475569'),
        spaceAfter=12
    )
    body_style = ParagraphStyle(
        'BodyStyle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#1e293b'),
        spaceAfter=8
    )
    banner_style = ParagraphStyle(
        'BannerStyle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        textColor=colors.HexColor('#dc2626'),
        spaceAfter=14
    )

    story = []
    story.append(Paragraph("SYNTHETIC DEMO DATA — NON-PHI MEDICAL RECORD — FOR CARELENS AI TESTING ONLY", banner_style))
    story.append(Paragraph(title, header_style))
    story.append(Paragraph(f"<b>Patient Name:</b> {patient_name} &nbsp;&nbsp;|&nbsp;&nbsp; <b>MRN:</b> {mrn} &nbsp;&nbsp;|&nbsp;&nbsp; <b>Clinical Date:</b> {clinical_date}", meta_style))
    story.append(Spacer(1, 10))

    for p_text in content_paragraphs:
        story.append(Paragraph(p_text, body_style))
    
    doc.build(story)

    # Extract text and count pages using pdfplumber
    extracted_text = ""
    page_count = 1
    with pdfplumber.open(filepath) as pdf:
        page_count = len(pdf.pages)
        for page in pdf.pages:
            t = page.extract_text()
            if t:
                extracted_text += t + "\n"
    
    return page_count, extracted_text.strip()

print("Generating synthetic PDF records and SQL seed...")
