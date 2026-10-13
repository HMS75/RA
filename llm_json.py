import json
import time
from llm import ask_llm


def parse_json(text):
    """Find the JSON inside the LLM's reply (even if it added extra words or ``` fences)."""
    text = text.strip()
    starts = [i for i in (text.find("{"), text.find("[")) if i != -1]
    if not starts:
        raise ValueError("no JSON found in reply")
    start = min(starts)
    end = max(text.rfind("}"), text.rfind("]"))
    return json.loads(text[start:end + 1])


def ask_json(system, user, retries=3, max_tokens=1500):
    last_error = None
    for attempt in range(retries):
        try:
            raw = ask_llm(
                system + "\n\nReply with JSON only. No extra words, no markdown fences.",
                user, max_tokens=max_tokens)
            return parse_json(raw)
        except Exception as e:          # bad JSON, rate limit, network hiccup...
            last_error = e
            time.sleep(3 * (attempt + 1))
    raise RuntimeError(f"LLM did not give valid JSON after {retries} tries: {last_error}")


def ask_text(system, user, max_tokens=1000, retries=3):
    last_error = None
    for attempt in range(retries):
        try:
            return ask_llm(system, user, max_tokens=max_tokens)
        except Exception as e:
            last_error = e
            time.sleep(3 * (attempt + 1))
    raise RuntimeError(f"LLM call failed after {retries} tries: {last_error}")