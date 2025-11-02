"""
Converter for PDF files.
"""

import logging
from pathlib import Path
from typing import Any, Dict

from ..base_converter import BaseConverter

logger = logging.getLogger(__name__)


class PdfConverter(BaseConverter):
    """Converter for PDF files."""
    
    def _extract_data(self, file_path: Path, **kwargs) -> Dict[str, Any]:
        """
        Extract text and metadata from PDF.
        
        Returns:
            Dictionary with pages array and metadata
        """
        # Try pdfminer.six first
        try:
            return self._extract_with_pdfminer(file_path)
        except ImportError:
            logger.debug("pdfminer.six not available, trying PyPDF2")
        
        # Fallback to PyPDF2
        try:
            return self._extract_with_pypdf2(file_path)
        except ImportError:
            raise ImportError(
                "Either pdfminer.six or PyPDF2 is required for .pdf files. "
                "Install with: pip install pdfminer.six or pip install PyPDF2"
            )
    
    def _extract_with_pdfminer(self, file_path: Path) -> Dict[str, Any]:
        """Extract using pdfminer.six."""
        from pdfminer.high_level import extract_text, extract_pages
        from pdfminer.layout import LTTextContainer
        
        pages = []
        
        try:
            # Extract text per page
            for page_num, page_layout in enumerate(extract_pages(str(file_path)), start=1):
                page_text = ""
                for element in page_layout:
                    if isinstance(element, LTTextContainer):
                        page_text += element.get_text()
                
                pages.append({
                    "page_number": page_num,
                    "text": page_text.strip(),
                })
            
            # Get total page count
            full_text = extract_text(str(file_path))
            
        except Exception as e:
            logger.error(f"Error reading PDF with pdfminer {file_path}: {e}")
            raise
        
        return {
            "page_count": len(pages),
            "pages": pages,
            "extraction_method": "pdfminer.six",
        }
    
    def _extract_with_pypdf2(self, file_path: Path) -> Dict[str, Any]:
        """Extract using PyPDF2."""
        import PyPDF2
        
        pages = []
        
        try:
            with open(file_path, 'rb') as f:
                pdf_reader = PyPDF2.PdfReader(f)
                page_count = len(pdf_reader.pages)
                
                for page_num, page in enumerate(pdf_reader.pages, start=1):
                    text = page.extract_text()
                    pages.append({
                        "page_number": page_num,
                        "text": text.strip(),
                    })
        
        except Exception as e:
            logger.error(f"Error reading PDF with PyPDF2 {file_path}: {e}")
            raise
        
        return {
            "page_count": page_count,
            "pages": pages,
            "extraction_method": "PyPDF2",
        }

