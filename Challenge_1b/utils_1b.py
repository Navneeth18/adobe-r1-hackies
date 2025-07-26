import fitz  # PyMuPDF
import re
import os
from concurrent.futures import ThreadPoolExecutor
from sentence_transformers import SentenceTransformer, util
import nltk
from collections import defaultdict
from tqdm import tqdm

# --- NLTK Setup ---
try:
    nltk.data.path.append('./nltk_data')
    from nltk.corpus import stopwords
    from nltk.tokenize import word_tokenize, sent_tokenize
    STOPWORDS = set(stopwords.words("english"))
except Exception as e:
    print(f"[CRITICAL_ERROR] Failed to load NLTK data: {e}")
    STOPWORDS = set()

def _clean_text(text):
    """A dedicated function to clean text artifacts from PDF extraction."""
    text = re.sub(r'[\u2022\u25E6\u25CF\ufb00-\ufb04]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

class SectionExtractor:
    """Final extractor using layout and text-based heuristics, ignoring font metadata."""

    def _is_heading_by_layout(self, text: str) -> bool:
        """Identifies a heading based on its structure, not its font."""
        if not text:
            return False
            
        # Rule 1: Headings are short.
        if len(text.split()) > 12:
            return False
            
        # Rule 2: Headings do not end with sentence-ending punctuation.
        if text.strip().endswith(('.', '!', '?')):
            return False
            
        # Rule 3: Headings are often in Title Case or ALL CAPS.
        # This is a very strong signal.
        if not (text.istitle() or text.isupper()):
            # Allow for single-word, capitalized headings
            if len(text.split()) > 1:
                return False
        
        # Rule 4: Headings are typically longer than a single character.
        if len(text) <= 2:
            return False

        return True

    def _extract_from_single_pdf(self, pdf_path: str) -> list:
        doc_name = os.path.basename(pdf_path)
        sections = []
        try:
            doc = fitz.open(pdf_path)
            current_heading = "Introduction"
            current_content = []
            heading_page = 1

            for page_num, page in enumerate(doc, 1):
                # Using 'blocks' gives us paragraphs separated by layout.
                blocks = page.get_text("blocks")
                for block in blocks:
                    # block[4] contains the text content of the block
                    block_text = _clean_text(block[4])
                    if not block_text:
                        continue

                    # Apply our layout-based heading detection
                    if self._is_heading_by_layout(block_text):
                        if current_content:
                            sections.append({
                                "title": current_heading,
                                "content": " ".join(current_content),
                                "source": doc_name, "page": heading_page
                            })
                        
                        # Start a new section
                        current_heading = block_text
                        current_content = []
                        heading_page = page_num
                    else:
                        current_content.append(block_text)
            
            # Add the last section after the loop finishes
            if current_content:
                sections.append({
                    "title": current_heading, "content": " ".join(current_content),
                    "source": doc_name, "page": heading_page
                })
            
            return sections
        except Exception as e:
            print(f"  [ERROR] Could not process {doc_name}: {e}")
            return []

    def extract_parallel(self, pdf_paths: list) -> list:
        max_workers = min(4, os.cpu_count() or 1)
        sections = []
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            with tqdm(total=len(pdf_paths), desc="Extracting Sections") as pbar:
                futures = {executor.submit(self._extract_from_single_pdf, path): path for path in pdf_paths}
                for future in futures:
                    result = future.result()
                    # Filter out empty "Introduction" sections if they have no real content
                    for section in result:
                        if section['title'] == 'Introduction' and not section['content'].strip():
                            continue
                        sections.append(section)
                    pbar.update(1)
        return sections

class RelevanceRanker:
    def __init__(self, model_path='./models/all-MiniLM-L6-v2'):
        self.model_path = model_path
        self.model = None
    def load_model(self):
        try: self.model = SentenceTransformer(self.model_path)
        except Exception as e: raise IOError(f"Could not load model from '{self.model_path}'.")
    def rank(self, sections, query, top_k):
        if not self.model: raise RuntimeError("Model not loaded.")
        if not sections: return []
        section_contents = [f"{sec.get('title', '')}. {sec.get('content', '')}" for sec in sections]
        section_embeddings = self.model.encode(section_contents, convert_to_tensor=True, show_progress_bar=True)
        query_embedding = self.model.encode(query, convert_to_tensor=True)
        cosine_scores = util.cos_sim(query_embedding, section_embeddings)[0]
        for i, section in enumerate(sections):
            section['relevance_score'] = round(cosine_scores[i].item(), 4)
        return sorted(sections, key=lambda x: x['relevance_score'], reverse=True)[:top_k]

class Summarizer:
    def summarize(self, text, num_sentences=3):
        cleaned_text = _clean_text(text)
        if not cleaned_text or not STOPWORDS: return "Content could not be summarized."
        try:
            sents = sent_tokenize(cleaned_text)
            if len(sents) <= num_sentences: return cleaned_text
            words = word_tokenize(cleaned_text.lower())
            freq = defaultdict(int)
            for word in words:
                if word.isalnum() and word not in STOPWORDS: freq[word] += 1
            if not freq: return " ".join(sents[:num_sentences])
            scores = {sent: sum(freq[word] for word in word_tokenize(sent.lower()) if word in freq) for sent in sents}
            ranked_sents = sorted(scores.items(), key=lambda x: x[1], reverse=True)
            return " ".join([sent for sent, _ in ranked_sents[:num_sentences]])
        except Exception:
            return cleaned_text