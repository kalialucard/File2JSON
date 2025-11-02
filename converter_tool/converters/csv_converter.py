"""
Converter for CSV files.
"""

import csv
import logging
from pathlib import Path
from typing import Any, Dict, List

from ..base_converter import BaseConverter

logger = logging.getLogger(__name__)


class CsvConverter(BaseConverter):
    """Converter for CSV files."""
    
    def _extract_data(self, file_path: Path, **kwargs) -> Dict[str, Any]:
        """
        Extract rows from CSV file.
        
        Returns:
            Dictionary with 'rows' array and 'column_names'
        """
        rows = []
        column_names = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                # Try to detect delimiter
                sample = f.read(1024)
                f.seek(0)
                
                sniffer = csv.Sniffer()
                delimiter = sniffer.sniff(sample).delimiter
                
                reader = csv.DictReader(f, delimiter=delimiter)
                column_names = reader.fieldnames or []
                
                for row in reader:
                    rows.append(dict(row))
        
        except Exception as e:
            logger.error(f"Error reading CSV file {file_path}: {e}")
            raise
        
        return {
            "column_names": column_names,
            "row_count": len(rows),
            "rows": rows,
        }

