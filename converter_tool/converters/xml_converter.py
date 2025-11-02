"""
Converter for XML files.
"""

import logging
from pathlib import Path
from typing import Any, Dict

from ..base_converter import BaseConverter

logger = logging.getLogger(__name__)


class XmlConverter(BaseConverter):
    """Converter for XML files."""
    
    def _extract_data(self, file_path: Path, **kwargs) -> Dict[str, Any]:
        """
        Parse XML file and convert to JSON-friendly structure.
        
        Returns:
            Dictionary representation of XML tree
        """
        import xml.etree.ElementTree as ET
        
        try:
            tree = ET.parse(str(file_path))
            root = tree.getroot()
            return self._element_to_dict(root)
        except ET.ParseError as e:
            logger.error(f"Invalid XML in file {file_path}: {e}")
            raise ValueError(f"Invalid XML: {e}")
        except Exception as e:
            logger.error(f"Error reading XML file {file_path}: {e}")
            raise
    
    def _element_to_dict(self, element) -> Dict[str, Any]:
        """
        Convert XML element to dictionary recursively.
        
        Args:
            element: XML Element object
            
        Returns:
            Dictionary representation
        """
        result = {
            "tag": element.tag,
            "attributes": dict(element.attrib),
            "text": element.text.strip() if element.text and element.text.strip() else None,
        }
        
        children = []
        for child in element:
            children.append(self._element_to_dict(child))
        
        if children:
            result["children"] = children
        
        # Handle mixed content (text + elements)
        tail = element.tail.strip() if element.tail and element.tail.strip() else None
        if tail:
            result["tail"] = tail
        
        return result

