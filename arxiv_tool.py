"""Tool 1: search arXiv for papers and download their PDFs."""
import os
import arxiv
import requests

PDF_DIR = "pdfs"


def search_papers(query, max_results=10):
    """Return a list of papers (as simple dicts) matching the query."""
    client = arxiv.Client()
    search = arxiv.Search(
        query=query,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.Relevance,
    )
    papers = []
    for r in client.results(search):
        papers.append({
            "arxiv_id": r.get_short_id(),
            "title": r.title.strip().replace("\n", " "),
            "authors": ", ".join(a.name for a in r.authors),
            "year": r.published.year,
            "url": r.entry_id,
            "abstract": r.summary.strip().replace("\n", " "),
            "pdf_url": r.pdf_url,
        })
    return papers


def download_pdf(paper):
    """Download the PDF to the pdfs/ folder. Skips if already downloaded."""
    os.makedirs(PDF_DIR, exist_ok=True)
    safe_id = paper["arxiv_id"].replace("/", "_")
    path = os.path.join(PDF_DIR, f"{safe_id}.pdf")
    if os.path.exists(path):
        return path
    resp = requests.get(paper["pdf_url"], timeout=60)
    resp.raise_for_status()
    with open(path, "wb") as f:
        f.write(resp.content)
    return path
