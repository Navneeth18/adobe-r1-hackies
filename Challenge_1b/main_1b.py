import json
import time
import os
from utils_1b import SectionExtractor, RelevanceRanker, Summarizer

# --- Configuration ---
INPUT_JSON_PATH = "input.json"
INPUT_PDF_DIR = "input"
OUTPUT_DIR = "output"
OUTPUT_JSON_PATH = os.path.join(OUTPUT_DIR, "challenge1b_output.json")
TOP_K = 5

def log(level, message):
    """Simple logger for program tracking."""
    print(f"[{time.strftime('%H:%M:%S')}] [{level.upper()}] {message}")

def main():
    """Main execution workflow for Challenge 1B."""
    total_start_time = time.time()
    log("start", "Persona-Driven Intelligence System Initializing...")

    # --- 1. Load and Validate Input ---
    try:
        with open(INPUT_JSON_PATH, "r", encoding="utf-8") as f:
            config = json.load(f)
        log("info", f"Loaded configuration from '{INPUT_JSON_PATH}'.")
    except Exception as e:
        log("fatal", f"Could not load or parse '{INPUT_JSON_PATH}': {e}")
        return

    # --- UPDATED INPUT PARSING LOGIC ---
    persona_obj = config.get("persona", {})
    job_obj = config.get("job_to_be_done", {})
    doc_objects = config.get("documents", []) # <-- CHANGE HERE: Read the 'documents' key

    persona = persona_obj.get("role")
    job_to_be_done = job_obj.get("task")
    
    if not all([persona, job_to_be_done, doc_objects]):
        log("fatal", "Input JSON is missing required fields ('documents', 'persona.role', 'job_to_be_done.task').")
        return

    # Extract filenames from the list of objects
    doc_filenames = [doc.get("filename") for doc in doc_objects if doc.get("filename")] # <-- CHANGE HERE
    pdf_paths = [os.path.join(INPUT_PDF_DIR, fname) for fname in doc_filenames]
    
    query = f"Persona: {persona}. Task: {job_to_be_done}"
    log("info", f"Query: '{query}'")

    # --- 2. Section Extraction ---
    log("info", "--- Step 1: Kicking off Section Extraction ---")
    t_start = time.time()
    extractor = SectionExtractor()
    all_sections = extractor.extract_parallel(pdf_paths)
    if not all_sections:
        log("fatal", "No sections could be extracted. Exiting.")
        return
    log("info", f"Extraction complete. Found {len(all_sections)} sections in {time.time() - t_start:.2f}s.")

    # --- 3. Relevance Ranking ---
    log("info", "--- Step 2: Starting Relevance Ranking ---")
    t_start = time.time()
    try:
        ranker = RelevanceRanker()
        ranker.load_model()
        top_sections = ranker.rank(all_sections, query, top_k=TOP_K)
        log("info", f"Ranking complete. Identified top {len(top_sections)} sections in {time.time() - t_start:.2f}s.")
    except Exception as e:
        log("fatal", f"An error occurred during relevance ranking: {e}")
        return

    # --- 4. Summarization ---
    log("info", "--- Step 3: Generating Summaries for Top Sections ---")
    t_start = time.time()
    summarizer = Summarizer()
    for section in top_sections:
        section["refined_text"] = summarizer.summarize(section["content"])
    log("info", f"Summarization complete in {time.time() - t_start:.2f}s.")

    # --- 5. Final Output Generation ---
    log("info", "--- Step 4: Formatting Final Output ---")
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    final_output = {
        "metadata": {
            "input_documents": doc_filenames, # Use the extracted list of filenames
            "persona": persona,
            "job_to_be_done": job_to_be_done,
            "processing_timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        },
        "extracted_sections": [
            {
                "document": s['source'],
                "page_number": s['page'],
                "section_title": s['title'],
                "importance_rank": idx + 1,
            } for idx, s in enumerate(top_sections)
        ],
        "sub_section_analysis": [
            {
                "document": s['source'],
                "page_number": s['page'],
                "refined_text": s['refined_text'],
            } for s in top_sections
        ]
    }

    try:
        with open(OUTPUT_JSON_PATH, "w", encoding="utf-8") as f:
            json.dump(final_output, f, indent=4)
        log("success", f"Processing complete. Output saved to '{OUTPUT_JSON_PATH}'.")
    except Exception as e:
        log("fatal", f"Failed to write output file: {e}")
        
    log("end", f"Total execution time: {time.time() - total_start_time:.2f} seconds.")

if __name__ == "__main__":
    main()