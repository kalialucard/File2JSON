"""
Converter for archive files (.zip, .tar, .tar.gz).
"""

import logging
import tarfile
import zipfile
from pathlib import Path
from typing import Any, Dict, List

from ..base_converter import BaseConverter

logger = logging.getLogger(__name__)


class ArchiveConverter(BaseConverter):
    """Converter for archive files."""
    
    def __init__(self, include_base64: bool = False, base64_limit: int = 1024 * 1024, 
                 recursion_depth: int = 3):
        """
        Initialize archive converter.
        
        Args:
            include_base64: Whether to include base64 encoded content
            base64_limit: Maximum size for base64 preview
            recursion_depth: Maximum depth for recursive archive extraction (default: 3)
        """
        super().__init__(include_base64, base64_limit)
        self.recursion_depth = recursion_depth
    
    def _extract_data(self, file_path: Path, **kwargs) -> Dict[str, Any]:
        """
        Extract contents from archive file.
        
        Returns:
            Dictionary with file listing and converted contents
        """
        file_path = Path(file_path)
        detected_type, _ = self._detect_type(file_path)
        
        if detected_type == 'zip':
            return self._extract_zip(file_path)
        elif detected_type in ('tar', 'gzip'):
            return self._extract_tar(file_path)
        else:
            raise ValueError(f"Unsupported archive type: {detected_type}")
    
    def _extract_zip(self, file_path: Path) -> Dict[str, Any]:
        """Extract ZIP archive."""
        files = []
        
        try:
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                file_list = zip_ref.namelist()
                
                for file_name in file_list:
                    file_info = zip_ref.getinfo(file_name)
                    
                    file_obj = {
                        "filename": file_name,
                        "size": file_info.file_size,
                        "compressed_size": file_info.compress_size,
                        "is_directory": file_name.endswith('/'),
                    }
                    
                    # Try to convert supported files recursively
                    if not file_obj["is_directory"] and self.recursion_depth > 0:
                        try:
                            # Read file content
                            content = zip_ref.read(file_name)
                            
                            # Save to temp location and convert
                            import tempfile
                            with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file_name).suffix) as tmp:
                                tmp.write(content)
                                tmp_path = Path(tmp.name)
                            
                            try:
                                # Try to convert the extracted file
                                detected_type, _ = self._detect_type(tmp_path)
                                if detected_type != 'binary' and self.recursion_depth > 0:
                                    from ..registry import get_converter
                                    converter = get_converter(detected_type)
                                    converter_instance = converter(
                                        include_base64=self.include_base64,
                                        base64_limit=self.base64_limit
                                    )
                                    if hasattr(converter_instance, 'recursion_depth'):
                                        converter_instance.recursion_depth = self.recursion_depth - 1
                                    
                                    converted = converter_instance.convert(tmp_path)
                                    file_obj["converted_content"] = converted["data"]
                            except Exception as e:
                                logger.debug(f"Could not convert {file_name}: {e}")
                            finally:
                                tmp_path.unlink()
                        
                        except Exception as e:
                            logger.warning(f"Error processing archive file {file_name}: {e}")
                    
                    files.append(file_obj)
        
        except Exception as e:
            logger.error(f"Error reading ZIP file {file_path}: {e}")
            raise
        
        return {
            "archive_type": "zip",
            "file_count": len(files),
            "files": files,
        }
    
    def _extract_tar(self, file_path: Path) -> Dict[str, Any]:
        """Extract TAR/TAR.GZ archive."""
        files = []
        
        try:
            mode = 'r:gz' if file_path.suffix == '.gz' or '.tar.gz' in str(file_path) else 'r'
            
            with tarfile.open(file_path, mode) as tar_ref:
                members = tar_ref.getmembers()
                
                for member in members:
                    file_obj = {
                        "filename": member.name,
                        "size": member.size,
                        "is_directory": member.isdir(),
                        "mode": oct(member.mode),
                        "mtime": member.mtime,
                    }
                    
                    # Try to convert supported files recursively
                    if not file_obj["is_directory"] and self.recursion_depth > 0:
                        try:
                            # Extract to temp location
                            import tempfile
                            with tempfile.NamedTemporaryFile(delete=False, suffix=Path(member.name).suffix) as tmp:
                                extracted = tar_ref.extractfile(member)
                                if extracted:
                                    tmp.write(extracted.read())
                                tmp_path = Path(tmp.name)
                            
                            try:
                                # Try to convert the extracted file
                                detected_type, _ = self._detect_type(tmp_path)
                                if detected_type != 'binary' and self.recursion_depth > 0:
                                    from ..registry import get_converter
                                    converter = get_converter(detected_type)
                                    converter_instance = converter(
                                        include_base64=self.include_base64,
                                        base64_limit=self.base64_limit
                                    )
                                    if hasattr(converter_instance, 'recursion_depth'):
                                        converter_instance.recursion_depth = self.recursion_depth - 1
                                    
                                    converted = converter_instance.convert(tmp_path)
                                    file_obj["converted_content"] = converted["data"]
                            except Exception as e:
                                logger.debug(f"Could not convert {member.name}: {e}")
                            finally:
                                tmp_path.unlink()
                        
                        except Exception as e:
                            logger.warning(f"Error processing archive file {member.name}: {e}")
                    
                    files.append(file_obj)
        
        except Exception as e:
            logger.error(f"Error reading TAR file {file_path}: {e}")
            raise
        
        return {
            "archive_type": "tar",
            "file_count": len(files),
            "files": files,
        }

