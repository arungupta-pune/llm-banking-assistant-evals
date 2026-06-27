# LLM Banking Assistant — Evaluation Harness

A test harness that puts guardrails around an LLM-powered retail-banking Q&A
assistant. The assistant answers customer questions **strictly from a product
fact sheet**, and the eval suite proves it **refuses what it doesn't know instead
of hallucinating** — the failure mode that makes generative AI risky in regulated
finance.

## Why this exists
A wrong interest rate or an invented withdrawal penalty isn't a bug — it's a
compliance incident. This repo treats quality as *objectives the AI must satisfy*,
checked automatically on every change:

- **Grounding / no hallucination** (OWASP LLM02): out-of-scope questions get a
  refusal, not a guess.
- *Coming next:* prompt-injection resistance (OWASP LLM01), PII-leak checks,
  more probabilistic assertions, CI on every push.

## Stack
Python 3.10+ · Gemini API · pytest

## Run it
```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
export GOOGLE_API_KEY=your_key_here                 # Windows: set GOOGLE_API_KEY=your_key_here
python assistant.py         # see it answer a known fact and refuse an unknown one
pytest -v                   # run the guardrail suite
```

## Design notes

- The refusal phrase (`REFUSAL_PHRASE`) is defined once in `assistant.py` and
  shared with the test suite — a wording change in the system prompt is
  automatically reflected in test assertions.
- `load_fact_sheet` is cached (`lru_cache`) so the file is read only once per
  process regardless of how many `ask()` calls are made.
- The Gemini client is instantiated lazily on the first `ask()` call, so
  importing `assistant` is always safe even without credentials set.
