import nltk
from collections import defaultdict

# Use local nltk data
nltk.data.path.append('./nltk_data')

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize

class Summarizer:
    def __init__(self):
        try:
            self.stopwords = set(stopwords.words("english"))
            print("[INFO] NLTK stopwords loaded for Summarizer.")
        except Exception:
            raise RuntimeError("NLTK 'stopwords' not found. Please run the download script.")

    def summarize(self, text, max_sentences=3):
        """Extracts the most important sentences from a text block."""
        try:
            if not text:
                return "Not enough content to summarize."
            
            sents = sent_tokenize(text)
            if len(sents) <= max_sentences:
                return text

            words = word_tokenize(text.lower())
            freq = defaultdict(int)
            for word in words:
                if word.isalnum() and word not in self.stopwords:
                    freq[word] += 1
            
            if not freq:
                return " ".join(sents[:max_sentences])

            scores = {sent: sum(freq[word] for word in word_tokenize(sent.lower()) if word in freq) for sent in sents}
            
            ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
            summary = " ".join([sent for sent, _ in ranked[:max_sentences]])
            return summary if summary else text
        except Exception as e:
            return f"[ERROR] Summary generation failed: {e}"