"""Tests for text/log converter."""

import tempfile
from datetime import datetime
from pathlib import Path

import pytest

from converter.converters.text_converter import TextConverter


def test_text_conversion():
    """Test text file conversion."""
    text_content = "Line 1\nLine 2\nLine 3\n"
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(text_content)
        temp_path = Path(f.name)
    
    try:
        converter = TextConverter()
        result = converter.convert(temp_path)
        
        assert result["detected_type"] == "txt"
        data = result["data"]
        assert data["line_count"] == 3
        assert len(data["lines"]) == 3
        assert data["lines"][0]["line_number"] == 1
        assert data["lines"][0]["text"] == "Line 1"
    finally:
        temp_path.unlink()


def test_text_with_timestamp():
    """Test text file with ISO8601 timestamp."""
    text_content = "2024-01-15T10:30:00Z - Log message here\n"
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f:
        f.write(text_content)
        temp_path = Path(f.name)
    
    try:
        converter = TextConverter()
        result = converter.convert(temp_path)
        
        data = result["data"]
        assert data["lines"][0]["timestamp"] is not None
        assert data["lines"][0]["timestamp"]["format"] == "iso8601"
    finally:
        temp_path.unlink()

