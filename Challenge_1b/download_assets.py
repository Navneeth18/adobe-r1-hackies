import nltk
from sentence_transformers import SentenceTransformer
import os

# Define the directories
model_dir = "models"
nltk_dir = "nltk_data"

# Create directories if they don't exist
os.makedirs(model_dir, exist_ok=True)
os.makedirs(nltk_dir, exist_ok=True)

print("--- Starting Asset Download ---")

# 1. Download and save the Sentence Transformer model
model_name = 'all-MiniLM-L6-v2'
model_path = os.path.join(model_dir, model_name)

if not os.path.exists(model_path):
    print(f"Downloading Sentence Transformer model: '{model_name}'...")
    model = SentenceTransformer(model_name)
    model.save(model_path)
    print(f"✅ Model saved successfully to '{model_path}'")
else:
    print(f"✅ Model '{model_name}' already exists. Skipping download.")


# 2. Download and save NLTK data
print("\nDownloading NLTK data (punkt & stopwords)...")
try:
    nltk.data.find('tokenizers/punkt')
    print("✅ NLTK 'punkt' tokenizer already downloaded.")
except LookupError:
    nltk.download('punkt', download_dir=nltk_dir)
    print("✅ NLTK 'punkt' saved successfully.")

try:
    nltk.data.find('corpora/stopwords')
    print("✅ NLTK 'stopwords' already downloaded.")
except LookupError:
    nltk.download('stopwords', download_dir=nltk_dir)
    print("✅ NLTK 'stopwords' saved successfully.")

print("\n--- Asset download complete! ---")