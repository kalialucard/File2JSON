"""Integration tests for the CLI and full workflow."""

import json
import tempfile
from pathlib import Path

import pytest

from converter.processor import FileProcessor


def test_process_single_csv():
    """Test processing a single CSV file."""
    csv_content = "name,value\nitem1,10\nitem2,20\n"
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create input file
        input_file = Path(tmpdir) / "test.csv"
        input_file.write_text(csv_content)
        
        # Create output directory
        output_dir = Path(tmpdir) / "output"
        output_dir.mkdir()
        
        # Process
        processor = FileProcessor(output_dir=output_dir)
        results = processor.process(input_file)
        
        assert results["successful"] == 1
        assert results["failed"] == 0
        
        # Check output file exists
        output_file = output_dir / "test.json"
        assert output_file.exists()
        
        # Verify content
        with open(output_file) as f:
            data = json.load(f)
            assert data["detected_type"] == "csv"
            assert data["data"]["row_count"] == 2


def test_process_multiple_files():
    """Test processing multiple files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        input_dir = Path(tmpdir) / "input"
        input_dir.mkdir()
        output_dir = Path(tmpdir) / "output"
        output_dir.mkdir()
        
        # Create multiple test files
        (input_dir / "test1.csv").write_text("a,b\n1,2\n")
        (input_dir / "test2.txt").write_text("Line 1\nLine 2\n")
        import json
        with open(input_dir / "test3.json", 'w') as f:
            json.dump({"test": "data"}, f)
        
        # Process
        processor = FileProcessor(output_dir=output_dir)
        results = processor.process(input_dir)
        
        assert results["successful"] == 3
        assert (output_dir / "test1.json").exists()
        assert (output_dir / "test2.json").exists()
        assert (output_dir / "test3.json").exists()


def test_format_filter():
    """Test format filtering."""
    with tempfile.TemporaryDirectory() as tmpdir:
        input_dir = Path(tmpdir) / "input"
        input_dir.mkdir()
        output_dir = Path(tmpdir) / "output"
        output_dir.mkdir()
        
        # Create files of different types
        (input_dir / "test1.csv").write_text("a,b\n1,2\n")
        (input_dir / "test2.txt").write_text("Line 1\n")
        
        # Process with filter
        processor = FileProcessor(
            output_dir=output_dir,
            formats_filter=["csv"]
        )
        results = processor.process(input_dir)
        
        assert results["successful"] == 1
        assert (output_dir / "test1.json").exists()
        assert not (output_dir / "test2.json").exists()


def test_master_json():
    """Test master.json creation."""
    with tempfile.TemporaryDirectory() as tmpdir:
        input_dir = Path(tmpdir) / "input"
        input_dir.mkdir()
        output_dir = Path(tmpdir) / "output"
        output_dir.mkdir()
        
        # Create test files
        (input_dir / "test1.csv").write_text("a,b\n1,2\n")
        (input_dir / "test2.txt").write_text("Line 1\n")
        
        # Process and create master
        processor = FileProcessor(output_dir=output_dir)
        processor.process(input_dir)
        processor.create_master_json(output_dir / "master.json")
        
        # Verify master.json
        master_file = output_dir / "master.json"
        assert master_file.exists()
        
        with open(master_file) as f:
            master_data = json.load(f)
            assert master_data["total_files"] == 2
            assert len(master_data["converted_files"]) == 2

