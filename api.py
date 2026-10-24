"""Day 6: web API (FastAPI). The Next.js frontend will talk to this.

Endpoints
  GET  /api/health
  GET  /api/overview                  what's in the database
  POST /api/ask                       {question, k} -> cited answer (quick, no agent)
  GET  /api/research/stream           ?topic=...&expand=true  -> live agent steps (Server-Sent Events)
  GET  /api/reviews                   list saved reviews
  GET  /api/reviews/{slug}            one saved review (full JSON)

The streaming endpoint sends these SSE events:
  step    one agent step, e.g. {"step": "search", "message": "Searching arXiv: ..."}
  result  the final review (sent once, at the end)
  error   {"message": "..."} if the agent crashed
  end     the stream is finished

Run:  uvicorn api:app --port 8000
"""
import asyncio
import glob
import json
import os
import queue
import re
import sys
import threading
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

import agent
import embedder
import llm
import tools

REVIEWS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reviews")

# Only ONE research run at a time: each run makes ~20 LLM calls and uses lots of memory.
_run_lock = threading.Lock()


@asynccontextmanager
async def lifespan(app):
    # Load the embedding model once at startup so the first request isn't slow
    try:
        await asyncio.to_thread(embedder.embed_query, "warm up")
    except Exception as e:
        print("Embedding warm-up failed:", e, file=sys.stderr)
    yield


app = FastAPI(title="Research Paper Agent API", lifespan=lifespan)

origins = [o.strip() for o in os.getenv("ALLOWED_ORIGINS", "https://ra-wine-chi.vercel.app").split(",")]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_methods=["*"], allow_headers=["*"])


def sse(event, data):
    """Format one Server-Sent Event."""
    return f"event: {event}\ndata: {json.dumps(data, default=str)}\n\n"


# ---------------- simple endpoints ----------------

@app.get("/api/health")
def health():
    return {"status": "ok", "llm_provider": llm.PROVIDER, "llm_model": llm.MODEL,
            "busy": _run_lock.locked()}


@app.get("/api/overview")
def overview():
    return tools.database_overview()


class AskBody(BaseModel):
    question: str = Field(min_length=3, max_length=300)
    k: int = Field(6, ge=1, le=12)


@app.post("/api/ask")
def ask(body: AskBody):
    return tools.ask_with_citations(body.question, body.k)


# ---------------- the live agent ----------------

@app.get("/api/research/stream")
async def research_stream(request: Request,
                          topic: str = Query(..., min_length=3, max_length=200),
                          expand: bool = True):
    if not _run_lock.acquire(blocking=False):
        raise HTTPException(429, "The agent is busy with another request. Try again in a few minutes.")

    events = queue.Queue()

    def worker():
        # The agent is normal (blocking) Python, so it runs in its own thread
        # and drops its events into a queue.
        try:
            result = agent.run_agent(topic, on_event=lambda e: events.put(("step", e)), expand=expand)
            path = agent.save_result(result)          # saved, so the page can reload it later
            result["slug"] = os.path.splitext(os.path.basename(path))[0]
            events.put(("result", result))
        except Exception as e:
            events.put(("error", {"message": str(e)}))
        finally:
            events.put(("end", {}))
            _run_lock.release()

    threading.Thread(target=worker, daemon=True).start()

    async def generator():
        loop = asyncio.get_running_loop()
        while True:
            try:
                kind, data = await loop.run_in_executor(None, lambda: events.get(timeout=10))
            except queue.Empty:
                if await request.is_disconnected():
                    break
                yield ": keep-alive\n\n"          # keeps the connection open while the LLM thinks
                continue
            yield sse(kind, data)
            if kind == "end":
                break

    return StreamingResponse(generator(), media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


# ---------------- saved reviews ----------------

@app.get("/api/reviews")
def list_reviews():
    out = []
    for path in glob.glob(os.path.join(REVIEWS_DIR, "*.json")):
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            continue
        out.append({"slug": os.path.splitext(os.path.basename(path))[0],
                    "topic": data.get("topic"),
                    "sources": len(data.get("sources", [])),
                    "created": os.path.getmtime(path)})
    out.sort(key=lambda r: r["created"], reverse=True)
    return out


@app.get("/api/reviews/{slug}")
def get_review(slug: str):
    if not re.fullmatch(r"[a-z0-9-]+", slug):          # blocks things like ../../secret
        raise HTTPException(400, "Bad review id")
    path = os.path.join(REVIEWS_DIR, slug + ".json")
    if not os.path.exists(path):
        raise HTTPException(404, "Review not found")
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    data["slug"] = slug
    return data
