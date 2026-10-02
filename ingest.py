"""Main Day 1 script: topic -> search arXiv -> download PDFs -> parse -> save in SingleStore.

Run:  python ingest.py "LLM hallucination mitigation" --max 10
"""
import argparse
from db import get_conn, init_db
from arxiv_tool import search_papers, download_pdf
from pdf_parser import parse_pdf


def paper_exists(cur, arxiv_id):
    cur.execute("SELECT id FROM papers WHERE arxiv_id = %s", (arxiv_id,))
    return cur.fetchone() is not None


def save_paper(cur, paper, chunks):
    cur.execute(
        "INSERT INTO papers (arxiv_id, title, authors, year, url, abstract) "
        "VALUES (%s, %s, %s, %s, %s, %s)",
        (paper["arxiv_id"], paper["title"], paper["authors"],
         paper["year"], paper["url"], paper["abstract"]),
    )
    paper_id = cur.lastrowid
    rows = [(paper_id, c["section"], c["chunk_index"], c["text"]) for c in chunks]
    cur.executemany(
        "INSERT INTO chunks (paper_id, section, chunk_index, text) VALUES (%s, %s, %s, %s)",
        rows,
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("query", help="research topic to search for")
    ap.add_argument("--max", type=int, default=10, help="how many papers")
    args = ap.parse_args()

    init_db()
    conn = get_conn()
    cur = conn.cursor()

    print(f"Searching arXiv for: {args.query}")
    papers = search_papers(args.query, args.max)
    print(f"Found {len(papers)} papers\n")

    added = 0
    for p in papers:
        if paper_exists(cur, p["arxiv_id"]):
            print(f"[skip] already saved: {p['title'][:60]}")
            continue
        try:
            pdf_path = download_pdf(p)
            chunks = parse_pdf(pdf_path)
            # Always keep the abstract as its own chunk (safety net)
            chunks.insert(0, {"section": "Abstract", "chunk_index": 0, "text": p["abstract"]})
            save_paper(cur, p, chunks)
            conn.commit()
            added += 1
            print(f"[ok]   {len(chunks):3d} chunks | {p['title'][:60]}")
        except Exception as e:
            print(f"[fail] {p['title'][:60]} -> {e}")

    cur.execute("SELECT COUNT(*) FROM papers")
    n_papers = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM chunks")
    n_chunks = cur.fetchone()[0]
    print(f"\nDone. Added {added} new papers. Database now has {n_papers} papers, {n_chunks} chunks.")
    conn.close()


if __name__ == "__main__":
    main()
