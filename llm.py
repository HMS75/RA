"""The ONLY file that talks to the LLM."""

import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

MODEL = os.getenv("LLM_MODEL", "gemini-3.5-flash")

_client = None

def ask_llm(system, user, max_tokens=2500):
    """Send one question to the LLM and return plain text."""

    global _client

    if _client is None:
        _client = genai.Client(
            api_key=os.getenv("GOOGLE_API_KEY")
        )

    response = _client.models.generate_content(
        model=MODEL,
        contents=user,
        config=types.GenerateContentConfig(
            system_instruction=system,
            max_output_tokens=max_tokens,
        ),
    )

    return response.text