"""
Resume Parser Tool wrapping PyMuPDF for reliable text extraction.
Handles PDF file paths, byte streams, UploadedFiles, and plain text resumes gracefully.
"""
import os
from typing import Union, BinaryIO
from resume.parser import extract_text_from_pdf

def parse_pdf_resume(source: Union[str, bytes, BinaryIO]) -> str:
    """
    Extracts text from a PDF resume file or returns text directly if already a string.
    Supports file path, bytes, or file-like object.
    """
    if source is None:
        raise ValueError("No resume source provided for extraction.")

    if isinstance(source, str):
        # If string is an existing file path, parse via PyMuPDF
        if os.path.exists(source):
            return extract_text_from_pdf(source)
        # If string starts with PDF header
        elif source.startswith("%PDF"):
            return extract_text_from_pdf(source.encode("latin-1"))
        # If already extracted resume text
        elif len(source.strip()) > 0:
            return source.strip()
        else:
            raise ValueError("Provided resume string is empty.")

    return extract_text_from_pdf(source)
