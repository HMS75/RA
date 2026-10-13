"""The ONLY file that talks to the LLM."""

import os

from dotenv import load_dotenv
from groq import Groq

load_dotenv()

MODEL = os.getenv("LLM_MODEL", "openai/gpt-oss-20b")

_client = None


def ask_llm(system, user, max_tokens=2500):
    """Send one question to the LLM and return plain text."""

    global _client

    if _client is None:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise RuntimeError("GROQ_API_KEY is not set. Add your Groq API key to .env.")
        _client = Groq(api_key=api_key)

    response = _client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        max_completion_tokens=max_tokens,
    )

    content = response.choices[0].message.content
    if content is None:
        raise RuntimeError("Groq returned an empty response.")
    return content