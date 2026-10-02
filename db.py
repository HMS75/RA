"""Database helper: connects to SingleStore and creates our tables."""
import os
import singlestoredb as s2
from dotenv import load_dotenv

load_dotenv()


def get_conn():
    return s2.connect(
        host=os.environ["S2_HOST"],
        port=int(os.getenv("S2_PORT", "3306")),
        user=os.environ["S2_USER"],
        password=os.environ["S2_PASSWORD"],
        database=os.environ["S2_DATABASE"],
    )


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
