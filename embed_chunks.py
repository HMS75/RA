"""Give every chunk an embedding and save it. Safe to re-run (only does missing ones).
    Run by hand:  python embed_chunks.py
    The agent also calls embed_missing() after it adds new papers."""

from db import get_conn
from embedder import embed_texts, to_db_format

BATCH = 64

def embed_missing(verbose=True):
    """Embed all chunks that don't have an embedding yet. Returns how many were done."""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, text FROM chunks WHERE embedding IS NULL")
    rows = cur.fetchall()
    if verbose:
        print(f"{len(rows)} chunks need embeddings")

    for start in range(0, len(rows), BATCH):
        batch = rows[start:start + BATCH]
        vectors = embed_texts([r[1] for r in batch])
        updates = [(to_db_format(v), r[0]) for v, r in zip(vectors, batch)]
        cur.executemany("UPDATE chunks SET embedding = %s WHERE id = %s", updates)
        conn.commit()
        if verbose:
            print(f"  done {min(start + BATCH, len(rows))}/{len(rows)}")

    # Make sure the keyword index has seen all the data
    try:
        cur.execute("OPTIMIZE TABLE chunks FLUSH")
    except Exception as e:
        if verbose:
            print("Optimize step:", e)

    conn.close()
    return len(rows)


if __name__ == "__main__":
    embed_missing()
    print("All chunks embedded.")