"""Tests for JSON converter."""

import json
import tempfile
from pathlib import Path

import pytest

from converter.converters.json_converter import JsonConverter


def test_json_conversion():
    """Test JSON file conversion."""
    json_data = {"name": "test", "values": [1, 2, 3]}
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(json_data, f)
        temp_path = Path(f.name)
    
    try:
        converter = JsonConverter()
        result = converter.convert(temp_path)
        
        assert result["detected_type"] == "json"
        assert result["data"] == json_data
    finally:
        temp_path.unlink()


def test_json_invalid():
    """Test invalid JSON handling."""
    invalid_json = '{"name": "test", invalid}'
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        f.write(invalid_json)
        temp_path = Path(f.name)
    
    try:
        converter = JsonConverter()
        with pytest.raises(ValueError):
            converter.convert(temp_path)
    finally:
        temp_path.unlink()

