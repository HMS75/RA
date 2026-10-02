"""Read a PDF, split it into sections, then cut each section into small chunks."""
import re
import pymupdf

# Heading words we look for -> the clean name we store
HEADINGS = {
    "abstract": "Abstract",
    "introduction": "Introduction",
    "background": "Background",
    "related work": "Related Work",
    "method": "Methods",
    "methods": "Methods",
    "methodology": "Methods",
    "approach": "Methods",
    "experiment": "Experiments",
    "experiments": "Experiments",
    "results": "Results",
    "evaluation": "Results",
    "discussion": "Discussion",
    "limitation": "Limitations",
    "limitations": "Limitations",
    "conclusion": "Conclusion",
    "conclusions": "Conclusion",
    "future work": "Future Work",
    "references": "References",
}

NUMBER_PREFIX = re.compile(r"^(\d+(\.\d+)*\.?|[IVX]+\.)\s+")


def extract_text(pdf_path):
    doc = pymupdf.open(pdf_path)
    pages = [page.get_text() for page in doc]
    doc.close()
    return "\n".join(pages)


def heading_name(line):
    """If this line looks like a section heading, return its clean name."""
    line = line.strip()
    if not line or len(line) > 40:
        return None
    cleaned = NUMBER_PREFIX.sub("", line).strip().rstrip(":.").lower()
    return HEADINGS.get(cleaned)


def split_sections(text):
    """Return a list of (section_name, section_text). Stops at References."""
    sections = {}
    order = []
    current = "Front"
    found_heading = False

    for line in text.split("\n"):
        name = heading_name(line)
        if name == "References":
            break
        if name:
            found_heading = True
            current = name
            if current not in sections:
                sections[current] = []
                order.append(current)
            continue
        sections.setdefault(current, [])
        if current not in order:
            order.append(current)
        sections[current].append(line)

    result = []
    for name in order:
        body = " ".join(sections[name])
        body = re.sub(r"\s+", " ", body).strip()
        if not body:
            continue
        if found_heading and name == "Front":
            continue  # title/authors area, not useful
        if not found_heading:
            name = "Full Text"  # we couldn't find headings, keep everything
        result.append((name, body))
    return result


def chunk_text(text, size=200, overlap=40):
    """Cut text into pieces of ~200 words, overlapping a bit so ideas aren't cut."""
    words = text.split()
    chunks = []
    step = size - overlap
    for start in range(0, len(words), step):
        piece = words[start:start + size]
        if len(piece) >= 30:  # ignore tiny leftovers
            chunks.append(" ".join(piece))
        if start + size >= len(words):
            break
    return chunks


def parse_pdf(pdf_path):
    """PDF -> list of {section, chunk_index, text}"""
    text = extract_text(pdf_path)
    out = []
    for section, body in split_sections(text):
        for i, piece in enumerate(chunk_text(body)):
            out.append({"section": section, "chunk_index": i, "text": piece})
    return out
