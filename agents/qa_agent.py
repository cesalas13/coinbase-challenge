"""QA scorer for the Coinbase challenge submission."""

from __future__ import annotations

import re
from dataclasses import dataclass

from config import MAX_WORDS_TOTAL


CRITERIA = [
    "Commercial Judgement",
    "Client Intuition",
    "Prioritization",
    "Questioning Ability",
    "Market Awareness",
    "Structured Thinking",
]

SALESY_TERMS = [
    "best-in-class",
    "trusted partner",
    "seamless",
    "unparalleled",
    "world-class",
    "revolutionary",
    "game changer",
]

VAGUE_TERMS = [
    "robust",
    "comprehensive",
    "innovative",
    "synergy",
    "leverage our platform",
    "value-added",
]


@dataclass
class QAResult:
    word_count: int
    scores: dict[str, int]
    flags: list[str]
    suggestions: list[str]

    def to_markdown(self) -> str:
        lines = [f"# QA Report", "", f"Word count: {self.word_count} / {MAX_WORDS_TOTAL}", "", "## Scores"]
        lines.extend(f"- {name}: {score}/10" for name, score in self.scores.items())
        lines.extend(["", "## Flags"])
        lines.extend(f"- {flag}" for flag in self.flags) if self.flags else lines.append("- None")
        lines.extend(["", "## Suggestions"])
        lines.extend(f"- {suggestion}" for suggestion in self.suggestions) if self.suggestions else lines.append("- No major changes suggested.")
        return "\n".join(lines) + "\n"


def count_words(text: str) -> int:
    main_text = re.sub(r"^#.*$", "", text, flags=re.MULTILINE)
    main_text = re.sub(r"AI Disclosure.*", "", main_text, flags=re.IGNORECASE | re.DOTALL)
    return len(re.findall(r"\b[\w$%.-]+\b", main_text))


def _contains_any(text: str, terms: list[str]) -> list[str]:
    lower = text.lower()
    return [term for term in terms if term in lower]


def qa_submission(text: str) -> QAResult:
    lower = text.lower()
    wc = count_words(text)
    flags: list[str] = []
    suggestions: list[str] = []

    scores = {criterion: 8 for criterion in CRITERIA}

    if wc >= MAX_WORDS_TOTAL:
        flags.append(f"Submission exceeds {MAX_WORDS_TOTAL} words.")
        suggestions.append("Cut setup language and repeated Coinbase positioning until the answer is below the word cap.")
        for criterion in scores:
            scores[criterion] -= 1
    elif wc > 930:
        flags.append("Submission is close to the total word cap.")
        suggestions.append("Keep a 50-70 word buffer for formatting differences in Google Docs.")

    salesy = _contains_any(text, SALESY_TERMS)
    if salesy:
        flags.append("Sales pitch language detected: " + ", ".join(salesy))
        suggestions.append("Replace sales phrasing with concrete operational or economic tradeoffs.")
        scores["Commercial Judgement"] -= 1
        scores["Client Intuition"] -= 1

    vague = _contains_any(text, VAGUE_TERMS)
    if vague:
        flags.append("Vague claims detected: " + ", ".join(vague))
        suggestions.append("Swap vague adjectives for data, constraints, or decision criteria.")
        scores["Structured Thinking"] -= 1

    if "ibit" not in lower or "cme" not in lower:
        flags.append("IBIT+CME comparison is missing or too light.")
        suggestions.append("Add why ETF/listed futures rails may be better for constrained mandates.")
        scores["Commercial Judgement"] -= 2

    if "margin" not in lower or "financing" not in lower:
        flags.append("Margin or financing economics are underdeveloped.")
        suggestions.append("Explicitly connect basis return to financing and variation-margin liquidity.")
        scores["Market Awareness"] -= 1

    if "unavailable" in lower:
        flags.append("One or more market data fields are unavailable.")
        suggestions.append("Refresh the market data agent or manually verify CME OI/funding before final submission.")

    if "$500m" not in lower and "$500M" not in text and "sovereign" not in lower:
        flags.append("Prioritization scenario lacks the sovereign-fund anchor.")
        suggestions.append("Name the $500M sovereign as the strategic priority and explain why.")
        scores["Prioritization"] -= 2

    question_marks = text.count("?")
    if question_marks < 4:
        flags.append("Discovery section has fewer than five clear questions.")
        suggestions.append("Use five direct questions and attach a short rationale to each.")
        scores["Questioning Ability"] -= 2

    market_numbers = len(re.findall(r"[$]?\d+(?:,\d{3})*(?:\.\d+)?%?", text))
    if market_numbers < 8:
        flags.append("Market context may not be specific enough.")
        suggestions.append("Include spot, futures/basis, annualized basis, IV, and OI or a clear data caveat.")
        scores["Market Awareness"] -= 1

    if not re.search(r"Exercise\s+1", text, re.IGNORECASE):
        flags.append("Exercise headings are missing.")
        suggestions.append("Use clear exercise headings for readability in the Google Doc.")
        scores["Structured Thinking"] -= 1

    scores = {criterion: max(1, min(10, score)) for criterion, score in scores.items()}
    return QAResult(word_count=wc, scores=scores, flags=flags, suggestions=suggestions)


if __name__ == "__main__":
    import sys

    submission = sys.stdin.read()
    print(qa_submission(submission).to_markdown())
