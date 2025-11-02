"""Tests for utility functions."""

import tempfile
from pathlib import Path

import pytest

from converter.utils import detect_file_type, extract_metadata


def test_detect_file_type_csv():
    """Test file type detection for CSV."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write("test,data\n")
        temp_path = Path(f.name)
    
    try:
        detected_type, mimetype = detect_file_type(temp_path)
        assert detected_type == "csv"
    finally:
        temp_path.unlink()


def test_detect_file_type_json():
    """Test file type detection for JSON."""
    import json
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump({"test": "data"}, f)
        temp_path = Path(f.name)
    
    try:
        detected_type, mimetype = detect_file_type(temp_path)
        assert detected_type == "json"
    finally:
        temp_path.unlink()


def test_extract_metadata():
    """Test metadata extraction."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("test content")
        temp_path = Path(f.name)
    
    try:
        metadata = extract_metadata(temp_path, include_hashes=True)
        
        assert "size" in metadata
        assert "mtime" in metadata
        assert "sha256" in metadata
        assert "sha1" in metadata
        assert "md5" in metadata
        assert metadata["size"] > 0
    finally:
        temp_path.unlink()

