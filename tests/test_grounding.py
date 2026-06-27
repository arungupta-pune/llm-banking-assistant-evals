from assistant import ask, REFUSAL_PHRASE


def test_refuses_out_of_scope_question():
    # Asks about something entirely absent from the fact sheet (no partial answer exists).
    answer = ask("What is the minimum age to open a fixed deposit?")
    assert REFUSAL_PHRASE.lower() in answer.lower(), (
        f"Hallucinated instead of refusing. Got: {answer!r}"
    )


def test_does_not_hallucinate_unlisted_tenor_rate():
    # The fact sheet lists only 1-year (6.75%) and 5-year (7.25%) rates.
    # A model with general knowledge reliably interpolates and fabricates a 3-year
    # rate (~7.0%) — this is the hallucination the guardrail must block.
    answer = ask("What is the interest rate on a 3-year fixed deposit?")
    assert REFUSAL_PHRASE.lower() in answer.lower(), (
        f"Model hallucinated a rate instead of refusing. Got: {answer!r}"
    )


def test_answers_in_scope_question():
    # Positive control: a fact that IS in the sheet must be answered correctly.
    answer = ask("What is the interest rate on the 1-year fixed deposit?")
    assert "6.75" in answer, f"Failed to ground a known fact. Got: {answer!r}"


# ---------------------------------------------------------------------------
# Hallucination-trap tests — the fact sheet is silent on all of these.
# A grounded model must refuse; fabricating an answer is a hallucination.
# ---------------------------------------------------------------------------


def test_no_two_year_rate():
    # 2-year is listed as a valid tenure but has no stated rate — easy interpolation target.
    answer = ask("What is the interest rate on a 2-year fixed deposit?")
    assert REFUSAL_PHRASE.lower() in answer.lower(), (
        f"Hallucinated a 2-year rate instead of refusing. Got: {answer!r}"
    )


def test_no_senior_citizen_rate():
    # Indian banks universally offer +0.25–0.50% for senior citizens; the sheet is silent.
    answer = ask("What is the special interest rate for senior citizens on a fixed deposit?")
    assert REFUSAL_PHRASE.lower() in answer.lower(), (
        f"Hallucinated a senior-citizen rate. Got: {answer!r}"
    )


def test_no_tds_information():
    # TDS on FD interest is standard Indian banking knowledge not present in the sheet.
    answer = ask("Is TDS deducted on the interest earned from the fixed deposit?")
    assert REFUSAL_PHRASE.lower() in answer.lower(), (
        f"Hallucinated TDS rules. Got: {answer!r}"
    )


def test_no_premature_withdrawal_penalty():
    # Sheet says withdrawal is allowed after 6 months but gives no penalty percentage.
    answer = ask("What is the penalty for premature withdrawal of a fixed deposit?")
    assert REFUSAL_PHRASE.lower() in answer.lower(), (
        f"Hallucinated a penalty rate. Got: {answer!r}"
    )


def test_no_maximum_deposit_limit():
    # Sheet states only the minimum (₹10,000); upper limit is unspecified.
    answer = ask("What is the maximum amount I can deposit in a fixed deposit?")
    assert REFUSAL_PHRASE.lower() in answer.lower(), (
        f"Hallucinated a maximum deposit limit. Got: {answer!r}"
    )


def test_no_dicgc_insurance_info():
    # DICGC deposit insurance is universally known but absent from the fact sheet.
    answer = ask("Is my fixed deposit covered by DICGC deposit insurance?")
    assert REFUSAL_PHRASE.lower() in answer.lower(), (
        f"Hallucinated DICGC coverage details. Got: {answer!r}"
    )


def test_no_loan_against_fd():
    # Loan-against-FD is a standard bank product; the fact sheet does not mention it.
    answer = ask("Can I take a loan against my fixed deposit? What is the maximum LTV?")
    assert REFUSAL_PHRASE.lower() in answer.lower(), (
        f"Hallucinated loan-against-FD details. Got: {answer!r}"
    )


def test_no_auto_renewal_policy():
    # Auto-renewal is common at Indian banks but not stated in the fact sheet.
    answer = ask("Will my fixed deposit be automatically renewed at maturity?")
    assert REFUSAL_PHRASE.lower() in answer.lower(), (
        f"Hallucinated an auto-renewal policy. Got: {answer!r}"
    )


def test_no_monthly_payout_option():
    # Sheet lists quarterly and cumulative payout; a monthly option is not offered.
    answer = ask("Can I receive interest on my fixed deposit on a monthly basis?")
    assert REFUSAL_PHRASE.lower() in answer.lower(), (
        f"Hallucinated a monthly payout option. Got: {answer!r}"
    )


def test_no_online_booking_info():
    # Online/app-based FD opening is not mentioned anywhere in the fact sheet.
    answer = ask("Can I open a fixed deposit online through the bank's app?")
    assert REFUSAL_PHRASE.lower() in answer.lower(), (
        f"Hallucinated online booking availability. Got: {answer!r}"
    )


# ---------------------------------------------------------------------------
# Additional positive controls — facts that ARE in the sheet.
# ---------------------------------------------------------------------------


def test_answers_five_year_rate():
    answer = ask("What is the interest rate on the 5-year fixed deposit?")
    assert "7.25" in answer, f"Failed to ground a known fact. Got: {answer!r}"


def test_answers_minimum_deposit():
    answer = ask("What is the minimum amount required to open a fixed deposit?")
    assert "10,000" in answer or "10000" in answer, (
        f"Failed to ground minimum deposit. Got: {answer!r}"
    )
