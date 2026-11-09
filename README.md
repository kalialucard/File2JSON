# File2JSON 🔄

> Convert cybersecurity and IT file formats into structured, searchable JSON — with metadata, hashes, and parallel processing.

[![Python](https://img.shields.io/badge/python-3.10%2B-blue?logo=python)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## What It Does

File2JSON is a production-ready Python CLI tool that ingests raw forensic and IT files and outputs structured JSON records you can feed into SIEMs, analysis pipelines, or notebooks.

| Input Format | What Gets Extracted |
|---|---|
| **EVTX** (Windows Event Log) | Event ID, timestamp, provider, XML payload |
| **PCAP / PCAPNG** | Packets with src/dst IP, ports, protocol, payload preview |
| **CSV / JSON / XML** | Parsed rows/nodes with schema inference |
| **TXT / LOG** | Line-by-line records with offset metadata |
| **PDF / DOCX** | Extracted text, page count, author metadata |
| **ZIP / TAR** | Recursive extraction with per-entry records |

Every output record also includes `sha256`, `sha1`, `md5`, `file_size`, and `mtime` fields.

## Screenshot

<!-- TODO: add a screenshot of `python -m converter_tool.cli --help` output here -->
![CLI Screenshot](docs/screenshot.png)

## Installation

**Prerequisites:** Python 3.10+, optionally `tshark` for PCAP conversion.

```bash
git clone https://github.com/kalialucard/File2JSON.git
cd File2JSON

python3 -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

pip install -e .
```

## Usage

```bash
# Convert a single EVTX file
python -m converter_tool.cli Security.evtx -o output/

# Convert all files in a directory
python -m converter_tool.cli ./evidence/ -o output/ --workers 4

# Merge all results into one master JSON
python -m converter_tool.cli ./evidence/ -o output/ --master-output

# Filter to specific extensions
python -m converter_tool.cli ./logs/ -o output/ --ext .log .csv
```

Output structure:

```
output/
├── Security.json           # per-file structured records
├── capture.pcap.json
└── all_findings.json       # master (with --master-output)
```

## Project Structure

```
File2JSON/
├── converter_tool/
│   ├── cli.py              # Click CLI entry point
│   ├── detector.py         # Magic-byte file type detection
│   ├── parsers/            # Format-specific parsers
│   └── models.py           # Pydantic output models
└── pyproject.toml
```

## Contributing

PRs welcome. Open an issue first for large changes.

## License

[MIT](LICENSE) © kalialucard
