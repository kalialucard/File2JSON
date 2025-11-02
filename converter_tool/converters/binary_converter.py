"""
Converter for unknown binary files (metadata extraction only).
"""

import base64
import logging
from pathlib import Path
from typing import Any, Dict

from ..base_converter import BaseConverter

logger = logging.getLogger(__name__)


class BinaryConverter(BaseConverter):
    """Converter for unknown binary files (metadata only)."""
    
    def _extract_data(self, file_path: Path, **kwargs) -> Dict[str, Any]:
        """
        Extract metadata for binary file, optionally including base64 preview.
        
        Returns:
            Dictionary with metadata and optional base64 preview
        """
        file_path = Path(file_path)
        stat = file_path.stat()
        
        data = {
            "binary_type": "unknown",
            "size": stat.st_size,
            "has_preview": False,
        }
        
        # Include base64 preview if requested and file is small enough
        if self.include_base64 and stat.st_size <= self.base64_limit:
            try:
                with open(file_path, 'rb') as f:
                    content = f.read()
                    data["base64_preview"] = base64.b64encode(content).decode('utf-8')
                    data["has_preview"] = True
            except Exception as e:
                logger.warning(f"Error reading file for base64 preview: {e}")
        
        return data

