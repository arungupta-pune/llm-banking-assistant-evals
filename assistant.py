from __future__ import annotations

import functools
import os
import time
from collections import deque
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

GEMINI_RPM: int = int(os.getenv("GEMINI_RPM", "6"))
GEMINI_RPM_BUFFER_SECS: float = float(os.getenv("GEMINI_RPM_BUFFER_SECS", "2.0"))

_request_times: deque[float] = deque()

REFUSAL_PHRASE = "I don't have that information. Please contact the bank directly."

SYSTEM_PROMPT = f"""You are a customer-support assistant for a retail bank.
Answer the customer's question USING ONLY the product fact sheet below.
If the answer is not in the fact sheet, reply with EXACTLY this sentence and nothing else:
"{REFUSAL_PHRASE}"
Never guess, estimate, or use any outside knowledge.

PRODUCT FACT SHEET:
{{fact_sheet}}"""

_DEFAULT_SHEET = str(Path(__file__).parent / "fact_sheets" / "fixed_deposit.md")

_client: genai.Client | None = None


def _rate_limit() -> None:
    window = 60.0
    now = time.monotonic()
    while _request_times and now - _request_times[0] >= window:
        _request_times.popleft()
    if len(_request_times) >= GEMINI_RPM:
        # Sleep until the oldest request falls outside the window, plus a buffer
        # to guard against server-side clock skew and window-boundary edge cases.
        sleep_for = window - (now - _request_times[0]) + GEMINI_RPM_BUFFER_SECS
        time.sleep(max(sleep_for, 0))
        now = time.monotonic()
        while _request_times and now - _request_times[0] >= window:
            _request_times.popleft()


def _get_client() -> genai.Client:
    global _client
    if _client is None:
        _client = genai.Client()
    return _client


@functools.lru_cache(maxsize=None)
def load_fact_sheet(path: str = _DEFAULT_SHEET) -> str:
    return Path(path).read_text(encoding="utf-8")


def ask(question: str, fact_sheet: str | None = None) -> str:
    if fact_sheet is None:
        fact_sheet = load_fact_sheet()

    _rate_limit()
    response = _get_client().models.generate_content(
        model="gemini-2.5-flash",
        contents=question,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT.format(fact_sheet=fact_sheet),
            max_output_tokens=300,
        ),
    )
    _request_times.append(time.monotonic())

    if response.text is None:
        raise RuntimeError(
            f"Model returned no text (finish_reason={response.candidates[0].finish_reason if response.candidates else 'unknown'})"
        )
    return response.text.strip()


if __name__ == "__main__":
    for q in [
        "What is the interest rate on the 1-year fixed deposit?",
        "What is the minimum age to open a fixed deposit?",
    ]:
        print(f"\nQ: {q}\nA: {ask(q)}")
