import logging
import PyPDF2

def get_pdf_page_count(file_path):
    """Get the number of pages in a PDF file.
    
    Args:
        file_path: Path to the PDF file
        
    Returns:
        int: Number of pages in the PDF
    """
    try:
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            return len(reader.pages)
    except Exception as e:
        logging.exception(f"Error getting page count from {file_path}:")
        raise

def extract_pdf_text(file_path, page_range=None):
    """Extract text from a PDF file.
    
    Args:
        file_path: Path to the PDF file
        page_range: Optional tuple of (start_page, end_page) for page range (1-based)
        
    Returns:
        str: Extracted text from the PDF
    """
    try:
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            total_pages = len(reader.pages)
            
            # Determine page range
            if page_range:
                start_page = max(0, page_range[0] - 1)  # Convert to 0-based
                end_page = min(total_pages, page_range[1])  # Already 1-based
            else:
                start_page = 0
                end_page = total_pages
            
            # Extract text from each page
            text_parts = []
            for page_num in range(start_page, end_page):
                page = reader.pages[page_num]
                text = page.extract_text()
                if text:
                    text_parts.append(f"=== Page {page_num + 1} ===\n{text}\n")
            
            return "\n".join(text_parts)
            
    except Exception as e:
        logging.exception(f"Error extracting text from {file_path}:")
        raise 