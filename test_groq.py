import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise RuntimeError("Set GROQ_API_KEY first.")

client = Groq(api_key=api_key)

try:
    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {
                "role": "system",
                "content": "You are a helpful research assistant."
            },
            {
                "role": "user",
                "content": "Explain RAG in exactly three bullet points."
            }
        ],
        max_completion_tokens=300,
        reasoning_effort="low",
    )

    print("MODEL:", response.model)
    print("RESPONSE:")
    print(response.choices[0].message.content)
    print("\nUSAGE:", response.usage)

except Exception as e:
    print(f"API test failed: {type(e).__name__}: {e}")