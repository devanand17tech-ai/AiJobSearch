import pymupdf as fitz  # PyMuPDF
import re
from typing import Union, BinaryIO

def extract_text_from_pdf(source: Union[str, bytes, BinaryIO]) -> str:
    """
    Extracts and cleans text from a PDF resume using PyMuPDF (fitz).
    
    Args:
        source: File path (str), raw bytes (bytes), or file-like object (BinaryIO)
        
    Returns:
        Cleaned text extracted from all pages of the PDF.
        
    Raises:
        ValueError: If PDF is invalid, empty, or unreadable.
    """
    if source is None:
        raise ValueError("No file provided for PDF extraction.")

    try:
        if isinstance(source, str):
            doc = fitz.open(source)
        elif isinstance(source, bytes):
            doc = fitz.open(stream=source, filetype="pdf")
        elif hasattr(source, "read"):
            # File-like object (e.g. Streamlit UploadedFile)
            source.seek(0)
            file_bytes = source.read()
            if not file_bytes:
                raise ValueError("Uploaded file is empty (0 bytes).")
            doc = fitz.open(stream=file_bytes, filetype="pdf")
        else:
            raise ValueError("Unsupported source format for PDF extraction.")

        if doc.page_count == 0:
            raise ValueError("PDF document has 0 pages.")

        full_text = []
        for page_num in range(doc.page_count):
            page = doc.load_page(page_num)
            text = page.get_text("text")
            if text:
                full_text.append(text)

        doc.close()

        extracted = "\n".join(full_text)
        
        # Clean unnecessary whitespace and control characters
        cleaned = re.sub(r'[ \t]+', ' ', extracted)  # Collapse multiple spaces
        cleaned = re.sub(r'\n\s*\n', '\n\n', cleaned)  # Normalize multi-newlines
        cleaned = cleaned.strip()

        if not cleaned:
            raise ValueError("No text could be extracted from the PDF (the file may be scanned/image-only or blank).")

        return cleaned

    except fitz.FileDataError as e:
        raise ValueError(f"Invalid or corrupted PDF file: {str(e)}")
    except Exception as e:
        if isinstance(e, ValueError):
            raise e
        raise ValueError(f"Failed to extract text from PDF: {str(e)}")
