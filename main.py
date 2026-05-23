"""Orchestrate the Coinbase Institutional Client Strategy Challenge workflow."""

from __future__ import annotations

from datetime import datetime, timezone

from agents.answer_generator import generate_all, word_count
from agents.coinbase_research_agent import research_coinbase_positioning
from agents.market_data_agent import run as run_market_data
from agents.qa_agent import qa_submission
from config import OUTPUT_DIR


def build_submission() -> str:
    snapshot, market_summary = run_market_data()
    research_coinbase_positioning()
    answers = generate_all(snapshot)

    sections = [
        "# Coinbase Institutional Client Strategy Challenge",
        "",
        f"_Generated: {datetime.now(timezone.utc).isoformat(timespec='seconds')} UTC_",
        "",
    ]
    for heading, answer in answers.items():
        sections.extend([f"## {heading}", "", answer.strip(), ""])

    body = "\n".join(sections).strip() + "\n"
    qa = qa_submission(body)

    disclosure = (
        "\n## AI Disclosure Draft\n\n"
        "I used AI tools to gather market context, structure drafts, and run quality checks. "
        "I reviewed and edited the final submission for accuracy, judgment, and tone.\n"
    )
    source_note = "\n## Market Data Source Note\n\n" + market_summary + "\n"
    qa_note = "\n" + qa.to_markdown()

    return body + disclosure + source_note + qa_note


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_DIR / "coinbase_challenge_submission.md"
    submission = build_submission()
    output_path.write_text(submission, encoding="utf-8")
    print(f"Wrote {output_path}")
    print(f"Main-answer word count: {word_count(submission.split('## AI Disclosure Draft')[0])}")


if __name__ == "__main__":
    main()
