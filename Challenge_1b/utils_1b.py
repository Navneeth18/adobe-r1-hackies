import fitz  # PyMuPDF
import re
import os
import time
from concurrent.futures import ThreadPoolExecutor
from sentence_transformers import SentenceTransformer, util
import nltk
from collections import defaultdict

# --- NLTK Setup ---
# Ensure NLTK data is loaded from the local project directory
try:
    nltk.data.path.append('./nltk_data')
    from nltk.corpus import stopwords
    from nltk.tokenize import word_tokenize, sent_tokenize
    STOPWORDS = set(stopwords.words("english"))
except Exception as e:
    print(f"[CRITICAL_ERROR] Failed to load NLTK data. Please ensure 'nltk_data' folder is present. Error: {e}")
    STOPWORDS = set()

class SectionExtractor:
    """
    Extracts structured sections from a collection of PDF documents in parallel.
    A section is defined as a heading and the content that follows it.
    """
    def _is_heading(self, text: str, block_font_size: float, common_font_size: float) -> bool:
        """Heuristically identifies if a line of text is a heading."""
        if not text or len(text.split()) > 15 or not text[0].isalpha():
            return False
        # Condition 1: Larger font size than the most common text size
        is_larger_font = block_font_size > (common_font_size + 1)
        # Condition 2: Text is in Title Case or ALL CAPS
        is_title_case = text.istitle() or text.isupper()
        # Condition 3: Doesn't end with punctuation typical for a sentence.
        is_not_sentence = not text.strip().endswith(('.', ':', ';'))
        
        return is_larger_font and is_title_case and is_not_sentence

    def _get_common_font_size(self, doc: fitz.Document) -> float:
        """Finds the most frequent font size, likely representing body text."""
        sizes = defaultdict(int)
        for page in doc:
            for block in page.get_text("dict")["blocks"]:
                if "lines" in block:
                    for line in block["lines"]:
                        for span in line["spans"]:
                            sizes[round(span["size"])] += 1
        return max(sizes, key=sizes.get) if sizes else 10.0

    def _extract_from_single_pdf(self, pdf_path: str) -> list:
        """Worker function to process one PDF and extract its sections."""
        sections = []
        try:
            doc = fitz.open(pdf_path)
            common_size = self._get_common_font_size(doc)
            current_heading = "Introduction"
            current_content = []
            heading_page = 1

            for page_num, page in enumerate(doc, 1):
                blocks = page.get_text("dict")["blocks"]
                for block in blocks:
                    if "lines" in block:
                        block_text = "".join(span["text"] for line in block["lines"] for span in line["spans"]).strip()
                        # Get the font size of the first span in the block
                        first_span_size = block["lines"][0]["spans"][0]["size"]
                        
                        if self._is_heading(block_text, first_span_size, common_size):
                            if current_content:
                                sections.append({
                                    "title": current_heading,
                                    "content": " ".join(current_content),
                                    "source": os.path.basename(pdf_path),
                                    "page": heading_page
                                })
                            current_heading = block_text
                            current_content = []
                            heading_page = page_num
                        else:
                            current_content.append(block_text)

            if current_content: # Add the last section
                sections.append({
                    "title": current_heading, "content": " ".join(current_content),
                    "source": os.path.basename(pdf_path), "page": heading_page
                })
            
            print(f"  [INFO] Extracted {len(sections)} sections from {os.path.basename(pdf_path)}")
            return sections
        except Exception as e:
            print(f"  [ERROR] Could not process {os.path.basename(pdf_path)}: {e}")
            return []

    def extract_parallel(self, pdf_paths: list) -> list:
        """
        Public method to launch parallel extraction.
        Uses ThreadPoolExecutor for I/O and CPU-bound tasks, suitable for varied hardware.
        """
        # Use a sensible number of workers for low-end laptops
        max_workers = min(4, os.cpu_count() or 1)
        print(f"[INFO] Starting parallel section extraction with {max_workers} workers...")
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            results = list(executor.map(self._extract_from_single_pdf, pdf_paths))
        
        return [section for doc_sections in results for section in doc_sections]


class RelevanceRanker:
    """
    Ranks text sections based on semantic similarity to a query using a transformer model.
    """
    def __init__(self, model_path='./models/all-MiniLM-L6-v2'):
        self.model_path = model_path
        self.model = None

    def load_model(self):
        """Loads the Sentence Transformer model. Called explicitly to track timing."""
        try:
            print("[INFO] Loading embedding model. This may take a moment...")
            self.model = SentenceTransformer(self.model_path)
            print("[INFO] Embedding model loaded successfully.")
        except Exception as e:
            print(f"[CRITICAL_ERROR] Could not load model from '{self.model_path}'. Ensure the model is downloaded. Error: {e}")
            raise

    def rank(self, sections: list, query: str, top_k: int = 5) -> list:
        """Encodes and ranks sections, returning the top_k most relevant."""
        if not self.model:
            raise RuntimeError("Model is not loaded. Please call .load_model() first.")
        if not sections:
            return []

        print(f"[INFO] Encoding {len(sections)} sections for ranking...")
        section_contents = [sec.get('content', '') for sec in sections]
        
        # Optimized batch encoding for performance
        section_embeddings = self.model.encode(section_contents, convert_to_tensor=True, show_progress_bar=True)
        query_embedding = self.model.encode(query, convert_to_tensor=True)
        
        # Compute cosine similarity
        cosine_scores = util.cos_sim(query_embedding, section_embeddings)[0]
        
        # Pair scores with sections
        scored_sections = []
        for i, section in enumerate(sections):
            section['relevance_score'] = round(cosine_scores[i].item(), 4)
            scored_sections.append(section)
        
        # Sort by score and return top results
        ranked_sections = sorted(scored_sections, key=lambda x: x['relevance_score'], reverse=True)
        return ranked_sections[:top_k]


class Summarizer:
    """
    Performs extractive summarization on a given text.
    """
    def summarize(self, text: str, num_sentences: int = 3) -> str:
        """Extracts the most important sentences based on word frequency."""
        if not text or not STOPWORDS:
            return "Could not summarize text."

        try:
            sents = sent_tokenize(text)
            if len(sents) <= num_sentences:
                return text

            words = word_tokenize(text.lower())
            freq = defaultdict(int)
            for word in words:
                if word.isalnum() and word not in STOPWORDS:
                    freq[word] += 1
            
            if not freq: return " ".join(sents[:num_sentences])

            scores = {sent: sum(freq[word] for word in word_tokenize(sent.lower()) if word in freq) for sent in sents}
            
            ranked_sents = sorted(scores.items(), key=lambda x: x[1], reverse=True)
            return " ".join([sent for sent, _ in ranked_sents[:num_sentences]])
        except Exception as e:
            print(f"  [WARN] Summarization failed for a section: {e}")
            return text