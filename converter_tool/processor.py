"""
File processing orchestrator with parallel processing support.
"""

import json
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Dict, List, Optional

from .registry import get_converter
from .utils import detect_file_type

logger = logging.getLogger(__name__)


class FileProcessor:
    """Orchestrates file conversion with parallel processing."""
    
    def __init__(
        self,
        output_dir: Path,
        overwrite: bool = False,
        formats_filter: Optional[List[str]] = None,
        workers: Optional[int] = None,
        max_packets: int = 10000,
        include_base64: bool = False,
    ):
        """
        Initialize file processor.
        
        Args:
            output_dir: Directory for output JSON files
            overwrite: Whether to overwrite existing files
            formats_filter: List of formats to process (None = all)
            workers: Number of worker threads (None = CPU count)
            max_packets: Maximum packets to extract from PCAP files
            include_base64: Include base64 preview for binary files
        """
        self.output_dir = Path(output_dir)
        self.overwrite = overwrite
        self.formats_filter = formats_filter
        self.max_packets = max_packets
        self.include_base64 = include_base64
        
        import os
        self.workers = workers or os.cpu_count() or 1
        
        self.converted_files: List[Dict] = []
        self.failed_files: List[Dict] = []
    
    def process(self, input_path: Path) -> Dict[str, int]:
        """
        Process input file or directory.
        
        Args:
            input_path: File or directory to process
            
        Returns:
            Dictionary with 'successful' and 'failed' counts
        """
        input_path = Path(input_path)
        
        if input_path.is_file():
            files_to_process = [input_path]
        elif input_path.is_dir():
            files_to_process = list(input_path.rglob('*'))
            files_to_process = [f for f in files_to_process if f.is_file()]
        else:
            raise ValueError(f"Input path is neither file nor directory: {input_path}")
        
        if not files_to_process:
            logger.warning(f"No files found in {input_path}")
            return {"successful": 0, "failed": 0}
        
        logger.info(f"Found {len(files_to_process)} files to process")
        
        # Process files in parallel
        with ThreadPoolExecutor(max_workers=self.workers) as executor:
            future_to_file = {
                executor.submit(self._process_single_file, file_path): file_path
                for file_path in files_to_process
            }
            
            for future in as_completed(future_to_file):
                file_path = future_to_file[future]
                try:
                    result = future.result()
                    if result:
                        self.converted_files.append(result)
                except Exception as e:
                    logger.error(f"Error processing {file_path}: {e}")
                    self.failed_files.append({
                        "file": str(file_path),
                        "error": str(e),
                    })
        
        return {
            "successful": len(self.converted_files),
            "failed": len(self.failed_files),
        }
    
    def _process_single_file(self, file_path: Path) -> Optional[Dict]:
        """
        Process a single file.
        
        Args:
            file_path: Path to file
            
        Returns:
            Converted data dictionary or None if failed/skipped
        """
        try:
            # Detect file type
            detected_type, mimetype = detect_file_type(file_path)
            
            # Check format filter
            if self.formats_filter and detected_type not in self.formats_filter:
                logger.debug(f"Skipping {file_path} (type {detected_type} not in filter)")
                return None
            
            # Get converter
            converter_class = get_converter(detected_type)
            converter = converter_class(
                include_base64=self.include_base64,
                base64_limit=1024 * 1024,
            )
            
            # Set recursion depth for archives
            if detected_type in ('zip', 'tar', 'gzip') and hasattr(converter, 'recursion_depth'):
                converter.recursion_depth = 3
            
            # Convert
            kwargs = {}
            if detected_type in ('pcap', 'pcapng'):
                kwargs['max_packets'] = self.max_packets
            
            converted_data = converter.convert(file_path, **kwargs)
            
            # Determine output filename
            output_filename = file_path.stem + ".json"
            output_path = self.output_dir / output_filename
            
            # Check if file exists
            if output_path.exists() and not self.overwrite:
                logger.warning(f"Output file exists, skipping: {output_path}")
                return None
            
            # Save JSON
            converter.save_json(output_path, converted_data)
            
            logger.info(f"Converted {file_path.name} -> {output_filename}")
            
            return converted_data
            
        except Exception as e:
            logger.error(f"Failed to process {file_path}: {e}", exc_info=True)
            return None
    
    def create_master_json(self, output_path: Path) -> None:
        """
        Create a master JSON file combining all converted files.
        
        Args:
            output_path: Path for master.json file
        """
        master_data = {
            "total_files": len(self.converted_files),
            "converted_files": self.converted_files,
        }
        
        if self.failed_files:
            master_data["failed_files"] = self.failed_files
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(master_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Created master.json with {len(self.converted_files)} entries")

