"""Tests for XML converter."""

import tempfile
from pathlib import Path

import pytest

from converter.converters.xml_converter import XmlConverter


def test_xml_conversion():
    """Test XML file conversion."""
    xml_content = '<?xml version="1.0"?><root><item id="1">Value</item></root>'
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
        f.write(xml_content)
        temp_path = Path(f.name)
    
    try:
        converter = XmlConverter()
        result = converter.convert(temp_path)
        
        assert result["detected_type"] == "xml"
        data = result["data"]
        assert data["tag"] == "root"
        assert len(data["children"]) == 1
        assert data["children"][0]["tag"] == "item"
        assert data["children"][0]["attributes"]["id"] == "1"
    finally:
        temp_path.unlink()


def test_xml_invalid():
    """Test invalid XML handling."""
    invalid_xml = '<root><unclosed></root>'
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
        f.write(invalid_xml)
        temp_path = Path(f.name)
    
    try:
        converter = XmlConverter()
        with pytest.raises(ValueError):
            converter.convert(temp_path)
    finally:
        temp_path.unlink()

