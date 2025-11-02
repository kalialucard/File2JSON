"""
Converter for Microsoft Word (.docx) files.
"""

import logging
from pathlib import Path
from typing import Any, Dict

from ..base_converter import BaseConverter

logger = logging.getLogger(__name__)


class DocxConverter(BaseConverter):
    """Converter for DOCX files."""
    
    def _extract_data(self, file_path: Path, **kwargs) -> Dict[str, Any]:
        """
        Extract paragraphs from DOCX file.
        
        Returns:
            Dictionary with paragraphs array
        """
        try:
            from docx import Document
        except ImportError:
            raise ImportError(
                "python-docx is required for .docx files. "
                "Install with: pip install python-docx"
            )
        
        paragraphs = []
        
        try:
            doc = Document(str(file_path))
            
            for para_num, paragraph in enumerate(doc.paragraphs, start=1):
                text = paragraph.text.strip()
                if text:  # Only include non-empty paragraphs
                    para_obj = {
                        "paragraph_number": para_num,
                        "text": text,
                        "style": paragraph.style.name if paragraph.style else None,
                    }
                    paragraphs.append(para_obj)
        
        except Exception as e:
            logger.error(f"Error reading DOCX file {file_path}: {e}")
            raise
        
        return {
            "paragraph_count": len(paragraphs),
            "paragraphs": paragraphs,
        }

