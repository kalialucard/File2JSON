"""
Command-line interface for the file converter.
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import List, Optional

from .processor import FileProcessor

logger = logging.getLogger(__name__)


def setup_logging(silent: bool = False, verbose: bool = False) -> None:
    """Configure logging."""
    level = logging.DEBUG if verbose else (logging.ERROR if silent else logging.INFO)
    
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(
        logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    )
    
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.addHandler(handler)


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Convert various IT/cybersecurity file types to JSON",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --input ./data --output-dir ./output
  %(prog)s --input file.evtx --output-dir ./output --combine
  %(prog)s --input ./captures --output-dir ./json --formats pcap,evtx --workers 8
        """
    )
    
    parser.add_argument(
        '--input',
        type=str,
        required=True,
        help='Input file or directory path'
    )
    
    parser.add_argument(
        '--output-dir',
        type=str,
        required=True,
        help='Output directory for JSON files'
    )
    
    parser.add_argument(
        '--combine',
        action='store_true',
        help='Create a combined master.json file with all outputs'
    )
    
    parser.add_argument(
        '--overwrite',
        action='store_true',
        help='Overwrite existing output files'
    )
    
    parser.add_argument(
        '--silent',
        action='store_true',
        help='Suppress console output (errors only)'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    parser.add_argument(
        '--formats',
        type=str,
        help='Comma-separated list of formats to process (e.g., evtx,pcap,csv). '
             'If not specified, all supported formats are processed.'
    )
    
    parser.add_argument(
        '--workers',
        type=int,
        default=None,
        help='Number of worker threads for parallel processing (default: CPU count)'
    )
    
    parser.add_argument(
        '--max-packets',
        type=int,
        default=10000,
        help='Maximum number of packets to extract from PCAP files (default: 10000)'
    )
    
    parser.add_argument(
        '--include-base64',
        action='store_true',
        help='Include base64-encoded content for binary files (up to 1MB)'
    )
    
    return parser.parse_args()


def main() -> int:
    """Main CLI entry point."""
    args = parse_args()
    setup_logging(silent=args.silent, verbose=args.verbose)
    
    # Validate input path
    input_path = Path(args.input)
    if not input_path.exists():
        logger.error(f"Input path does not exist: {input_path}")
        return 1
    
    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Parse formats filter
    formats_filter: Optional[List[str]] = None
    if args.formats:
        formats_filter = [f.strip().lower() for f in args.formats.split(',')]
    
    # Initialize processor
    processor = FileProcessor(
        output_dir=output_dir,
        overwrite=args.overwrite,
        formats_filter=formats_filter,
        workers=args.workers,
        max_packets=args.max_packets,
        include_base64=args.include_base64,
    )
    
    # Process input
    try:
        results = processor.process(input_path)
        
        if not args.silent:
            logger.info(f"Processed {results['successful']} files successfully")
            if results['failed'] > 0:
                logger.warning(f"Failed to process {results['failed']} files")
        
        # Create master.json if requested
        if args.combine:
            processor.create_master_json(output_dir / "master.json")
            if not args.silent:
                logger.info(f"Created master.json with {results['successful']} entries")
        
        return 0 if results['failed'] == 0 else 1
        
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        return 130
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        return 1

