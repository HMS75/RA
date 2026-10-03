"""Day 2 setup (run once): adds a place for embeddings + a keyword-search index."""
from db import get_conn
from embedder import DIM


def main():
    conn = get_conn()
    cur = conn.cursor()

    # 1) Column that will hold each chunk's embedding
    try:
        cur.execute(f"ALTER TABLE chunks ADD COLUMN embedding VECTOR({DIM}) NULL")
        print("Added embedding column")
    except Exception as e:
        print("Embedding column step:", e)

    # 2) Keyword (full-text) index on the chunk text
    try:
        cur.execute("ALTER TABLE chunks ADD FULLTEXT USING VERSION 2 chunks_ft (text)")
        print("Added full-text index")
    except Exception as e:
        print("Full-text index step:", e)

    conn.commit()
    conn.close()
    print("Setup done.")


if __name__ == "__main__":
    main()
