# File Converter

A production-ready Python tool to convert various IT/cybersecurity file types into structured JSON format. Supports automatic file type detection, parallel processing, and handles multiple formats including EVTX, PCAP, CSV, JSON, XML, logs, PDF, DOCX, and archives.

## Features

- **Multiple Format Support**: EVTX, PCAP/PCAPNG, CSV, JSON, XML, TXT/LOG, PDF, DOCX, ZIP/TAR
- **Automatic Type Detection**: Uses `python-magic`/`filetype` with extension fallback
- **Parallel Processing**: Multi-threaded conversion with configurable worker count
- **Comprehensive Metadata**: Includes file hashes (SHA256, SHA1, MD5), size, timestamps
- **Recursive Archive Support**: Processes nested archives with configurable depth limit
- **Robust Error Handling**: Continues processing other files on failure
- **Master JSON Output**: Optional combined output file for batch processing

## Installation

### Prerequisites

- Python 3.10 or higher
- (Optional) `tshark` for pyshark-based PCAP conversion (install via system package manager)

### Setup

1. Create and activate a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

**Note**: Some format-specific libraries are optional. Install as needed:

- `python-evtx` for .evtx files
- `pyshark` or `scapy` for .pcap files (pyshark requires `tshark`)
- `pdfminer.six` or `PyPDF2` for .pdf files
- `python-docx` for .docx files

### System Dependencies

**For PCAP support with pyshark:**
- Ubuntu/Debian: `sudo apt-get install tshark`
- Fedora/RHEL: `sudo dnf install wireshark-cli`
- macOS: `brew install wireshark`

**For python-magic:**
- Ubuntu/Debian: `sudo apt-get install libmagic1`
- Fedora/RHEL: `sudo dnf install file-devel`
- macOS: `brew install libmagic`

## Usage

### Basic Usage

Convert a single file:
```bash
python -m converter.main --input file.evtx --output-dir ./output
```

Convert a directory:
```bash
python -m converter.main --input ./Reaper --output-dir ./Reaper_JSON --combine --workers 4
```

### Command-Line Options

```
--input PATH          Input file or directory path (required)
--output-dir PATH      Output directory for JSON files (required)
--combine             Create a combined master.json file with all outputs
--overwrite           Overwrite existing output files
--silent              Suppress console output (errors only)
--verbose             Enable verbose logging
--formats FORMATS     Comma-separated list of formats to process (e.g., evtx,pcap,csv)
--workers N           Number of worker threads (default: CPU count)
--max-packets N       Maximum packets to extract from PCAP files (default: 10000)
--include-base64      Include base64-encoded content for binary files (up to 1MB)
```

### Examples

Process only EVTX and PCAP files:
```bash
python -m converter.main --input ./captures --output-dir ./json --formats evtx,pcap --workers 8
```

Convert with verbose logging:
```bash
python -m converter.main --input ./data --output-dir ./output --verbose --combine
```

Process single file silently:
```bash
python -m converter.main --input log.txt --output-dir ./output --silent
```

## Supported Formats

### Windows Event Log (.evtx)
Extracts EventID, TimeCreated, EventRecordID, and all Data elements from each record.

**Requirements**: `python-evtx`

### Network Captures (.pcap, .pcapng)
Extracts packet metadata: timestamp, source/destination IP & port, protocol, and summary.

**Requirements**: `pyshark` (requires `tshark`) or `scapy`

**Note**: Use `--max-packets` to limit extraction for large files.

### CSV Files (.csv)
Converts rows to JSON array with automatic delimiter detection.

### JSON Files (.json)
Validates and pretty-prints JSON content.

### XML Files (.xml)
Converts XML tree to JSON structure preserving hierarchy, attributes, and text.

### Text/Log Files (.txt, .log)
Extracts lines with optional timestamp detection (ISO8601 and epoch formats).

### PDF Files (.pdf)
Extracts text per page and page count.

**Requirements**: `pdfminer.six` or `PyPDF2`

### Word Documents (.docx)
Extracts paragraphs with style information.

**Requirements**: `python-docx`

### Archives (.zip, .tar, .tar.gz)
Lists contents and recursively converts supported files within archives.

**Limitation**: Recursion depth limited to 3 levels to prevent infinite loops.

### Unknown Binary Files
Extracts metadata (filename, size, hashes) with optional base64 preview (via `--include-base64`).

## Output Format

All converters produce JSON files following this schema:

```json
{
  "source_filename": "file.evtx",
  "source_path": "/absolute/path/to/file.evtx",
  "detected_type": "evtx",
  "mimetype": "application/x-evtx",
  "converted_at": "2024-01-15T10:30:00Z",
  "metadata": {
    "size": 12345,
    "mtime": 1705312200.0,
    "mtime_iso": "2024-01-15T10:30:00",
    "sha256": "...",
    "sha1": "...",
    "md5": "..."
  },
  "data": {
    // Format-specific data structure
  }
}
```

### Master JSON

When using `--combine`, a `master.json` file is created with:

```json
{
  "total_files": 10,
  "converted_files": [
    // Array of all converted file outputs
  ],
  "failed_files": [
    // Array of failed files (if any)
  ]
}
```

## Testing

Run tests with pytest:

```bash
pytest
```

Run with coverage:

```bash
pytest --cov=converter --cov-report=html
```

## Project Structure

```
.
├── converter/
│   ├── __init__.py
│   ├── base_converter.py      # Base converter class
│   ├── registry.py             # Converter registry
│   ├── utils.py                # File detection, hashing
│   ├── processor.py            # Parallel processing
│   ├── cli.py                  # Command-line interface
│   ├── main.py                 # Entry point
│   └── converters/
│       ├── __init__.py
│       ├── evtx.py
│       ├── pcap.py
│       ├── csv_converter.py
│       ├── json_converter.py
│       ├── xml_converter.py
│       ├── text_converter.py
│       ├── pdf_converter.py
│       ├── docx_converter.py
│       ├── archive_converter.py
│       └── binary_converter.py
├── tests/
│   ├── __init__.py
│   ├── test_csv.py
│   ├── test_json.py
│   ├── test_text.py
│   ├── test_xml.py
│   ├── test_utils.py
│   ├── test_integration.py
│   └── fixtures/
│       ├── sample.csv
│       ├── sample.txt
│       ├── sample.json
│       └── sample.xml
├── requirements.txt
├── pyproject.toml
├── README.md
├── LICENSE
└── .gitignore
```

## Limitations

1. **PCAP Files**: Large files are limited by `--max-packets` (default: 10,000 packets) to prevent excessive memory usage.
2. **PDF Files**: Text extraction only; images and complex formatting are not preserved.
3. **Archives**: Recursion depth is limited to 3 levels to prevent infinite loops.
4. **Binary Files**: Full conversion not attempted; only metadata extraction (with optional base64 preview).
5. **Memory Usage**: Very large files may consume significant memory; streaming is used where possible.

## Error Handling

The tool handles errors gracefully:
- Corrupted files are logged and skipped
- Missing dependencies raise clear error messages
- Unsupported file types are treated as binary (metadata only)
- Processing continues even if individual files fail

## Contributing

Contributions are welcome! Please ensure:
- Code follows PEP 8 style guidelines
- Tests are included for new features
- Documentation is updated

## License

MIT License - see LICENSE file for details.

## Example Output

For a CSV file:
```json
{
  "source_filename": "data.csv",
  "source_path": "/path/to/data.csv",
  "detected_type": "csv",
  "mimetype": "text/csv",
  "converted_at": "2024-01-15T10:30:00Z",
  "metadata": {
    "size": 256,
    "mtime": 1705312200.0,
    "mtime_iso": "2024-01-15T10:30:00",
    "sha256": "abc123...",
    "sha1": "def456...",
    "md5": "ghi789..."
  },
  "data": {
    "column_names": ["name", "age", "city"],
    "row_count": 2,
    "rows": [
      {"name": "Alice", "age": "30", "city": "New York"},
      {"name": "Bob", "age": "25", "city": "San Francisco"}
    ]
  }
}
```


