import os
from pathlib import Path
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

client = genai.Client()

SYSTEM_PROMPT = """You are a customer-support assistant for a retail bank.
Answer the customer's question USING ONLY the product fact sheet below.
If the answer is not in the fact sheet, reply with EXACTLY this sentence and nothing else:
"I don't have that information. Please contact the bank directly."
Never guess, estimate, or use any outside knowledge.

PRODUCT FACT SHEET:
{fact_sheet}"""

def load_fact_sheet(path: str = "fact_sheets/fixed_deposit.md") -> str:
    return Path(path).read_text(encoding="utf-8")

def ask(question: str, fact_sheet: str | None = None) -> str:
    if fact_sheet is None:
        fact_sheet = load_fact_sheet()
        
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=question,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT.format(fact_sheet=fact_sheet),
            max_output_tokens=300,
            temperature=0.0  
        )
    )
    
    return response.text.strip()

if __name__ == "__main__":
    for q in [
        "What is the interest rate on the 1-year fixed deposit?",
        "What is the penalty percentage for premature withdrawal?",
    ]:
        print(f"\nQ: {q}\nA: {ask(q)}")