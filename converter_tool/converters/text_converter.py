"""
Converter for plain text and log files.
"""

import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

from ..base_converter import BaseConverter

logger = logging.getLogger(__name__)


class TextConverter(BaseConverter):
    """Converter for text/log files."""
    
    # Regex patterns for timestamp detection
    ISO8601_PATTERN = re.compile(
        r'\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})?'
    )
    EPOCH_PATTERN = re.compile(r'\b\d{10}(?:\.\d+)?\b')
    
    def _extract_data(self, file_path: Path, **kwargs) -> Dict[str, Any]:
        """
        Extract lines from text file with optional timestamp detection.
        
        Returns:
            Dictionary with 'lines' array
        """
        lines = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                for line_num, line_text in enumerate(f, start=1):
                    line_obj = {
                        "line_number": line_num,
                        "text": line_text.rstrip('\n\r'),
                    }
                    
                    # Try to extract timestamp
                    timestamp = self._extract_timestamp(line_text)
                    if timestamp:
                        line_obj["timestamp"] = timestamp
                        line_obj["timestamp_format"] = timestamp.get("format")
                    
                    lines.append(line_obj)
        
        except Exception as e:
            logger.error(f"Error reading text file {file_path}: {e}")
            raise
        
        return {
            "line_count": len(lines),
            "lines": lines,
        }
    
    def _extract_timestamp(self, text: str) -> Dict[str, Any]:
        """
        Extract timestamp from text line if present.
        
        Args:
            text: Line of text
            
        Returns:
            Dictionary with timestamp info or None
        """
        # Try ISO8601 pattern
        iso_match = self.ISO8601_PATTERN.search(text)
        if iso_match:
            try:
                ts_str = iso_match.group()
                # Try parsing as ISO8601
                if 'T' in ts_str:
                    dt = datetime.fromisoformat(ts_str.replace('Z', '+00:00'))
                else:
                    dt = datetime.fromisoformat(ts_str)
                
                return {
                    "value": dt.isoformat(),
                    "raw": ts_str,
                    "format": "iso8601",
                }
            except Exception:
                pass
        
        # Try epoch pattern
        epoch_match = self.EPOCH_PATTERN.search(text)
        if epoch_match:
            try:
                epoch_float = float(epoch_match.group())
                dt = datetime.fromtimestamp(epoch_float)
                return {
                    "value": dt.isoformat(),
                    "raw": epoch_match.group(),
                    "format": "epoch",
                }
            except (ValueError, OSError):
                pass
        
        return None

