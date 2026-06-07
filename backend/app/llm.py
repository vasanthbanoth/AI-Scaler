from __future__ import annotations

import os

from openai import OpenAI

from app.config import get_settings
from app.prompts import SYSTEM_PROMPT


def _openai_client(key: str) -> OpenAI:
    return OpenAI(api_key=key)


def _groq_client(key: str) -> OpenAI:
    return OpenAI(api_key=key, base_url="https://api.groq.com/openai/v1")


def chat_completion(context: str, user_message: str) -> str:
    s = get_settings()
    user_content = f"CONTEXT:\n{context}\n\nUSER:\n{user_message}"
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_content},
    ]

    attempts: list[tuple[OpenAI, str, str]] = []
    if s.openai_api_key and s.openai_api_key.startswith("sk-"):
        attempts.append((_openai_client(s.openai_api_key), s.chat_model, "openai"))
    if s.groq_api_key:
        attempts.append(
            (_groq_client(s.groq_api_key), os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"), "groq")
        )

    if not attempts:
        raise ValueError("No LLM configured — set OPENAI_API_KEY or GROQ_API_KEY")

    last_err: Exception | None = None
    for client, model, label in attempts:
        try:
            completion = client.chat.completions.create(
                model=model,
                temperature=0.2,
                messages=messages,
            )
            return completion.choices[0].message.content or ""
        except Exception as e:
            last_err = e
            err = str(e).lower()
            if "quota" in err or "429" in err or "insufficient" in err:
                continue
            raise

    raise last_err or ValueError("All LLM providers failed")
