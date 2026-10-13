"""Day 5: MCP server. Exposes our research tools to any MCP app (Claude Desktop, Cursor, ...).

IMPORTANT: this server talks to the app through stdout, so NEVER use print() in this file or in
the tools it calls. (Use print(..., file=sys.stderr) if you need to debug.)

Test it:   python test_mcp.py
Inspector: mcp dev mcp_server.py
"""
from mcp.server.fastmcp import FastMCP
import tools

mcp = FastMCP("research-agent")


@mcp.tool()
def database_overview() -> dict:
    """Show what the research database currently contains: the number of papers and text chunks,
    and the most recently added papers. Call this first to see which topics are already covered."""
    return tools.database_overview()


@mcp.tool()
def search_arxiv(query: str, max_results: int = 10) -> list[dict]:
    """Search arXiv for papers about a topic. Use 3 to 6 keywords for best results.
    Each result says whether the paper is already in the database ('in_database')."""
    return tools.search_arxiv(query, max_results)


@mcp.tool()
def ingest_papers(arxiv_ids: list[str]) -> dict:
    """Add papers to the database by arXiv id (for example '2401.08358'). Downloads the PDF,
    splits it into sections, and creates search embeddings. Takes roughly 10-30 seconds per paper,
    so add only a few at a time."""
    return tools.ingest_papers(arxiv_ids)


@mcp.tool()
def search_knowledge_base(query: str, k: int = 6) -> list[dict]:
    """Search the papers already in the database (meaning + keyword search).
    Returns text chunks with the paper title, year, arXiv id and section, so you can cite them."""
    return tools.search_knowledge_base(query, k)


@mcp.tool()
def ask_with_citations(question: str, k: int = 6) -> dict:
    """Answer a question using ONLY the database. Every fact in the answer carries a source number.
    If the database does not contain the answer, the reply starts with 'NOT FOUND IN SOURCES'
    (then try search_arxiv + ingest_papers to add relevant papers, and ask again)."""
    return tools.ask_with_citations(question, k)


@mcp.tool()
def compare_papers(arxiv_ids: list[str]) -> list[dict]:
    """Compare papers that are already in the database. For each one, returns the problem,
    method, data/benchmarks, key results and limitations. Use 2 to 5 papers."""
    return tools.compare_papers(arxiv_ids)


@mcp.tool()
def write_literature_review(topic: str, search_arxiv_for_gaps: bool = False) -> str:
    """Run the full research agent on a topic and return a cited literature review in markdown.
    SLOW: it takes several minutes, and some apps stop waiting before it finishes. By default it
    only uses papers already in the database; set search_arxiv_for_gaps=true to let it add new papers."""
    import agent
    result = agent.run_agent(topic, on_event=None, expand=search_arxiv_for_gaps)
    return agent.to_markdown(result)


if __name__ == "__main__":
    mcp.run()          # talks over stdio