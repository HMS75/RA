"""Day 3: ask a question -> find chunks -> LLM answers using ONLY those chunks, with citations.

Run:  python rag.py "What methods reduce LLM hallucination?"
"""
import argparse
import re
from search import search
from llm import ask_llm

NOT_FOUND = "NOT FOUND IN SOURCES"

SYSTEM_PROMPT = f"""You are a careful research assistant.
You will get a question and numbered SOURCES (pieces of research papers).

Rules:
1. Use ONLY the information inside the sources. Never use outside knowledge.
2. After EVERY sentence that states a fact, add the source number(s) like [1] or [2][3].
3. Only cite a source if it clearly supports that sentence.
4. If the sources do not contain enough information to answer, start your reply with
   "{NOT_FOUND}:" and then say briefly what is missing. Do not guess.
5. If the sources only cover part of the question, answer that part and say what is missing.
6. Keep the answer short and clear: 3 to 6 sentences or a few bullet points."""


# ---------- Step 1: get good chunks (no duplicates) ----------

def retrieve(query, k=6, max_per_paper=2):
    """Hybrid search, then remove repeats so one paper can't fill the whole list."""
    candidates = search(query, mode="hybrid", k=k * 4)   # fetch extra, then trim
    picked, per_paper, seen_text = [], {}, set()
    for c in candidates:
        paper_key = c["title"].strip().lower()
        text_key = c["text"][:100]
        if per_paper.get(paper_key, 0) >= max_per_paper or text_key in seen_text:
            continue
        per_paper[paper_key] = per_paper.get(paper_key, 0) + 1
        seen_text.add(text_key)
        picked.append(c)
        if len(picked) == k:
            break
    return picked


# ---------- Step 2: build the prompt ----------

def build_context(chunks):
    parts = []
    for i, c in enumerate(chunks, start=1):
        parts.append(f"[{i}] {c['title']} ({c['year']}) - Section: {c['section']}\n{c['text']}")
    return "\n\n".join(parts)


# ---------- Step 3: check the answer's citations ----------

CITE_PATTERN = re.compile(r"\[(\d+(?:\s*,\s*\d+)*)\]")


def extract_citations(text):
    """Find all source numbers used in the text, e.g. [1][3] -> {1, 3}"""
    nums = set()
    for group in CITE_PATTERN.findall(text):
        nums.update(int(n) for n in re.split(r"\s*,\s*", group))
    return nums


def find_uncited_sentences(answer):
    """Sentences that state something but have no citation (a warning sign)."""
    uncited = []
    for s in re.split(r"(?<=[.!?])\s+|\n+", answer):
        s = s.strip()
        is_intro_line = s.endswith(":") or s.lower().startswith("based on")
        if len(s) > 40 and not CITE_PATTERN.search(s) and not s.startswith(NOT_FOUND) and not is_intro_line:
            uncited.append(s)
    return uncited


# ---------- Put it all together ----------

def answer_question(question, k=6):
    chunks = retrieve(question, k)
    if not chunks:
        return {"question": question, "answer": f"{NOT_FOUND}: no chunks were retrieved.",
                "found": False, "sources": [], "invalid_citations": [], "uncited_sentences": []}

    user_prompt = f"QUESTION: {question}\n\nSOURCES:\n{build_context(chunks)}"
    answer = ask_llm(SYSTEM_PROMPT, user_prompt)

    cited = extract_citations(answer)
    valid = {n for n in cited if 1 <= n <= len(chunks)}
    invalid = sorted(cited - valid)                       # numbers the LLM made up
    sources = [{"number": n, **chunks[n - 1]} for n in sorted(valid)]

    return {
        "question": question,
        "answer": answer,
        "found": not answer.strip().startswith(NOT_FOUND),
        "sources": sources,                 # only the sources that were actually cited
        "all_retrieved": chunks,            # everything we showed the LLM
        "invalid_citations": invalid,
        "uncited_sentences": find_uncited_sentences(answer),
    }


def print_result(r):
    print("\n" + "=" * 70)
    print("QUESTION:", r["question"])
    print("=" * 70)
    print(r["answer"])
    print("\n--- SOURCES CITED ---")
    for s in r["sources"]:
        print(f"[{s['number']}] {s['title']} ({s['year']}) | arXiv:{s['arxiv_id']} | {s['section']}")
    if r["invalid_citations"]:
        print("\nWARNING: LLM cited source numbers that don't exist:", r["invalid_citations"])
    if r["uncited_sentences"]:
        print("\nWARNING: sentences with no citation:")
        for s in r["uncited_sentences"]:
            print("  -", s[:100])


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("question")
    ap.add_argument("--k", type=int, default=6, help="how many chunks to give the LLM")
    args = ap.parse_args()
    print_result(answer_question(args.question, args.k))