"""Configuration for the Coinbase challenge agents."""

from __future__ import annotations

import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
RESEARCH_DIR = BASE_DIR / "research"
OUTPUT_DIR = BASE_DIR / "output"
SKILL_PATH = BASE_DIR / "skills" / "coinbase-basis-challenge" / "SKILL.md"

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-20250514")
GLASSNODE_API_KEY = os.getenv("GLASSNODE_API_KEY", "")

MARKET_DB_PATH = DATA_DIR / "market_data.db"

COINBASE_BTC_TICKER_URL = "https://api.exchange.coinbase.com/products/BTC-USD/ticker"
DERIBIT_SUMMARY_URL = "https://www.deribit.com/api/v2/public/get_book_summary_by_currency"
DERIBIT_VOL_URL = "https://www.deribit.com/api/v2/public/get_volatility_index_data"
YAHOO_CHART_URL = "https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
GLASSNODE_CME_OI_URL = "https://api.glassnode.com/v1/metrics/derivatives/futures_cme_open_interest_sum"

CHALLENGE_DUE = "2026-06-01 23:59 PST"
MAX_WORDS_TOTAL = 1000
