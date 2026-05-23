"""Claude-backed Coinbase Prime research agent with an offline fallback."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from config import ANTHROPIC_API_KEY, ANTHROPIC_MODEL, RESEARCH_DIR


PROMPT = """Research Coinbase Institutional and Coinbase Prime positioning from the last six months.

Search the web for recent Coinbase Prime blog posts, product pages, institutional updates, and client/case-study style materials. Extract:
- Key differentiators
- Agency-only positioning
- Integrated platform messaging
- Recent product launches or platform expansions
- Institutional client proof points or case studies

Write a concise markdown positioning memo for a Coinbase Institutional Client Strategy Challenge answer. Be factual, cite source URLs inline where possible, and separate confirmed facts from inferred positioning.
"""


FALLBACK_POSITIONING = """# Coinbase Institutional Positioning

Generated without live Claude web research. Verify before final submission.

## Key Differentiators

- Coinbase Prime should be positioned as an integrated institutional platform rather than a single execution venue: trading, custody, financing, governance controls, reporting, and broader digital-asset access belong in one operating workflow.
- The commercial angle for a basis-trade client is operational efficiency and future readiness, not simply "Coinbase is cheaper." The right comparison is net return after execution, custody, margin, financing, legal review, and reporting friction.
- Coinbase's strongest pitch versus an ETF+CME implementation is direct BTC ownership and reusable digital-asset infrastructure. The ETF+CME route may still win for clients constrained to listed securities.

## Agency-Only Message

- Use agency-style language: Coinbase acts as an execution and infrastructure partner aligned with client outcomes, not a principal taking the other side of the client's trade.
- Avoid overstating. If the answer references agency-only positioning, verify current public wording before submission.

## Integrated Platform Message

- Integrated custody, trading, financing/collateral workflows, and reporting reduce the number of operational handoffs in a cash-and-carry trade.
- Cross-margin or collateral efficiency is a potential advantage only where available for the client's instruments and legal setup.

## Recent Research To Verify

- Coinbase Prime product updates from Coinbase Institutional blog.
- Coinbase Derivatives and institutional futures access updates.
- Any 2025-2026 announcements around financing, custody, international exchange, or Prime integrations.
- Institutional client references involving asset managers, hedge funds, corporates, ETFs, or sovereign-style allocators.
"""


def _anthropic_client():
    if not ANTHROPIC_API_KEY:
        return None
    try:
        from anthropic import Anthropic
    except ImportError:
        return None
    return Anthropic(api_key=ANTHROPIC_API_KEY)


def research_coinbase_positioning(output_path: Path | None = None) -> str:
    RESEARCH_DIR.mkdir(parents=True, exist_ok=True)
    output_path = output_path or RESEARCH_DIR / "coinbase_positioning.md"
    client = _anthropic_client()

    if client is None:
        memo = FALLBACK_POSITIONING
    else:
        response = client.messages.create(
            model=ANTHROPIC_MODEL,
            max_tokens=3500,
            temperature=0.2,
            tools=[{"type": "web_search_20250305", "name": "web_search", "max_uses": 8}],
            messages=[{"role": "user", "content": PROMPT}],
        )
        memo = "\n".join(block.text for block in response.content if getattr(block, "type", None) == "text")

    header = f"<!-- Generated {datetime.now(timezone.utc).isoformat(timespec='seconds')} UTC -->\n\n"
    output_path.write_text(header + memo.strip() + "\n", encoding="utf-8")
    return output_path.read_text(encoding="utf-8")


if __name__ == "__main__":
    print(research_coinbase_positioning())
