"""Tests for CSV converter."""

import json
import tempfile
from pathlib import Path

import pytest

from converter.converters.csv_converter import CsvConverter


def test_csv_conversion():
    """Test CSV file conversion."""
    # Create a test CSV file
    csv_content = "name,age,city\nAlice,30,New York\nBob,25,San Francisco\n"
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write(csv_content)
        temp_path = Path(f.name)
    
    try:
        converter = CsvConverter()
        result = converter.convert(temp_path)
        
        assert result["detected_type"] == "csv"
        assert result["source_filename"] == temp_path.name
        assert "data" in result
        
        data = result["data"]
        assert data["row_count"] == 2
        assert len(data["rows"]) == 2
        assert data["rows"][0]["name"] == "Alice"
        assert data["rows"][0]["age"] == "30"
        assert data["rows"][1]["name"] == "Bob"
    finally:
        temp_path.unlink()


def test_csv_empty():
    """Test CSV with only headers."""
    csv_content = "name,age\n"
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write(csv_content)
        temp_path = Path(f.name)
    
    try:
        converter = CsvConverter()
        result = converter.convert(temp_path)
        
        data = result["data"]
        assert data["row_count"] == 0
        assert len(data["rows"]) == 0
    finally:
        temp_path.unlink()

