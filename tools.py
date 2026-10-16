"""The agent's TOOLS. Each one does one clear job and returns plain data (dicts / lists).

The agent uses them today. On Day 5 we will also expose the same tools through an MCP server,
so keep them simple: clear name, clear inputs, JSON-friendly outputs.
"""
import re
from db import get_conn
from arxiv_tool import search_papers, get_papers_by_ids, download_pdf
from pdf_parser import parse_pdf
from ingest import save_paper
from embed_chunks import embed_missing
from rag import retrieve, answer_question
from llm_json import ask_json


# ---------- small helpers ----------

def _base_id(arxiv_id):
    """'2401.08358v2' -> '2401.08358' (so v1 and v2 count as the same paper)."""
    return re.sub(r"v\d+$", "", arxiv_id)


def _in_db(cur, arxiv_id):
    base = _base_id(arxiv_id)
    cur.execute("SELECT id FROM papers WHERE arxiv_id = %s OR arxiv_id LIKE %s",
                (base, base + "v%"))
    return cur.fetchone() is not None


# ---------- Tool 1 ----------

def search_arxiv(query, max_results=10):
    """Search arXiv for papers about a topic. Tells you which ones are already in our database."""
    papers = search_papers(query, max_results)
    conn = get_conn()
    cur = conn.cursor()
    out = []
    for p in papers:
        out.append({
            "arxiv_id": p["arxiv_id"], "title": p["title"], "authors": p["authors"],
            "year": p["year"], "url": p["url"], "abstract": p["abstract"],
            "in_database": _in_db(cur, p["arxiv_id"]),
        })
    conn.close()
    return out


# ---------- Tool 2 ----------

def ingest_papers(arxiv_ids):
    """Download papers by arXiv id, split into chunks, save them, and create embeddings."""
    papers = get_papers_by_ids(arxiv_ids)
    conn = get_conn()
    cur = conn.cursor()
    results, added = [], 0
    for p in papers:
        if _in_db(cur, p["arxiv_id"]):
            results.append({"arxiv_id": p["arxiv_id"], "title": p["title"], "status": "already_saved"})
            continue
        try:
            chunks = parse_pdf(download_pdf(p))
            chunks.insert(0, {"section": "Abstract", "chunk_index": 0, "text": p["abstract"]})
            save_paper(cur, p, chunks)
            conn.commit()
            added += 1
            results.append({"arxiv_id": p["arxiv_id"], "title": p["title"],
                            "status": "added", "chunks": len(chunks)})
        except Exception as e:
            results.append({"arxiv_id": p["arxiv_id"], "title": p["title"],
                            "status": "failed", "error": str(e)})
    conn.close()
    embedded = embed_missing(verbose=False) if added else 0
    return {"papers_added": added, "chunks_embedded": embedded, "results": results}


# ---------- Tool 3 ----------

def search_knowledge_base(query, k=6):
    """Search the papers already in our database (meaning + keyword search, no duplicates)."""
    return retrieve(query, k)


# ---------- Tool 4 ----------

def ask_with_citations(question, k=6):
    """Answer a question using only our database. Every fact gets a source number."""
    r = answer_question(question, k)
    r.pop("all_retrieved", None)
    return r


# ---------- Tool 5 ----------

SECTION_ORDER = ["Abstract", "Methods", "Experiments", "Results",
                 "Discussion", "Limitations", "Conclusion", "Full Text"]


def _paper_context(cur, paper_id, max_words=1400):
    cur.execute("SELECT section, chunk_index, text FROM chunks WHERE paper_id = %s "
                "ORDER BY chunk_index", (paper_id,))
    by_section = {}
    for section, _, text in cur.fetchall():
        by_section.setdefault(section, []).append(text)
    parts, words = [], 0
    for section in SECTION_ORDER:
        for text in by_section.get(section, [])[:2]:      # at most 2 chunks per section
            if words > max_words:
                break
            parts.append(f"[{section}] {text}")
            words += len(text.split())
    return "\n\n".join(parts)


def compare_papers(arxiv_ids):
    """For each paper, extract: problem, method, data/benchmarks, key results, limitations."""
    conn = get_conn()
    cur = conn.cursor()
    rows = []
    for aid in arxiv_ids:
        base = _base_id(aid)
        cur.execute("SELECT id, title, year, arxiv_id FROM papers "
                    "WHERE arxiv_id = %s OR arxiv_id LIKE %s", (base, base + "v%"))
        found = cur.fetchone()
        if not found:
            rows.append({"arxiv_id": aid, "error": "paper not in database"})
            continue
        paper_id, title, year, stored_id = found
        context = _paper_context(cur, paper_id)
        system = "You extract facts from research paper text. Use ONLY the text given."
        user = ("PAPER: " + title + "\n\nTEXT:\n" + context + "\n\n"
                "Reply as JSON with these keys, each a short string of at most 25 words: "
                '{"problem": "", "method": "", "data_or_benchmarks": "", '
                '"key_results": "", "limitations": ""}. '
                'If something is not in the text, write "not stated".')
        try:
            info = ask_json(system, user)
        except Exception as e:
            info = {"error": str(e)}
        rows.append({"arxiv_id": stored_id, "title": title, "year": year, **info})
    conn.close()
    return rows


# ---------- Tool 6 ----------

def database_overview(recent=10):
    """Show how many papers/chunks the database holds and which papers were added last."""
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM papers")
        n_papers = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM chunks")
        n_chunks = cur.fetchone()[0]
        cur.execute("SELECT title, year, arxiv_id FROM papers ORDER BY id DESC LIMIT %s", (recent,))
        latest = [{"title": r[0], "year": r[1], "arxiv_id": r[2]} for r in cur.fetchall()]
        conn.close()
        return {"papers": n_papers, "chunks": n_chunks, "most_recently_added": latest}
    except Exception as exc:
        return {"papers": 0, "chunks": 0, "most_recently_added": [], "status": "unavailable", "error": str(exc)}


ALL_TOOLS = [search_arxiv, ingest_papers, search_knowledge_base,
             ask_with_citations, compare_papers, database_overview]