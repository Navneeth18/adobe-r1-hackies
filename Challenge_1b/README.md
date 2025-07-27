# Persona-Driven Document Intelligence (Challenge 1B)

This project is a solution for the Adobe "Connecting the Dots" Hackathon, Round 1B. It is an intelligent document analysis system that processes a collection of PDFs to extract and rank the most relevant information based on a specified user persona and their job-to-be-done. The entire system is packaged in a Docker container for offline, platform-independent execution.

## Project Structure

The final project is organized as follows. All offline model assets (`models/` and `nltk_data/`) are included in the repository to ensure the Docker container can be built and run without internet access.

```
.
├── Dockerfile
├── README.md
├── approach_explanation.md
├── main_1b.py
├── requirements.txt
├── utils_1b.py
├── .dockerignore
├── .gitignore
├── models/
│   └── all-MiniLM-L6-v2/
│       └── ... (model files)
└── nltk_data/
    ├── corpora/
    └── tokenizers/
```

## How to Build and Run the Solution

The solution is containerized using Docker. Ensure Docker Desktop is running on your machine before proceeding.

### Prerequisites

* Docker Desktop installed and running.
* A local folder named `input` containing the PDF documents to be analyzed.
* A file named `input.json` in the project root, specifying the persona and documents.

### Step 1: Build the Docker Image

Navigate to the project's root directory in your terminal and execute the following command. This will build the Docker image, including all necessary dependencies and offline models.

```bash
docker build --platform linux/amd64 -t adobe-r1-hackies:latest .
```

### Step 2: Run the Docker Container

After the image is built successfully, run the container using the command below. This command mounts your local `input` and `output` directories into the container, allowing the script to read your PDFs and write the results back to your machine.

* The `--rm` flag automatically removes the container after execution.
* The `-v` flags map the volumes.
* The `--network none` flag ensures the container runs offline as per competition rules.

```powershell
# For PowerShell on Windows
docker run --rm -v "${PWD}/input:/app/input" -v "${PWD}/output:/app/output" --network none adobe-r1-hackies:latest

# For Bash on Linux/macOS
docker run --rm -v "$(pwd)/input:/app/input" -v "$(pwd)/output:/app/output" --network none adobe-r1-hackies:latest
```

The application will process the documents and generate a `challenge1b_output.json` file in a newly created `output` folder in your project directory.

## Solution Approach

Our system uses a three-stage pipeline to deliver accurate, persona-driven insights:

1.  **Heuristic Section Extraction:** We first parse the PDFs using `PyMuPDF`, analyzing the document layout to identify text blocks. A set of robust, font-independent heuristics (e.g., text length, capitalization, punctuation) is applied to distinguish headings from body content. This method is resilient to diverse PDF formatting and is executed in parallel for high efficiency.

2.  **Semantic Relevance Ranking:** To find the most relevant content, we use the `all-MiniLM-L6-v2` sentence-transformer model. This model, chosen for its high performance and small footprint (<100MB), converts the user's query (persona + job) and each extracted document section into vector embeddings. By calculating the cosine similarity between the query and section vectors, we produce a precise relevance score for every section and rank them accordingly.

3.  **Extractive Summarization:** For the top-ranked sections, we generate concise summaries. This is achieved using NLTK to tokenize the content, identify the most significant words (excluding stopwords), and score each sentence based on the weight of its words. The highest-scoring sentences are selected to form a `refined_text` summary, providing a quick and meaningful overview of the key information.

For a more detailed explanation of the methodology, please see `approach_explanation.md`.

## Dependencies

All required Python libraries are listed in `requirements.txt` and are installed automatically when building the Docker image.

* `pymupdf==1.23.26`
* `sentence-transformers==2.7.0`
* `torch>=2.3.0`
* `nltk==3.8.1`
* `huggingface-hub<0.21.0`
