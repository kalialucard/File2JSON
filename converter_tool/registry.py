"""
Registry for mapping file types to converter classes.
"""

from typing import Dict, Type

from .base_converter import BaseConverter
from .converters import (
    ArchiveConverter,
    BinaryConverter,
    CsvConverter,
    DocxConverter,
    EvtxConverter,
    JsonConverter,
    PcapConverter,
    PdfConverter,
    TextConverter,
    XmlConverter,
)

# Map detected types to converter classes
CONVERTER_REGISTRY: Dict[str, Type[BaseConverter]] = {
    'evtx': EvtxConverter,
    'pcap': PcapConverter,
    'pcapng': PcapConverter,
    'csv': CsvConverter,
    'json': JsonConverter,
    'xml': XmlConverter,
    'txt': TextConverter,
    'pdf': PdfConverter,
    'docx': DocxConverter,
    'zip': ArchiveConverter,
    'tar': ArchiveConverter,
    'gzip': ArchiveConverter,
    'binary': BinaryConverter,
}


def get_converter(file_type: str) -> Type[BaseConverter]:
    """
    Get converter class for a file type.
    
    Args:
        file_type: Detected file type (e.g., 'evtx', 'pcap', 'csv')
        
    Returns:
        Converter class
    """
    return CONVERTER_REGISTRY.get(file_type, BinaryConverter)

