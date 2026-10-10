import os
import io
import logging
import base64
from typing import Dict, Any, List
import pdfplumber
import httpx
from PIL import Image

from app.core.config import settings

logger = logging.getLogger(__name__)

class PDFExtractor:
    @staticmethod
    def extract_text_and_provenance(filepath: str, mime_type: str = "application/pdf") -> Dict[str, Any]:
        """
        Extracts page-level text and provenance from text PDFs, scanned PDFs, or images (PNG/JPEG).
        Returns:
        {
          "status": "processed" | "failed",
          "extracted_text": str,
          "page_count": int,
          "provenance": "pypdf_text" | "gemini_vision_pdf" | "gemini_vision_image" | "pytesseract_ocr",
          "pages": [{"page_number": int, "text": str}],
          "error": str | None
        }
        """
        if not os.path.exists(filepath):
            logger.error(f"File not found for extraction: {filepath}")
            return {
                "status": "failed",
                "extracted_text": "",
                "page_count": 0,
                "provenance": "none",
                "pages": [],
                "error": "File not found"
            }

        mime_lower = (mime_type or "").lower()
        is_image = "image" in mime_lower or filepath.lower().endswith((".png", ".jpg", ".jpeg"))

        if is_image:
            return PDFExtractor._extract_image(filepath)
        else:
            return PDFExtractor._extract_pdf(filepath)

    @staticmethod
    def _ocr_pil_image_via_gemini(pil_img: Image.Image) -> tuple[str, str]:
        """Performs OCR on a PIL image using Gemini 3.5 Flash Lite Vision API with fallback to PyTesseract."""
        gemini_key = (settings.GEMINI_API_KEY or "").strip()
        if gemini_key and "placeholder" not in gemini_key and "your-" not in gemini_key:
            try:
                img_byte_arr = io.BytesIO()
                pil_img.save(img_byte_arr, format='PNG')
                b64_img = base64.b64encode(img_byte_arr.getvalue()).decode("utf-8")

                model_name = settings.PRIMARY_LLM_MODEL or "gemini-3.5-flash-lite"
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={gemini_key}"
                payload = {
                    "contents": [{
                        "parts": [
                            {"inlineData": {"mimeType": "image/png", "data": b64_img}},
                            {"text": "Perform OCR on this medical document image. Transcribe VISIBLE TEXT ONLY. Do not invent, hallucinate, or assume any dates, values, names, or clinical details that are not explicitly readable in the image. If text is blurry or unreadable, mark it as '[unclear]'. Output ONLY the transcribed visible text string."}
                        ]
                    }],
                    "generationConfig": {"temperature": 0.0}
                }
                res = httpx.post(url, json=payload, timeout=15.0)
                if res.status_code == 200:
                    g_data = res.json()
                    parts = g_data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])
                    txt = parts[0].get("text", "").strip()
                    if txt:
                        return txt, "gemini_vision"
            except Exception as exc:
                logger.warning(f"Gemini Vision OCR attempt failed: {exc}")

        # Local PyTesseract fallback (only if executable binary is installed)
        try:
            import pytesseract
            import shutil
            if shutil.which("tesseract") is not None or os.path.exists(pytesseract.pytesseract.tesseract_cmd):
                txt = pytesseract.image_to_string(pil_img).strip()
                if txt:
                    return txt, "pytesseract"
        except Exception as exc:
            logger.debug(f"PyTesseract execution skipped/unavailable: {exc}")

        return "", "none"

    @staticmethod
    def _extract_image(filepath: str) -> Dict[str, Any]:
        try:
            img = Image.open(filepath)
            txt, prov = PDFExtractor._ocr_pil_image_via_gemini(img)
            if txt:
                return {
                    "status": "processed",
                    "extracted_text": txt,
                    "page_count": 1,
                    "provenance": f"{prov}_image",
                    "pages": [{"page_number": 1, "text": txt}],
                    "error": None
                }

            return {
                "status": "failed",
                "extracted_text": "",
                "page_count": 1,
                "provenance": "scanned_image_failed",
                "pages": [],
                "error": "OCR engine unavailable or no readable text detected in image. Staff review required."
            }
        except Exception as exc:
            logger.error(f"Image extraction failure for {filepath}: {exc}")
            return {
                "status": "failed",
                "extracted_text": "",
                "page_count": 0,
                "provenance": "scanned_image_failed",
                "pages": [],
                "error": f"Image processing error: {str(exc)}"
            }

    @staticmethod
    def _extract_pdf(filepath: str) -> Dict[str, Any]:
        try:
            pages_list: List[Dict[str, Any]] = []
            pages_text: List[str] = []
            
            with pdfplumber.open(filepath) as pdf:
                page_count = len(pdf.pages)
                for idx, page in enumerate(pdf.pages, start=1):
                    txt = (page.extract_text() or "").strip()
                    pages_list.append({"page_number": idx, "text": txt})
                    if txt:
                        pages_text.append(f"--- Page {idx} ---\n{txt}")

            full_text = "\n\n".join(pages_text).strip()

            # If text PDF extraction succeeded
            if full_text and len(full_text) >= 15:
                return {
                    "status": "processed",
                    "extracted_text": full_text,
                    "page_count": page_count,
                    "provenance": "pypdf_text",
                    "pages": pages_list,
                    "error": None
                }

            # Scanned PDF Fallback: Render pages to PIL image and run OCR
            ocr_pages_list: List[Dict[str, Any]] = []
            ocr_pages_text: List[str] = []
            ocr_prov_used = "none"

            try:
                import pypdfium2 as pdfium
                pdf_doc = pdfium.PdfDocument(filepath)
                for idx, page in enumerate(pdf_doc, start=1):
                    pil_image = page.render(scale=2).to_pil()
                    txt, prov = PDFExtractor._ocr_pil_image_via_gemini(pil_image)
                    if txt:
                        ocr_prov_used = prov
                        ocr_pages_list.append({"page_number": idx, "text": txt})
                        ocr_pages_text.append(f"--- Page {idx} ---\n{txt}")

                full_ocr_text = "\n\n".join(ocr_pages_text).strip()
                if full_ocr_text:
                    return {
                        "status": "processed",
                        "extracted_text": full_ocr_text,
                        "page_count": len(pdf_doc),
                        "provenance": f"{ocr_prov_used}_pdf",
                        "pages": ocr_pages_list,
                        "error": None
                    }
            except Exception as ocr_exc:
                logger.warning(f"PDFium render OCR fallback failed: {ocr_exc}")

            return {
                "status": "failed",
                "extracted_text": "",
                "page_count": page_count,
                "provenance": "pypdf_text",
                "pages": [],
                "error": "No readable text extracted from PDF file. Staff review required."
            }

        except Exception as exc:
            logger.error(f"Extraction exception for {filepath}: {str(exc)}")
            return {
                "status": "failed",
                "extracted_text": "",
                "page_count": 0,
                "provenance": "pypdf_text",
                "pages": [],
                "error": str(exc)
            }
