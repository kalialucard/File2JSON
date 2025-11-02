"""
Converter for JSON files (validation and pretty-printing).
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict

from ..base_converter import BaseConverter

logger = logging.getLogger(__name__)


class JsonConverter(BaseConverter):
    """Converter for JSON files."""
    
    def _extract_data(self, file_path: Path, **kwargs) -> Any:
        """
        Load and validate JSON file.
        
        Returns:
            The parsed JSON data
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in file {file_path}: {e}")
            raise ValueError(f"Invalid JSON: {e}")
        except Exception as e:
            logger.error(f"Error reading JSON file {file_path}: {e}")
            raise
        
        return data

