"""
Utility functions for file type detection, metadata extraction, and hashing.
"""

import hashlib
import logging
import os
from pathlib import Path
from typing import Dict, Optional, Tuple

logger = logging.getLogger(__name__)


def detect_file_type(file_path: Path) -> Tuple[str, str]:
    """
    Detect file type using python-magic or filetype, with extension fallback.
    
    Returns:
        Tuple of (detected_type, mimetype)
        detected_type: lowercase extension or generic type (e.g., 'evtx', 'pcap', 'binary')
        mimetype: MIME type string if available, else 'application/octet-stream'
    """
    file_path = Path(file_path)
    extension = file_path.suffix.lower()
    
    # Try python-magic first
    try:
        import magic
        mime = magic.Magic(mime=True)
        mimetype = mime.from_file(str(file_path))
        logger.debug(f"python-magic detected MIME: {mimetype} for {file_path}")
        
        # Map common MIME types to our format types
        mime_to_type = {
            'application/x-evtx': 'evtx',
            'application/vnd.tcpdump.pcap': 'pcap',
            'application/vnd.tcpdump.pcapng': 'pcapng',
            'application/pdf': 'pdf',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'docx',
            'application/zip': 'zip',
            'application/gzip': 'gzip',
            'application/x-tar': 'tar',
            'text/csv': 'csv',
            'application/json': 'json',
            'application/xml': 'xml',
            'text/xml': 'xml',
            'text/plain': 'txt',
        }
        
        detected = mime_to_type.get(mimetype)
        if detected:
            return (detected, mimetype)
    except ImportError:
        logger.debug("python-magic not available, falling back to extension")
    except Exception as e:
        logger.warning(f"python-magic error: {e}, falling back to extension")
    
    # Try filetype library
    try:
        import filetype
        kind = filetype.guess(str(file_path))
        if kind:
            mimetype = kind.mime
            logger.debug(f"filetype detected MIME: {mimetype} for {file_path}")
            
            # Map filetype extensions to our types
            ext_to_type = {
                '.evtx': 'evtx',
                '.pcap': 'pcap',
                '.pcapng': 'pcapng',
            }
            
            detected = ext_to_type.get(f".{kind.extension}")
            if detected:
                return (detected, mimetype)
    except ImportError:
        logger.debug("filetype not available, using extension fallback")
    except Exception as e:
        logger.warning(f"filetype error: {e}, using extension fallback")
    
    # Extension-based fallback
    extension_map = {
        '.evtx': 'evtx',
        '.pcap': 'pcap',
        '.pcapng': 'pcapng',
        '.csv': 'csv',
        '.json': 'json',
        '.xml': 'xml',
        '.log': 'txt',
        '.txt': 'txt',
        '.pdf': 'pdf',
        '.docx': 'docx',
        '.zip': 'zip',
        '.tar': 'tar',
        '.gz': 'gzip',
        '.tgz': 'tar',
    }
    
    # Handle .tar.gz
    if file_path.suffixes[-2:] == ['.tar', '.gz']:
        detected = 'tar'
        mimetype = 'application/x-gzip'
    else:
        detected = extension_map.get(extension, 'binary')
        mimetype = 'application/octet-stream'
    
    return (detected, mimetype)


def calculate_hashes(file_path: Path) -> Dict[str, str]:
    """
    Calculate SHA256, SHA1, and MD5 hashes of a file.
    
    Args:
        file_path: Path to the file
        
    Returns:
        Dictionary with 'sha256', 'sha1', and 'md5' keys
    """
    sha256_hash = hashlib.sha256()
    sha1_hash = hashlib.sha1()
    md5_hash = hashlib.md5()
    
    try:
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                sha256_hash.update(chunk)
                sha1_hash.update(chunk)
                md5_hash.update(chunk)
    except Exception as e:
        logger.error(f"Error calculating hashes for {file_path}: {e}")
        return {"sha256": "", "sha1": "", "md5": ""}
    
    return {
        "sha256": sha256_hash.hexdigest(),
        "sha1": sha1_hash.hexdigest(),
        "md5": md5_hash.hexdigest(),
    }


def extract_metadata(file_path: Path, include_hashes: bool = True) -> Dict:
    """
    Extract file metadata including size, modification time, and hashes.
    
    Args:
        file_path: Path to the file
        include_hashes: Whether to calculate file hashes (can be slow for large files)
        
    Returns:
        Dictionary with metadata
    """
    file_path = Path(file_path)
    stat = file_path.stat()
    
    metadata = {
        "size": stat.st_size,
        "mtime": stat.st_mtime,
        "mtime_iso": None,  # Will be set by the converter
    }
    
    if include_hashes:
        metadata.update(calculate_hashes(file_path))
    else:
        metadata.update({"sha256": "", "sha1": "", "md5": ""})
    
    return metadata


def ensure_output_dir(output_path: Path) -> None:
    """Ensure the output directory exists."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

