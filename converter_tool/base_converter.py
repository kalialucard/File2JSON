"""
Base converter class that all format-specific converters inherit from.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from .utils import extract_metadata

logger = logging.getLogger(__name__)


class BaseConverter:
    """Base class for all file format converters."""
    
    def __init__(self, include_base64: bool = False, base64_limit: int = 1024 * 1024):
        """
        Initialize converter.
        
        Args:
            include_base64: Whether to include base64 encoded content for binary files
            base64_limit: Maximum size (in bytes) to include base64 preview
        """
        self.include_base64 = include_base64
        self.base64_limit = base64_limit
    
    def convert(self, file_path: Path, **kwargs) -> Dict[str, Any]:
        """
        Convert a file to JSON-serializable structure.
        
        Args:
            file_path: Path to the input file
            **kwargs: Additional format-specific parameters
            
        Returns:
            Dictionary following the standard output schema
        """
        file_path = Path(file_path)
        detected_type, mimetype = self._detect_type(file_path)
        
        try:
            metadata = extract_metadata(file_path, include_hashes=True)
            # Convert mtime to ISO8601
            if metadata.get("mtime"):
                metadata["mtime_iso"] = datetime.fromtimestamp(
                    metadata["mtime"]
                ).isoformat()
            
            data = self._extract_data(file_path, **kwargs)
            
            return {
                "source_filename": file_path.name,
                "source_path": str(file_path.absolute()),
                "detected_type": detected_type,
                "mimetype": mimetype,
                "converted_at": datetime.utcnow().isoformat() + "Z",
                "metadata": metadata,
                "data": data,
            }
        except Exception as e:
            logger.error(f"Error converting {file_path}: {e}", exc_info=True)
            raise
    
    def _detect_type(self, file_path: Path) -> tuple:
        """Detect file type - implemented by base class using utils."""
        from .utils import detect_file_type
        return detect_file_type(file_path)
    
    def _extract_data(self, file_path: Path, **kwargs) -> Any:
        """
        Extract data from file - must be implemented by subclasses.
        
        Args:
            file_path: Path to the file
            **kwargs: Format-specific parameters
            
        Returns:
            JSON-serializable data structure
        """
        raise NotImplementedError("Subclasses must implement _extract_data")
    
    def save_json(self, output_path: Path, data: Dict[str, Any], pretty: bool = True) -> None:
        """
        Save converted data to JSON file.
        
        Args:
            output_path: Path to output JSON file
            data: Dictionary to save
            pretty: Whether to pretty-print JSON
        """
        from .utils import ensure_output_dir
        ensure_output_dir(output_path)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            if pretty:
                json.dump(data, f, indent=2, ensure_ascii=False)
            else:
                json.dump(data, f, ensure_ascii=False)
        
        logger.debug(f"Saved JSON to {output_path}")

