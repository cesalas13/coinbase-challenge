"""Generate challenge exercise answers using the local skill and market data."""

from __future__ import annotations

import re
from pathlib import Path

from agents.market_data_agent import MarketSnapshot, format_market_summary, latest_snapshot
from config import ANTHROPIC_API_KEY, ANTHROPIC_MODEL, RESEARCH_DIR, SKILL_PATH


def word_count(text: str) -> int:
    return len(re.findall(r"\b[\w$%.-]+\b", text))


def load_skill() -> str:
    return SKILL_PATH.read_text(encoding="utf-8")


def load_positioning() -> str:
    path = RESEARCH_DIR / "coinbase_positioning.md"
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _anthropic_client():
    if not ANTHROPIC_API_KEY:
        return None
    try:
        from anthropic import Anthropic
    except ImportError:
        return None
    return Anthropic(api_key=ANTHROPIC_API_KEY)


def _claude_generate(task: str, max_words: int, extra_context: str = "") -> str | None:
    client = _anthropic_client()
    if client is None:
        return None
    prompt = f"""Use the skill and context below to answer the Coinbase Institutional Client Strategy Challenge task.

Hard limit: {max_words} words. Be commercially direct, specific, and candid. Do not include a heading unless requested.

SKILL:
{load_skill()}

CONTEXT:
{extra_context}

TASK:
{task}
"""
    response = client.messages.create(
        model=ANTHROPIC_MODEL,
        max_tokens=1200,
        temperature=0.35,
        messages=[{"role": "user", "content": prompt}],
    )
    return "\n".join(block.text for block in response.content if getattr(block, "type", None) == "text").strip()


def _trim_to_words(text: str, max_words: int) -> str:
    words = re.findall(r"\S+", text)
    return text if len(words) <= max_words else " ".join(words[:max_words]).rstrip(" ,;:") + "."


_FALLBACK_NOTICE = (
    "FALLBACK PLACEHOLDER. The Anthropic SDK was unavailable when this ran. "
    "Replace with your own analysis or rerun with ANTHROPIC_API_KEY set. "
    "This stub exists so the pipeline still produces a populated draft for "
    "downstream QA testing."
)


def generate_exercise_1() -> str:
    generated = _claude_generate(
        "Exercise 1: Decision framework for a large cash-and-carry via Coinbase Prime versus an ETF-plus-CME-futures implementation. Use the SKILL framework. Structure: Coinbase advantages, Coinbase disadvantages, conversation positioning.",
        350,
        load_positioning(),
    )
    if generated:
        return _trim_to_words(generated, 350)
    return _FALLBACK_NOTICE


def generate_exercise_2() -> str:
    generated = _claude_generate(
        "Exercise 2: Prioritize the four client demands listed in the challenge brief (see SKILL.md). Use deal size times probability, strategic vs tactical, time sensitivity, and delegation. Show reasoning.",
        250,
        load_positioning(),
    )
    if generated:
        return _trim_to_words(generated, 250)
    return _FALLBACK_NOTICE


def generate_exercise_3() -> str:
    generated = _claude_generate(
        "Exercise 3: Five discovery questions, each with brief rationale. Focus on strategic intent, constraints, sizing, infrastructure, and market view.",
        150,
        load_positioning(),
    )
    if generated:
        return _trim_to_words(generated, 150)
    return _FALLBACK_NOTICE


def generate_exercise_4(snapshot: MarketSnapshot | None = None) -> str:
    snapshot = snapshot or latest_snapshot()
    context = format_market_summary(snapshot) if snapshot else "No market snapshot available."
    generated = _claude_generate(
        "Exercise 4: Market context in 3-5 bullets. Use format '[Data point]: [Implication for basis trade]'.",
        250,
        context,
    )
    if generated:
        return _trim_to_words(generated, 250)
    if not snapshot:
        return "- Current market data unavailable: rerun market_data_agent before final submission."

    def money(value: float | None) -> str:
        return "unavailable" if value is None else f"${value:,.0f}"

    def pct(value: float | None) -> str:
        return "unavailable" if value is None else f"{value:.2f}%"

    if snapshot.perp_funding_rate_pct is None:
        funding_line = "- Perp funding unavailable: verify leveraged-demand signals before relying on basis persistence."
    elif snapshot.perp_funding_rate_pct > 0.005:
        funding_line = f"- Perp funding at {pct(snapshot.perp_funding_rate_pct)}: positive funding supports leveraged long demand, but a flip lower would warn that basis can compress quickly."
    elif snapshot.perp_funding_rate_pct < -0.005:
        funding_line = f"- Perp funding at {pct(snapshot.perp_funding_rate_pct)}: negative funding weakens the carry backdrop and argues for a higher net-return hurdle."
    else:
        funding_line = f"- Perp funding near flat at {pct(snapshot.perp_funding_rate_pct)}: leverage demand is not paying much carry, so the listed-futures basis must stand on its own economics."

    bullets = [
        f"- BTC spot at {money(snapshot.spot_price)}: sizing a $100M leg means execution quality and slippage control matter as much as headline fees.",
        f"- {snapshot.futures_symbol or 'BTC future'} at {money(snapshot.futures_price)} versus spot: current basis is {money(snapshot.basis_usd)} ({pct(snapshot.annualized_basis_pct)} annualized), so the trade should be judged after financing, custody, ETF costs, and margin drag.",
        f"- BTC implied volatility at {pct(snapshot.implied_vol_pct)}: higher volatility raises variation-margin and liquidity-buffer requirements for the short futures leg.",
        f"- CME BTC futures open interest at {snapshot.cme_open_interest:,.0f} contracts: institutional liquidity appears usable, but crowded positioning should be stress-tested." if snapshot.cme_open_interest else "- CME BTC futures open interest unavailable: verify institutional depth before finalizing execution assumptions.",
        funding_line,
    ]
    return _trim_to_words("\n".join(bullets), 250)


def generate_all(snapshot: MarketSnapshot | None = None) -> dict[str, str]:
    return {
        "Exercise 1": generate_exercise_1(),
        "Exercise 2": generate_exercise_2(),
        "Exercise 3": generate_exercise_3(),
        "Exercise 4": generate_exercise_4(snapshot),
    }
