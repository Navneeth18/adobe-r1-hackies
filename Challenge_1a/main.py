import os
import re
import json
import fitz  # PyMuPDF

from utils import merge_title_on_page1, extract_outline_from_page

INPUT_DIR = "./input"
OUTPUT_DIR = "./output"

def extract_from_pdf(file_path, page_offset=0):
    import fitz
    import re

    doc = fitz.open(file_path)
    outline = []
    seen = set()

    # Extract raw title from page 1
    raw_title = merge_title_on_page1(doc[0])

    def is_invalid_title(text):
        return bool(re.search(r"\.(cdr|docx?|pdf|ai|indd)$", text.strip().lower()))

    title = "" if not raw_title or is_invalid_title(raw_title) else raw_title

    def is_same_as_title(text, title):
        text_clean = text.strip().lower()
        title_clean = title.strip().lower()
        return (
            text_clean == title_clean
            or text_clean.startswith(title_clean)
            or title_clean in text_clean
        )

    def is_valid_heading(text):
        word_count = len(text.split())
        return (
            word_count <= 8 and
            not re.search(r"(http|www\.|\.com)", text, re.IGNORECASE) and
            not text.lower().startswith(("mission", "address", "rsvp", "page", "date", "time", "parents", "guardian"))
            and not re.match(r"\d{1,5}\s+\w+", text)  # avoid addresses
        )

    if len(doc) == 1:
        # 🔹 Single-page: pick only one valid heading
        headings = extract_outline_from_page(doc[0])
        for level, text in headings:
            if is_same_as_title(text, title):
                continue
            if text in seen:
                continue
            if not is_valid_heading(text):
                continue
            if re.match(r"^\d{1,2} [A-Z]{3,10} \d{4}$", text):
                continue
            if re.match(r"^Page \d+ of \d+", text):
                continue
            seen.add(text)
            outline.append({
                "level": "H1",
                "text": text,
                "page": 0
            })
            break  # ✅ Only one heading
    else:
        # 🔹 Multi-page: extract all valid headings
        for page_num in range(len(doc)):
            page = doc[page_num]
            headings = extract_outline_from_page(page)

            for level, text in headings:
                if is_same_as_title(text, title):
                    continue
                if text in seen:
                    continue
                if re.match(r"^\d{1,2} [A-Z]{3,10} \d{4}$", text):
                    continue
                if re.match(r"^Page \d+ of \d+", text):
                    continue
                seen.add(text)
                outline.append({
                    "level": level,
                    "text": text,
                    "page": page_num + page_offset
                })

        outline = [h for h in outline if h["page"] > 0]

    return {
        "title": title,
        "outline": outline
    }



def main():
    for filename in os.listdir(INPUT_DIR):
        if filename.lower().endswith(".pdf"):
            filepath = os.path.join(INPUT_DIR, filename)

            result = extract_from_pdf(filepath)  # 🔍 Use the extraction function

            json_name = filename.rsplit(".", 1)[0] + ".json"
            outpath = os.path.join(OUTPUT_DIR, json_name)

            with open(outpath, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2, ensure_ascii=False)

            print(f"✅ Processed: {filename} → {json_name}")


if __name__ == "__main__":
    main()
