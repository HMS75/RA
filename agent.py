"""Day 4: the research agent.

Topic in -> plan -> check what we know -> (search arXiv + add papers if needed)
         -> retrieve -> compare papers -> write a cited literature review.

Run:  python agent.py "impact of noisy data on language model performance"
Quick test without going to arXiv:  python agent.py "your topic" --no-expand
"""
import argparse
import json
import os
import re

import tools
from llm_json import ask_json, ask_text
from rag import extract_citations, find_uncited_sentences

# ---- settings you can tweak ----
MAX_SUBQUESTIONS = 3      # how many sub-questions the plan can have
MAX_ROUNDS = 2            # how many times we try to find new papers per sub-question
INGEST_PER_ROUND = 4      # max new papers added per attempt
COVERAGE_OK = 7           # score (0-10) at which we say "we know enough"
FILTER_MIN_SCORE = 7     # a new paper needs at least this score (0-10) to be added
CHUNKS_PER_QUESTION = 6
MAX_COMPARE = 5           # how many papers go in the comparison table


# =====================  small LLM "skills" the agent uses  =====================

def plan(topic):
    """Step 1 - PLAN: split the topic into 2-3 sub-questions."""
    system = "You help plan a literature review by breaking a research topic into focused sub-questions."
    user = ("TOPIC: " + topic + "\n\n"
            "Write 2 or 3 sub-questions that together cover the topic "
            "(for example: main approaches, how they are evaluated, limitations). "
            "For each one also write a short arXiv search query (3 to 6 keywords, no punctuation).\n"
            'Reply as JSON: {"sub_questions": [{"question": "...", "search_query": "..."}]}')
    data = ask_json(system, user)
    subs = []
    for item in data.get("sub_questions", [])[:MAX_SUBQUESTIONS]:
        if isinstance(item, dict) and item.get("question"):
            subs.append({"question": item["question"],
                         "search_query": item.get("search_query") or item["question"]})
    return subs or [{"question": topic, "search_query": topic}]


def check_coverage(question, chunks):
    """Step 2 - CHECK: do the chunks we have actually cover the question? Score 0-10."""
    if not chunks:
        return {"score": 0, "missing": "nothing was retrieved"}
    passages = "\n\n".join(f"- ({c['title']}, {c['section']}) {c['text'][:700]}" for c in chunks)
    system = "You judge whether research passages contain enough to answer a question."
    user = ("QUESTION: " + question + "\n\nPASSAGES:\n" + passages + "\n\n"
            "Score from 0 to 10 how well these passages together contain what is needed to answer "
            "the question. 10 = fully answers it, 5 = partly relevant, 0 = unrelated.\n"
            'Reply as JSON: {"score": 0, "missing": "short note on what is missing"}')
    data = ask_json(system, user)
    try:
        score = int(float(data.get("score", 0)))
    except (TypeError, ValueError):
        score = 0
    return {"score": score, "missing": str(data.get("missing", ""))}


def filter_candidates(question, candidates):
    """Step 4 - FILTER: score new arXiv papers by relevance, keep only the good ones.
    Returns (ids_to_keep, best_scores) so we can show what the LLM thought."""
    listing = "\n\n".join(f"ID: {c['arxiv_id']}\nTitle: {c['title']}\nAbstract: {c['abstract'][:500]}"
                          for c in candidates)
    system = "You pick which research papers are truly relevant to a question."
    user = ("QUESTION: " + question + "\n\nCANDIDATE PAPERS:\n" + listing + "\n\n"
            "Score each paper from 0 to 10 for how useful it is for answering the question. "
            "Papers that directly address the question deserve 7 or more.\n"
            'Reply as JSON: {"papers": [{"arxiv_id": "...", "score": 0}]}')
    data = ask_json(system, user, max_tokens=2000)
    items = data if isinstance(data, list) else (data.get("papers") or data.get("results") or [])

    # LLMs sometimes change the id format (add "arXiv:", drop the version...), so compare base ids
    by_base = {tools._base_id(c["arxiv_id"]): c["arxiv_id"] for c in candidates}
    scored = []
    for item in items:
        if not isinstance(item, dict):
            continue
        raw = str(item.get("arxiv_id") or item.get("id") or "").strip()
        base = tools._base_id(re.sub(r"^arxiv:\s*", "", raw, flags=re.I))
        if base in by_base:
            try:
                scored.append((by_base[base], float(item.get("score", 0))))
            except (TypeError, ValueError):
                pass
    scored.sort(key=lambda x: x[1], reverse=True)
    picks = [aid for aid, sc in scored if sc >= FILTER_MIN_SCORE][:INGEST_PER_ROUND]
    return picks, [sc for _, sc in scored[:5]]


def rewrite_query(question, tried, missing):
    """Self-check loop: the last search didn't help, so write a better search query."""
    system = "You write short arXiv search queries."
    user = ("QUESTION: " + question + "\nQueries already tried: " + "; ".join(tried) +
            "\nWhat was missing: " + missing + "\n\n"
            "Write ONE new arXiv search query (3 to 6 keywords) that is different from the ones "
            "already tried and more likely to find the missing information.\n"
            'Reply as JSON: {"search_query": "..."}')
    return ask_json(system, user).get("search_query") or tried[-1]


SYNTH_SYSTEM = """You write a short literature review for a researcher.
You get a TOPIC and numbered SOURCES (pieces of research papers).

Rules:
1. Use ONLY facts found in the numbered sources. Never use outside knowledge.
2. EVERY sentence and EVERY bullet that states a fact MUST end with source number(s) in square brackets.
   Good: "Fine-tuning on curated data lowered hallucination rates in two studies [2][5]."
   Bad:  "Fine-tuning on curated data lowered hallucination rates."
3. If you cannot support a sentence with a source, do not write it.
4. If a part of the topic has weak evidence, say so honestly in the last section.
5. Write in clear, simple English. Use exactly these markdown sections:
## Overview
## Main approaches
## How the papers compare
## Limitations and open problems
## Gaps in the evidence"""

REPAIR_SYSTEM = """You fix the citations in a literature review draft.
You get numbered SOURCES and a DRAFT.
For every sentence or bullet in the draft:
- if a source supports it, keep it and end it with the source number(s), like [3] or [2][5];
- if NO source supports it, delete it.
Do not add new facts. Keep the same markdown section headings.
Reply with the full corrected review only."""


def normalize_citations(text):
    """Turn other citation styles into plain [n]: 【3】, [Source 3], (Source 3), [S3]."""
    text = re.sub(r"【\s*(\d+)[^】]*】", r"[\1]", text)
    text = re.sub(r"\[\s*(?:sources?|s)\s*(\d+(?:\s*,\s*\d+)*)\s*\]", r"[\1]", text, flags=re.I)
    text = re.sub(r"\(\s*sources?\s*(\d+(?:\s*,\s*\d+)*)\s*\)", r"[\1]", text, flags=re.I)
    return text


def _factual_sentences(text):
    parts = re.split(r"(?<=[.!?])\s+|\n+", text)
    return [x.strip() for x in parts if len(x.strip()) > 40 and not x.strip().startswith("#")]


def ensure_citations(review, sources_text, max_attempts=2):
    """Repair uncited sentences while keeping prompts smaller.
    Returns (review, number_of_repair_attempts)."""
    def uncited_ratio(t):
        sents = _factual_sentences(t)
        return 1.0 if not sents else len(find_uncited_sentences(t)) / len(sents)
    best, best_ratio, attempts = review, uncited_ratio(review), 0
    # Keep the repair prompt smaller to reduce TPM errors.
    MAX_SOURCE_CHARS = 10000
    MAX_DRAFT_CHARS = 10000
    sources_for_repair = sources_text[:MAX_SOURCE_CHARS]
    while best_ratio > 0.25 and attempts < max_attempts:
        attempts += 1
        draft_for_repair = best[:MAX_DRAFT_CHARS]
        prompt = (
            "SOURCES:\n" + sources_for_repair
            + "\n\nDRAFT:\n" + draft_for_repair
        )
        try:
            fixed = normalize_citations(
                ask_text(REPAIR_SYSTEM, prompt, max_tokens=2500)
            )
        except RuntimeError as e:
            print(f"[CITATION_REPAIR] Attempt {attempts} failed: {e}")
            break
        if not fixed.strip():
            break
        ratio = uncited_ratio(fixed)
        if ratio < best_ratio and len(fixed) > 0.4 * len(best):
            best, best_ratio = fixed, ratio
    return best, attempts


# =====================  the agent  =====================

def run_agent(topic, on_event=None, expand=True):
    log = []

    def emit(step, message, **data):
        event = {"step": step, "message": message, **data}
        log.append(event)
        if on_event:
            on_event(event)

    # ---- 1. PLAN ----
    emit("plan", "Breaking the topic into sub-questions...")
    subs = plan(topic)
    emit("plan_done", f"Plan: {len(subs)} sub-questions", sub_questions=subs)

    # ---- 2-5. for each sub-question: check, maybe expand, retrieve ----
    results = []
    for i, sq in enumerate(subs, start=1):
        q = sq["question"]
        emit("check", f"[{i}/{len(subs)}] Checking what we already know: {q}")
        chunks = tools.search_knowledge_base(q, CHUNKS_PER_QUESTION)
        cov = check_coverage(q, chunks)
        emit("coverage", f"Coverage score {cov['score']}/10", score=cov["score"], missing=cov["missing"])

        tried = [sq["search_query"]]
        query, rounds, added_total = sq["search_query"], 0, 0
        while expand and cov["score"] < COVERAGE_OK and rounds < MAX_ROUNDS:
            rounds += 1
            if rounds > 1:
                query = rewrite_query(q, tried, cov["missing"])
                tried.append(query)
                emit("rewrite", f"Trying a better search query: {query}", query=query)
            emit("search", f"Searching arXiv: {query}", query=query)
            found = tools.search_arxiv(query, 10)
            new = [p for p in found if not p["in_database"]]
            emit("search_done", f"Found {len(found)} papers, {len(new)} are new", total=len(found), new=len(new))
            if not new:
                continue
            picks, best = filter_candidates(q, new)
            titles = [p["title"] for p in new if p["arxiv_id"] in picks]
            emit("filter", f"Kept {len(picks)} relevant papers (top scores the LLM gave: {best or 'none readable'})",
                 papers=titles, top_scores=best)
            if not picks:
                continue
            emit("ingest", "Downloading and adding papers (this takes a minute)...")
            res = tools.ingest_papers(picks)
            added_total += res["papers_added"]
            emit("ingest_done", f"Added {res['papers_added']} papers, {res['chunks_embedded']} chunks",
                 results=res["results"])
            chunks = tools.search_knowledge_base(q, CHUNKS_PER_QUESTION)
            cov = check_coverage(q, chunks)
            emit("coverage", f"Coverage score now {cov['score']}/10", score=cov["score"], missing=cov["missing"])

        results.append({"question": q, "chunks": chunks, "coverage": cov, "papers_added": added_total})

    # ---- 6. pick papers to compare (the ones that show up most) ----
    counts, order, titles = {}, [], {}
    for r in results:
        for c in r["chunks"]:
            aid = c["arxiv_id"]
            titles[aid] = c["title"]
            if aid not in counts:
                counts[aid] = 0
                order.append(aid)
            counts[aid] += 1
    ranked = sorted(order, key=lambda a: (-counts[a], order.index(a)))[:MAX_COMPARE]
    emit("compare", f"Comparing {len(ranked)} papers...", papers=[titles[a] for a in ranked])
    comparison = tools.compare_papers(ranked)

    # ---- 7. write the review ----
    numbered, seen = [], {}
    for r in results:
        for c in r["chunks"]:
            if c["chunk_id"] not in seen:
                seen[c["chunk_id"]] = len(numbered) + 1
                numbered.append({"number": len(numbered) + 1, **c})
    sources_text = "\n\n".join(
        f"[{s['number']}] {s['title']} ({s['year']}) - Section: {s['section']}\n{s['text']}"
        for s in numbered)
    weak = [r["question"] for r in results if r["coverage"]["score"] < COVERAGE_OK]
    weak_note = ("Sub-questions with WEAK evidence: " + "; ".join(weak)) if weak else "All sub-questions had decent evidence."
    user = (f"TOPIC: {topic}\n\n{weak_note}\n\nSOURCES:\n{sources_text}\n\n"
            "Remember: end every factual sentence with source numbers like [1] or [2][4].")
    emit("write", "Writing the literature review...")
    review = normalize_citations(ask_text(SYNTH_SYSTEM, user, max_tokens=4000))
    review, repairs = ensure_citations(review, sources_text)
    if repairs:
        emit("repair", f"Citations were missing, asked the LLM to fix them ({repairs} attempt(s))")

    # ---- 8. check the citations ----
    cited = extract_citations(review)
    valid = {n for n in cited if 1 <= n <= len(numbered)}
    sources = []
    for s in numbered:
        if s["number"] in valid:
            sources.append({**s, "url": f"https://arxiv.org/abs/{s['arxiv_id']}"})
    result = {
        "topic": topic,
        "sub_questions": [{"question": r["question"], "coverage": r["coverage"],
                           "papers_added": r["papers_added"]} for r in results],
        "review": review,
        "comparison": comparison,
        "sources": sources,
        "invalid_citations": sorted(cited - valid),
        "uncited_sentences": find_uncited_sentences(review),
        "log": log,
    }
    emit("done", f"Done. {len(sources)} sources cited.")
    return result


# =====================  saving + printing  =====================

def _cell(text):
    return str(text or "").replace("|", "/").replace("\n", " ")


def to_markdown(r):
    lines = [f"# Literature review: {r['topic']}", "", r["review"], "", "## Paper comparison", "",
             "| Paper | Method | Data / benchmarks | Key results | Limitations |",
             "|---|---|---|---|---|"]
    for p in r["comparison"]:
        if "title" in p and "method" in p:
            lines.append(f"| {_cell(p['title'])} ({p['year']}) | {_cell(p['method'])} | "
                         f"{_cell(p['data_or_benchmarks'])} | {_cell(p['key_results'])} | {_cell(p['limitations'])} |")
    lines += ["", "## Sources", ""]
    for s in r["sources"]:
        lines.append(f"[{s['number']}] {s['title']} ({s['year']}), section: {s['section']} - {s['url']}")
    if r["invalid_citations"] or r["uncited_sentences"]:
        lines += ["", "## Warnings", ""]
        if r["invalid_citations"]:
            lines.append(f"- Citation numbers that don't exist: {r['invalid_citations']}")
        for s in r["uncited_sentences"]:
            lines.append(f"- No citation: {s[:120]}")
    return "\n".join(lines)


def save_result(r, folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), "reviews")):
    os.makedirs(folder, exist_ok=True)
    slug = re.sub(r"[^a-z0-9]+", "-", r["topic"].lower()).strip("-")[:60]
    md_path = os.path.join(folder, slug + ".md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(to_markdown(r))
    with open(os.path.join(folder, slug + ".json"), "w", encoding="utf-8") as f:
        json.dump(r, f, indent=2, default=str)
    return md_path


def print_event(e):
    print(f"[{e['step'].upper():12}] {e['message']}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("topic")
    ap.add_argument("--no-expand", action="store_true",
                    help="only use papers already in the database (fast test)")
    args = ap.parse_args()

    result = run_agent(args.topic, on_event=print_event, expand=not args.no_expand)
    path = save_result(result)
    print("\n" + "=" * 70 + "\n")
    print(to_markdown(result))
    print(f"\nSaved to {path}")