"""
Converter for Windows Event Log (.evtx) files.
"""

import logging
from pathlib import Path
from typing import Any, Dict

from ..base_converter import BaseConverter

logger = logging.getLogger(__name__)


class EvtxConverter(BaseConverter):
    """Converter for Windows EVTX files."""
    
    def _extract_data(self, file_path: Path, **kwargs) -> Dict[str, Any]:
        """
        Extract records from EVTX file.
        
        Returns:
            Dictionary with 'records' array containing event records
        """
        try:
            import Evtx.Evtx as evtx
            import Evtx.Views as evtx_views
        except ImportError:
            raise ImportError(
                "python-evtx is required for .evtx files. "
                "Install with: pip install python-evtx"
            )
        
        records = []
        
        try:
            with open(str(file_path), 'rb') as f:
                evtx_file = evtx.Evtx(f)
                for record in evtx_file.records():
                    try:
                        event = evtx_views.evtx_record_xml_view(record)
                        
                        # Parse XML to extract key fields
                        import xml.etree.ElementTree as ET
                        root = ET.fromstring(event)
                        
                        # Extract EventID
                        event_id = None
                        event_id_elem = root.find('.//{http://schemas.microsoft.com/win/2004/08/events/event}EventID')
                        if event_id_elem is not None:
                            event_id = event_id_elem.text
                        
                        # Extract TimeCreated
                        time_created = None
                        time_elem = root.find('.//{http://schemas.microsoft.com/win/2004/08/events/event}TimeCreated')
                        if time_elem is not None:
                            time_created = time_elem.get('SystemTime')
                        
                        # Extract EventRecordID
                        event_record_id = None
                        record_id_elem = root.find('.//{http://schemas.microsoft.com/win/2004/08/events/event}EventRecordID')
                        if record_id_elem is not None:
                            event_record_id = record_id_elem.text
                        
                        # Extract all Data elements
                        data_dict = {}
                        for data_elem in root.findall('.//{http://schemas.microsoft.com/win/2004/08/events/event}Data'):
                            name = data_elem.get('Name')
                            value = data_elem.text
                            if name:
                                data_dict[name] = value
                        
                        record_obj = {
                            "EventID": event_id,
                            "TimeCreated": time_created,
                            "EventRecordID": event_record_id,
                            "data": data_dict,
                            "xml": event,  # Include full XML for reference
                        }
                        records.append(record_obj)
                        
                    except Exception as e:
                        logger.warning(f"Error parsing EVTX record: {e}")
                        continue
                        
        except Exception as e:
            logger.error(f"Error reading EVTX file {file_path}: {e}")
            raise
        
        return {
            "record_count": len(records),
            "records": records,
        }

