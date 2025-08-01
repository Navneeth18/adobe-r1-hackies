import fitz  # PyMuPDF
from collections import defaultdict, Counter


import re
import fitz
from collections import Counter


def is_date_line(text):
    return re.match(r"^\d{1,2}\s+\w+\s+\d{4}$", text.strip().upper())


def is_date_like(text):
    if not text:
        return False

    # Normalize
    text = text.strip().upper()

    date_pattern = re.compile(r"\d{1,2} [A-Z]{3,10} \d{4}")
    matches = date_pattern.findall(text)

    # Count how many words are part of these matches
    total_words = len(text.split())
    total_date_words = len(matches) * 3  # each match is 3 words

    # If 90% or more of the words are dates, it's not a heading
    return total_words > 0 and total_date_words / total_words >= 0.9 and len(matches) >= 2

def merge_title_on_page1(page, size_threshold=11.5):
    """Extract merged title from largest font lines at top of page."""
    blocks = page.get_text("dict")["blocks"]
    lines_by_size = defaultdict(list)

    for block in blocks:
        if block["type"] != 0:
            continue
        for line in block.get("lines", []):
            full_line = ""
            max_size = 0
            for span in line.get("spans", []):
                text = span["text"].strip()
                if not text:
                    continue
                size = round(span["size"], 1)
                if size > size_threshold:
                    full_line += text + " "
                    max_size = max(max_size, size)
            if full_line.strip():
                lines_by_size[max_size].append(full_line.strip())

    if not lines_by_size:
        return ""

    # Choose largest font size's top 1–2 lines
    top_size = max(lines_by_size)
    top_lines = lines_by_size[top_size][:2]
    return "  ".join(top_lines).strip()


def extract_outline_from_page(page):
    from collections import Counter
    import re

    blocks = page.get_text("dict")["blocks"]
    lines = []
    sizes = []

    for block in blocks:
        if block["type"] != 0:
            continue
        for line in block.get("lines", []):
            line_text = ""
            max_size = 0
            top = 0
            for span in line.get("spans", []):
                text = span["text"].strip()
                if not text:
                    continue
                line_text += text + " "
                max_size = max(max_size, round(span["size"], 1))
                top = span["origin"][1]
            if line_text.strip():
                lines.append({"text": line_text.strip(), "size": max_size, "top": top})
                sizes.append(max_size)

    # Analyze font sizes
    size_counter = Counter(sizes)
    sorted_sizes = sorted([s for s in size_counter if s > 11.5], reverse=True)
    size_to_level = {}
    if len(sorted_sizes) > 0:
        size_to_level[sorted_sizes[0]] = "H1"
    if len(sorted_sizes) > 1:
        size_to_level[sorted_sizes[1]] = "H2"
    if len(sorted_sizes) > 2:
        size_to_level[sorted_sizes[2]] = "H3"
    if len(sorted_sizes) > 3:
        size_to_level[sorted_sizes[3]] = "H4"

    headings = []
    buffer = ""
    last_level = None
    last_top = None

    for line in lines:
        level = size_to_level.get(line["size"])
        text = line["text"]

        # Fallback: numbered patterns (not used in your file04 but still useful)
        match = re.match(r"^(\d+(\.\d+)*)(?=\s|:)", text)
        if match:
            dot_count = match.group(1).count(".")
            level = f"H{min(dot_count + 1, 4)}"

        # Fallback: ALL CAPS and large text
        if not level:
            if (
                text.isupper()
                and len(text.split()) <= 6
                and (sorted_sizes and line["size"] >= sorted_sizes[0] * 0.9)
            ):
                level = "H1"
            else:
                continue

        if is_date_line(text):
            continue

        # Merge similar lines close together
        if last_level == level and abs(line["top"] - last_top) <= 25 and not re.match(r"^\d+(\.\d+)+\s", text):
            buffer += " " + text
        else:
            if buffer:
                merged = buffer.strip()
                if not is_date_like(merged):
                    headings.append((last_level, merged))
            buffer = text
            last_level = level
            last_top = line["top"]

    # Flush remaining
    if buffer:
        merged = buffer.strip()
        if not is_date_like(merged):
            headings.append((last_level, merged))

    return headings
