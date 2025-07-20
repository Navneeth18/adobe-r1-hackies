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

The solution programmatically analyzes a PDF's visual layout. It identifies the title by finding the largest text on the first page. Headings (H1-H3) are detected by mapping the largest font sizes and identifying common numbering patterns (e.g., "2.1"). The logic also merges multi-line headings and filters out noise like page numbers.

## 7. Configuration

Input and output directories (`./input` and `./output`) are configured in `main.py` and correspond to the paths inside the container.

## 8. Troubleshooting

- **Permission Errors**: Ensure your host `output` directory is writeable.
- **No JSON Output**: Verify the `input` directory contains PDFs, volumes are mounted correctly, and check container logs (`docker logs <container_id>`) for errors.
