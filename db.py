"""Database helper: connects to SingleStore and creates our tables."""
import os
import singlestoredb as s2
from dotenv import load_dotenv

load_dotenv()


def get_conn():
    required = {
        "S2_HOST": os.getenv("S2_HOST"),
        "S2_USER": os.getenv("S2_USER"),
        "S2_PASSWORD": os.getenv("S2_PASSWORD"),
        "S2_DATABASE": os.getenv("S2_DATABASE"),
    }
    missing = [name for name, value in required.items() if not value]
    if missing:
        raise RuntimeError(
            "Database is not configured. Set " + ", ".join(missing) + "."
        )

    try:
        return s2.connect(
            host=required["S2_HOST"],
            port=int(os.getenv("S2_PORT", "3306")),
            user=required["S2_USER"],
            password=required["S2_PASSWORD"],
            database=required["S2_DATABASE"],
        )
    except Exception as exc:
        raise RuntimeError(f"Database connection failed: {exc}") from exc

# One row per paper
PAPERS_SQL = """
CREATE TABLE IF NOT EXISTS papers (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    arxiv_id VARCHAR(50),
    title TEXT,
    authors TEXT,
    year INT,
    url VARCHAR(300),
    abstract TEXT
)
"""

# One row per small piece of text (chunk) from a paper
CHUNKS_SQL = """
CREATE TABLE IF NOT EXISTS chunks (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    paper_id BIGINT,
    section VARCHAR(50),
    chunk_index INT,
    text TEXT
)
"""


def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(PAPERS_SQL)
    cur.execute(CHUNKS_SQL)
    conn.commit()
    conn.close()
    print("Tables ready: papers, chunks")


if __name__ == "__main__":
    init_db()
