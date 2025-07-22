# PDF Structure Extraction Engine

## 1. Overview

This is a high-performance, offline PDF processing solution that extracts titles and hierarchical headings (H1, H2, H3) into structured JSON files. It analyzes document layout rather than bookmarks and is containerized with Docker for easy, consistent deployment.

## 2. Key Features

- **Automated & Structured**: Processes all PDFs in an input directory, extracting titles and headings with page numbers into corresponding JSON files.
- **Fast & Offline**: Optimized to process a 50-page PDF in under 10 seconds and works without any internet connection.
- **Layout-Aware**: Intelligently identifies headings by analyzing font sizes, styles, and positioning.

## 3. Technology Stack

- **Language**: Python 3.10
- **Core Library**: `PyMuPDF` (Fitz)
- **Containerization**: Docker

## 4. Project Structure

```
.
├── Dockerfile
├── main.py
├── requirements.txt
├── utils.py
├── input/
└── output/
```

- **`Dockerfile`**: Defines the container image.
- **`main.py`**: Main processing script.
- **`utils.py`**: PDF analysis helper functions.
- **`requirements.txt`**: Python dependencies.
- **`input/`**: Directory for your PDFs.
- **`output/`**: Directory for JSON results.

## 5. Setup and Execution

**Prerequisites**: Docker must be installed and running.

**1. Build the Docker Image:**
```bash
docker build --platform linux/amd64 -t pdf-processor .
```

**2. Run the Container:**
```bash
docker run --rm -v "$(pwd)/input":/app/input:ro -v "$(pwd)/output":/app/output --network none pdf-processor
```
*This command mounts your local `input` and `output` folders and runs the container offline.*

## 6. Solution Architecture

6.1. Title Extraction
Component: merge_title_on_page1(doc[0])

Logic:

Scans the first page of the PDF.
Identifies the largest text block as the document title.
Cleans up noise (e.g., "RFP:", "RSVP:", dashes) using pattern checks.

Validation:

Rejects titles that are non-informative, repetitive, or match headings.
Ensures title is distinct from any extracted outline headings.

6.2. Outline Extraction
Component: extract_outline_from_page(page)

Logic:

Parses each PDF page using PyMuPDF (fitz) and extracts all text spans.
Collects lines along with their font sizes and top positions (Y-coordinates).
Filters out non-text elements (e.g., images, footers, dates).

6.3. Heading Level Detection
Sorts all detected font sizes (above a threshold) in descending order.

Assigns:

Largest size → H1

Second-largest → H2

Third-largest → H3

Fourth-largest → H4

6.4 Numbered Section Mapping
Detects structured numbers like:

"2.1" → H2

"3.5.1" → H3 

Applies additional logic to override based on visual cues.

6.5 Heading Merging
Purpose: Merge multi-line headings into a single logical block.

Logic:

Uses spatial proximity (within 25 pixels vertically).

Buffers text until the next distinct heading is detected.

Preserves colon-ended titles (e.g., "Training:", "Summary:").

6.6. Filtering & Noise Removal
Rules Applied:

Skips:

Page numbers (e.g., "Page 3 of 5")

Dates (e.g., "12 JUL 2024")

Emails, short fragments (e.g., "rooms.", "structure")

Filters out repeated headings and heading lines that match the title.

Accepts only valid headings based on:

Length

Capitalization

Punctuation (colons, etc.)

6.7. Single vs Multi-Page Handling
Single-page PDF:

Extracts only one valid H1 heading, ensuring it's not the title.

Multi-page PDF:

Extracts all valid headings across all pages.

Optionally skips page 0 headings if needed for format consistency.

## 7. Configuration

Input and output directories (`./input` and `./output`) are configured in `main.py` and correspond to the paths inside the container.

## 8. Troubleshooting

- **Permission Errors**: Ensure your host `output` directory is writeable.
- **No JSON Output**: Verify the `input` directory contains PDFs, volumes are mounted correctly, and check container logs (`docker logs <container_id>`) for errors.
