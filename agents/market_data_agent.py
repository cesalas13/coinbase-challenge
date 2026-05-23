"""Fetch and persist market data for the Coinbase challenge submission."""

from __future__ import annotations

import json
import math
import sqlite3
import urllib.parse
import urllib.request
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import requests
except ImportError:  # The requirements file installs requests; urllib keeps smoke tests runnable.
    requests = None

from config import (
    COINBASE_BTC_TICKER_URL,
    DERIBIT_SUMMARY_URL,
    DERIBIT_VOL_URL,
    GLASSNODE_API_KEY,
    GLASSNODE_CME_OI_URL,
    MARKET_DB_PATH,
    YAHOO_CHART_URL,
)


@dataclass
class MarketSnapshot:
    timestamp_utc: str
    spot_price: float | None
    futures_symbol: str | None
    futures_price: float | None
    futures_expiry: str | None
    days_to_expiry: int | None
    basis_usd: float | None
    basis_pct: float | None
    annualized_basis_pct: float | None
    implied_vol_pct: float | None
    cme_open_interest: float | None
    perp_funding_rate_pct: float | None
    sources: dict[str, str]
    errors: list[str]


def _get_json(url: str, params: dict[str, Any] | None = None, timeout: int = 12) -> Any:
    headers = {"User-Agent": "coinbase-challenge-agent/1.0"}
    if requests is not None:
        response = requests.get(url, params=params, timeout=timeout, headers=headers)
        response.raise_for_status()
        return response.json()
    if params:
        url = f"{url}?{urllib.parse.urlencode(params)}"
    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def fetch_coinbase_spot() -> tuple[float | None, str | None]:
    data = _get_json(COINBASE_BTC_TICKER_URL)
    return float(data["price"]), COINBASE_BTC_TICKER_URL


def _parse_deribit_expiry(instrument_name: str) -> datetime | None:
    try:
        # Example: BTC-26JUN26
        expiry_token = instrument_name.split("-")[1]
        return datetime.strptime(expiry_token, "%d%b%y").replace(tzinfo=timezone.utc)
    except (IndexError, ValueError):
        return None


def fetch_deribit_future() -> tuple[str | None, float | None, str | None, int | None, str | None]:
    """Use a liquid quarterly Deribit BTC future as a CME-style futures basis proxy."""
    data = _get_json(DERIBIT_SUMMARY_URL, {"currency": "BTC", "kind": "future"})
    rows = data.get("result", [])
    now = datetime.now(timezone.utc)
    quarterly_months = {3, 6, 9, 12}
    quarterly_candidates: list[tuple[datetime, dict[str, Any]]] = []
    dated_candidates: list[tuple[datetime, dict[str, Any]]] = []
    for row in rows:
        name = row.get("instrument_name", "")
        if name.endswith("-PERPETUAL"):
            continue
        expiry = _parse_deribit_expiry(name)
        price = row.get("mid_price") or row.get("mark_price") or row.get("last")
        if not expiry or expiry <= now or not price:
            continue
        days = (expiry - now).total_seconds() / 86400
        if days < 20:
            continue
        dated_candidates.append((expiry, row))
        if expiry.month in quarterly_months:
            quarterly_candidates.append((expiry, row))
    candidates = quarterly_candidates or dated_candidates
    if not candidates:
        return None, None, None, None, None
    expiry, row = sorted(candidates, key=lambda item: item[0])[0]
    price = float(row.get("mid_price") or row.get("mark_price") or row.get("last"))
    days = max(1, math.ceil((expiry - now).total_seconds() / 86400))
    return row.get("instrument_name"), price, expiry.date().isoformat(), days, DERIBIT_SUMMARY_URL


def fetch_deribit_iv() -> tuple[float | None, str | None]:
    try:
        data = _get_json(DERIBIT_VOL_URL, {"currency": "BTC"})
        points = data.get("result", {}).get("data", [])
        if not points:
            return None, None
        latest = points[-1]
        value = latest[1] if isinstance(latest, list) and len(latest) > 1 else latest.get("value")
        return float(value), DERIBIT_VOL_URL
    except Exception:
        data = _get_json(DERIBIT_SUMMARY_URL, {"currency": "BTC", "kind": "option"})
        ivs = [float(row["mark_iv"]) for row in data.get("result", []) if row.get("mark_iv")]
        if not ivs:
            return None, None
        return sum(ivs) / len(ivs), DERIBIT_SUMMARY_URL


def fetch_cme_open_interest() -> tuple[float | None, str | None]:
    """Fetch CME BTC futures open interest using Glassnode if keyed, then Yahoo metadata."""
    if GLASSNODE_API_KEY:
        data = _get_json(
            GLASSNODE_CME_OI_URL,
            {"a": "BTC", "i": "24h", "api_key": GLASSNODE_API_KEY, "timestamp_format": "humanized"},
        )
        if data:
            latest = data[-1]
            value = latest.get("v")
            if value is not None:
                return float(value), GLASSNODE_CME_OI_URL

    url = YAHOO_CHART_URL.format(symbol="BTC=F")
    data = _get_json(url, {"range": "5d", "interval": "1d"})
    result = data.get("chart", {}).get("result", [{}])[0]
    quote = result.get("indicators", {}).get("quote", [{}])[0]
    open_interest = quote.get("openInterest") or quote.get("openinterest")
    if isinstance(open_interest, list):
        values = [value for value in open_interest if value is not None]
        if values:
            return float(values[-1]), url
    meta_oi = result.get("meta", {}).get("openInterest")
    return (float(meta_oi), url) if meta_oi else (None, url)


def fetch_perp_funding_rate() -> tuple[float | None, str | None]:
    data = _get_json(DERIBIT_SUMMARY_URL, {"currency": "BTC", "kind": "future"})
    for row in data.get("result", []):
        if row.get("instrument_name") == "BTC-PERPETUAL":
            rate = row.get("funding_8h") or row.get("current_funding")
            if rate is not None:
                return float(rate) * 100, DERIBIT_SUMMARY_URL

    url = "https://fapi.binance.com/fapi/v1/premiumIndex"
    data = _get_json(url, {"symbol": "BTCUSDT"})
    rate = data.get("lastFundingRate")
    return (float(rate) * 100, url) if rate is not None else (None, url)


def init_db(db_path: Path = MARKET_DB_PATH) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS market_snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp_utc TEXT NOT NULL,
                spot_price REAL,
                futures_symbol TEXT,
                futures_price REAL,
                futures_expiry TEXT,
                days_to_expiry INTEGER,
                basis_usd REAL,
                basis_pct REAL,
                annualized_basis_pct REAL,
                implied_vol_pct REAL,
                cme_open_interest REAL,
                perp_funding_rate_pct REAL,
                sources_json TEXT NOT NULL,
                errors_json TEXT NOT NULL
            )
            """
        )


def save_snapshot(snapshot: MarketSnapshot, db_path: Path = MARKET_DB_PATH) -> None:
    init_db(db_path)
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            """
            INSERT INTO market_snapshots (
                timestamp_utc, spot_price, futures_symbol, futures_price, futures_expiry,
                days_to_expiry, basis_usd, basis_pct, annualized_basis_pct, implied_vol_pct,
                cme_open_interest, perp_funding_rate_pct, sources_json, errors_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                snapshot.timestamp_utc,
                snapshot.spot_price,
                snapshot.futures_symbol,
                snapshot.futures_price,
                snapshot.futures_expiry,
                snapshot.days_to_expiry,
                snapshot.basis_usd,
                snapshot.basis_pct,
                snapshot.annualized_basis_pct,
                snapshot.implied_vol_pct,
                snapshot.cme_open_interest,
                snapshot.perp_funding_rate_pct,
                json.dumps(snapshot.sources, sort_keys=True),
                json.dumps(snapshot.errors),
            ),
        )


def latest_snapshot(db_path: Path = MARKET_DB_PATH) -> MarketSnapshot | None:
    if not db_path.exists():
        return None
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute("SELECT * FROM market_snapshots ORDER BY id DESC LIMIT 1").fetchone()
    if not row:
        return None
    return MarketSnapshot(
        timestamp_utc=row["timestamp_utc"],
        spot_price=row["spot_price"],
        futures_symbol=row["futures_symbol"],
        futures_price=row["futures_price"],
        futures_expiry=row["futures_expiry"],
        days_to_expiry=row["days_to_expiry"],
        basis_usd=row["basis_usd"],
        basis_pct=row["basis_pct"],
        annualized_basis_pct=row["annualized_basis_pct"],
        implied_vol_pct=row["implied_vol_pct"],
        cme_open_interest=row["cme_open_interest"],
        perp_funding_rate_pct=row["perp_funding_rate_pct"],
        sources=json.loads(row["sources_json"]),
        errors=json.loads(row["errors_json"]),
    )


def fetch_market_snapshot() -> MarketSnapshot:
    errors: list[str] = []
    sources: dict[str, str] = {}
    spot_price = futures_price = implied_vol_pct = cme_open_interest = perp_funding_rate_pct = None
    futures_symbol = futures_expiry = None
    days_to_expiry = None

    try:
        spot_price, source = fetch_coinbase_spot()
        if source:
            sources["spot"] = source
    except Exception as exc:
        errors.append(f"Coinbase spot unavailable: {exc}")

    try:
        futures_symbol, futures_price, futures_expiry, days_to_expiry, source = fetch_deribit_future()
        if source:
            sources["futures_proxy"] = source
    except Exception as exc:
        errors.append(f"Futures proxy unavailable: {exc}")

    try:
        implied_vol_pct, source = fetch_deribit_iv()
        if source:
            sources["implied_volatility"] = source
    except Exception as exc:
        errors.append(f"BTC implied volatility unavailable: {exc}")

    try:
        cme_open_interest, source = fetch_cme_open_interest()
        if source:
            sources["cme_open_interest"] = source
    except Exception as exc:
        errors.append(f"CME open interest unavailable: {exc}")

    try:
        perp_funding_rate_pct, source = fetch_perp_funding_rate()
        if source:
            sources["perp_funding"] = source
    except Exception as exc:
        errors.append(f"Perp funding unavailable: {exc}")

    basis_usd = basis_pct = annualized_basis_pct = None
    if spot_price and futures_price:
        basis_usd = futures_price - spot_price
        basis_pct = basis_usd / spot_price * 100
        if days_to_expiry:
            annualized_basis_pct = basis_pct * 365 / days_to_expiry

    return MarketSnapshot(
        timestamp_utc=datetime.now(timezone.utc).isoformat(timespec="seconds"),
        spot_price=spot_price,
        futures_symbol=futures_symbol,
        futures_price=futures_price,
        futures_expiry=futures_expiry,
        days_to_expiry=days_to_expiry,
        basis_usd=basis_usd,
        basis_pct=basis_pct,
        annualized_basis_pct=annualized_basis_pct,
        implied_vol_pct=implied_vol_pct,
        cme_open_interest=cme_open_interest,
        perp_funding_rate_pct=perp_funding_rate_pct,
        sources=sources,
        errors=errors,
    )


def format_market_summary(snapshot: MarketSnapshot) -> str:
    def money(value: float | None) -> str:
        return "unavailable" if value is None else f"${value:,.0f}"

    def pct(value: float | None) -> str:
        return "unavailable" if value is None else f"{value:.2f}%"

    lines = [
        f"- BTC spot ({snapshot.timestamp_utc} UTC): {money(snapshot.spot_price)}.",
        f"- Futures proxy ({snapshot.futures_symbol or 'unavailable'}, expiry {snapshot.futures_expiry or 'n/a'}): {money(snapshot.futures_price)}.",
        f"- Basis: {money(snapshot.basis_usd)} / {pct(snapshot.basis_pct)} spot, annualized {pct(snapshot.annualized_basis_pct)}.",
        f"- BTC implied volatility: {pct(snapshot.implied_vol_pct)}.",
        f"- CME BTC futures open interest: {snapshot.cme_open_interest:,.0f} contracts." if snapshot.cme_open_interest else "- CME BTC futures open interest: unavailable.",
        f"- BTC perpetual funding: {pct(snapshot.perp_funding_rate_pct)} per funding interval.",
    ]
    if snapshot.errors:
        lines.append("- Data caveats: " + "; ".join(snapshot.errors))
    return "\n".join(lines)


def run() -> tuple[MarketSnapshot, str]:
    snapshot = fetch_market_snapshot()
    save_snapshot(snapshot)
    return snapshot, format_market_summary(snapshot)


if __name__ == "__main__":
    market_snapshot, summary = run()
    print(summary)
    print(json.dumps(asdict(market_snapshot), indent=2))
