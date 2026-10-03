"""Day 2: give every chunk an embedding and save it. Safe to re-run (only does missing ones)."""
from db import get_conn
from embedder import embed_texts, to_db_format

BATCH = 64


def main():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("SELECT id, text FROM chunks WHERE embedding IS NULL")
    rows = cur.fetchall()
    print(f"{len(rows)} chunks need embeddings")

    for start in range(0, len(rows), BATCH):
        batch = rows[start:start + BATCH]
        vectors = embed_texts([r[1] for r in batch])
        updates = [(to_db_format(v), r[0]) for v, r in zip(vectors, batch)]
        cur.executemany("UPDATE chunks SET embedding = %s WHERE id = %s", updates)
        conn.commit()
        print(f"  done {min(start + BATCH, len(rows))}/{len(rows)}")

    # Make sure the keyword index has seen all the data
    try:
        cur.execute("OPTIMIZE TABLE chunks FLUSH")
    except Exception as e:
        print("Optimize step:", e)

    conn.close()
    print("All chunks embedded.")


if __name__ == "__main__":
    main()
