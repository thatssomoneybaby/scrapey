import tempfile
import os
import logging
from PIL import Image
import numpy as np
from tkinter import messagebox
from scrapey.utils import app_settings
from pdf2image import convert_from_path

def perform_ocr(image_path, engine='tesseract'):
    """
    Extract text from an image using the specified OCR engine.
    Supported engines: tesseract, easyocr.
    This version converts the image to grayscale before performing OCR.
    """
    try:
        # Convert image to grayscale
        with Image.open(image_path) as img:
            gray = img.convert('L')
            
            # Save grayscale image to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp:
                temp_path = tmp.name
                gray.save(temp_path)
        
        text = ""
        if engine.lower() == 'tesseract':
            import pytesseract
            logging.info("Using Tesseract OCR engine")
            text = pytesseract.image_to_string(
                temp_path,
                lang=app_settings.get('ocr_language', 'eng')
            )
        elif engine.lower() == 'easyocr':
            try:
                import easyocr
                logging.info("Using EasyOCR engine")
                reader = easyocr.Reader([app_settings.get('ocr_language', 'en')])
                result = reader.readtext(temp_path)
                text = "\n".join([item[1] for item in result])
            except ImportError:
                logging.error("easyocr import failed")
                messagebox.showerror(
                    "Missing Dependency",
                    "easyocr is not installed. Please install it to use EasyOCR.\n\n"
                    "Try: pip install easyocr"
                )
                return ""
    except Exception as e:
        logging.exception("Error during OCR:")
        raise
    finally:
        # Clean up temporary file
        os.remove(temp_path)
    return text

def ocr_scanned_pdf(pdf_path, engine='tesseract', page_range=None):
    """
    Convert each page of a scanned PDF to an image, then run OCR on each page.
    Requires pdf2image and poppler to be installed.
    """
    try:
        # Convert PDF pages to images
        images = convert_from_path(pdf_path)
        total_pages = len(images)
        
        # Determine page range
        if page_range:
            start_page = max(0, page_range[0] - 1)  # Convert to 0-based
            end_page = min(total_pages, page_range[1])  # Already 1-based
        else:
            start_page = 0
            end_page = total_pages
            
        text_parts = []
        for page_num in range(start_page, end_page):
            # Save page image to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp:
                temp_path = tmp.name
                images[page_num].save(temp_path, 'PNG')
                
            # Perform OCR on the page
            text = perform_ocr(temp_path, engine)
            if text:
                text_parts.append(f"=== Page {page_num + 1} ===\n{text}\n")
                
            # Clean up temporary file
            os.remove(temp_path)
            
        return "\n".join(text_parts)
        
    except Exception as e:
        logging.exception("Error during PDF OCR:")
        raise 