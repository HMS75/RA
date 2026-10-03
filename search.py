"""Day 2: search the chunks three ways -> vector, keyword, or hybrid (both mixed).

Run:  python search.py "methods for reducing LLM hallucination" --mode hybrid --k 5
"""
import argparse
import re
from db import get_conn
from embedder import embed_query, to_db_format, DIM

STOPWORDS = {"the", "and", "for", "with", "that", "this", "are", "from", "how",
             "what", "which", "can", "using", "use", "into", "about", "your"}


def clean_keywords(query):
    """Keep only simple words so special characters can't break the search."""
    words = re.findall(r"[a-z0-9]+", query.lower())
    return [w for w in words if len(w) > 2 and w not in STOPWORDS]


def vector_search(query, k=20):
    """Find chunks whose MEANING is close to the question. Returns [(chunk_id, score)]."""
    qvec = to_db_format(embed_query(query))
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        f"SELECT id, embedding <*> (%s :> VECTOR({DIM})) AS score "
        "FROM chunks WHERE embedding IS NOT NULL ORDER BY score DESC LIMIT %s",
        (qvec, k),
    )
    rows = cur.fetchall()
    conn.close()
    return [(r[0], float(r[1])) for r in rows]


def keyword_search(query, k=20):
    """Find chunks that contain the actual WORDS. Returns [(chunk_id, score)]."""
    words = clean_keywords(query)
    if not words:
        return []
    q = "text:(" + " ".join(words) + ")"
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, MATCH(TABLE chunks) AGAINST (%s) AS score FROM chunks "
        "WHERE MATCH(TABLE chunks) AGAINST (%s) ORDER BY score DESC LIMIT %s",
        (q, q, k),
    )
    rows = cur.fetchall()
    conn.close()
    return [(r[0], float(r[1])) for r in rows]


def combine_rankings(rank_lists, k=60):
    """Mix several ranked lists into one (called Reciprocal Rank Fusion).
    A chunk scores higher the closer to the top it appears in each list."""
    scores = {}
    for ranked in rank_lists:
        for position, (chunk_id, _) in enumerate(ranked, start=1):
            scores[chunk_id] = scores.get(chunk_id, 0) + 1 / (k + position)
    return sorted(scores.items(), key=lambda x: x[1], reverse=True)


def hybrid_search(query, k=20):
    return combine_rankings([vector_search(query, k), keyword_search(query, k)])[:k]


def fetch_chunks(ranked):
    """Turn [(chunk_id, score)] into full results with title, section and text."""
    if not ranked:
        return []
    ids = [cid for cid, _ in ranked]
    placeholders = ",".join(["%s"] * len(ids))
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT c.id, p.title, p.arxiv_id, p.year, c.section, c.text "
        "FROM chunks c JOIN papers p ON p.id = c.paper_id "
        f"WHERE c.id IN ({placeholders})",
        ids,
    )
    info = {r[0]: r for r in cur.fetchall()}
    conn.close()
    results = []
    for cid, score in ranked:
        if cid in info:
            _, title, arxiv_id, year, section, text = info[cid]
            results.append({"chunk_id": cid, "score": score, "title": title,
                            "arxiv_id": arxiv_id, "year": year,
                            "section": section, "text": text})
    return results


def search(query, mode="hybrid", k=5):
    """The one function the rest of the project will call."""
    fn = {"vector": vector_search, "keyword": keyword_search, "hybrid": hybrid_search}[mode]
    return fetch_chunks(fn(query, k)[:k])


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("query")
    ap.add_argument("--mode", choices=["vector", "keyword", "hybrid"], default="hybrid")
    ap.add_argument("--k", type=int, default=5)
    args = ap.parse_args()

    for i, r in enumerate(search(args.query, args.mode, args.k), start=1):
        print(f"\n#{i}  [{r['section']}]  {r['title']} ({r['year']})  score={r['score']:.4f}")
        print("   ", r["text"][:300].replace("\n", " "), "...")
