# exams/ocr.py

import pytesseract
from PIL import Image
from pdf2image import convert_from_path
import tempfile
import re
from typing import Dict

# Optional: Explicit path if tesseract is not in PATH (use absolute path if needed)
pytesseract.pytesseract.tesseract_cmd = 'tesseract'


def extract_text_from_image(image_path: str) -> str:
    """
    Extracts and cleans text from a single image file using OCR.
    """
    try:
        img = Image.open(image_path)
        raw_text = pytesseract.image_to_string(img)
        return clean_text(raw_text)
    except Exception as e:
        raise RuntimeError(f"OCR image extraction failed: {str(e)}")


def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Converts each page of a PDF into text using OCR and returns combined clean text.
    """
    try:
        pages = convert_from_path(pdf_path, dpi=300)
        full_text = ""

        for i, page in enumerate(pages):
            with tempfile.NamedTemporaryFile(suffix='.png', delete=True) as temp_img:
                page.save(temp_img.name, 'PNG')
                page_text = pytesseract.image_to_string(Image.open(temp_img.name))
                full_text += f"\n--- PAGE {i + 1} ---\n{page_text.strip()}\n"

        return clean_text(full_text)

    except Exception as e:
        raise RuntimeError(f"OCR PDF extraction failed: {str(e)}")


def clean_text(text: str) -> str:
    """
    Cleans OCR text output for better AI ingestion or metadata parsing.
    - Normalizes whitespace
    - Fixes common OCR misreads (O vs 0, l vs 1, dashes, etc.)
    - Strips non-ASCII (optional)
    """
    text = re.sub(r'\s+', ' ', text)  # Collapse whitespace
    text = re.sub(r'[^\x00-\x7F]+', '', text)  # Remove non-ASCII characters
    text = re.sub(r'\bO\b', '0', text)  # Fix misread O as 0
    text = re.sub(r'\bl\b', '1', text)  # Fix misread l as 1
    text = re.sub(r'[—–]', '-', text)  # Normalize dash types
    return text.strip()


def extract_exam_metadata(text: str) -> Dict[str, str]:
    """
    Infers exam metadata from OCR’d text.
    Returns:
        {
            'subject': str | None,
            'year': int | None,
            'term': str | None,
            'title': str
        }
    """
    metadata = {
        'subject': None,
        'year': None,
        'term': None,
        'title': None,
    }

    subject_match = re.search(r"\b(Mathematics|English|Science|Kiswahili|Biology|Chemistry|Physics|History|Geography|CRE|IRE)\b", text, re.IGNORECASE)
    year_match = re.search(r"\b(20\d{2})\b", text)
    term_match = re.search(r"\bTerm\s*(1|2|3)\b", text, re.IGNORECASE)

    if subject_match:
        metadata['subject'] = subject_match.group(1).title()

    if year_match:
        metadata['year'] = int(year_match.group(1))

    if term_match:
        metadata['term'] = f"Term {term_match.group(1)}"

    if metadata['subject'] and metadata['term'] and metadata['year']:
        metadata['title'] = f"{metadata['subject']} - {metadata['term']} {metadata['year']}"
    else:
        metadata['title'] = "Unknown Exam"

    return metadata
