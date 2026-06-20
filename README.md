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
Python · Anthropic API · pytest

## Run it
```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env        # then paste your ANTHROPIC_API_KEY
python assistant.py         # see it answer a known fact and refuse an unknown one
pytest -v                   # run the guardrail suite
```

