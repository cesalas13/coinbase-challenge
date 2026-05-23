# Coinbase Institutional Client Strategy Challenge: Agent Pipeline

A small multi-agent pipeline that produces a draft submission for the Coinbase Institutional Client Strategy Challenge, end to end:

```
market-data agent  →  research agent  →  answer generator  →  QA agent  →  draft submission
       ↓                    ↓                   ↓                ↓
   BTC spot / futures /  Coinbase Prime    answers under     scores 1-10
   basis / IV / perp     positioning       hard word caps    on grading
   funding snapshot      memo with         (350 / 250 /      criteria,
   (sqlite-persisted)    cited sources     150 / 250)        flags edits
```

Each agent is a separate Python module with a single responsibility. The output is a Google-Doc-ready markdown draft with an AI disclosure footer and a market data source note. The pipeline is meant to be human-in-the-loop: the agents drive the boring infrastructure (snapshotting, drafting, scoring, formatting) so the operator's time goes to judgment and editing.

## Why this exists

The challenge is a structured commercial-judgment exercise: four exercises on Bitcoin basis-trade strategy, Coinbase Prime positioning, and institutional client prioritization. The deliverable is a tight written submission under a 1,000-word total cap.

Doing this without infrastructure looks like: tab through ten broker reports, copy-paste rates from three exchanges, write four answers by hand, count words manually, edit five times. Doing it with agents looks like: one `python3 main.py`, get a snapshot + draft + QA report, then spend the rest of the time on the edits that actually move the score.

## Architecture

```
coinbase-challenge/
├── agents/
│   ├── market_data_agent.py        ← pulls BTC spot, futures basis, IV, OI, funding
│   ├── coinbase_research_agent.py  ← Anthropic SDK + web search → positioning memo
│   ├── answer_generator.py         ← four answers under hard word caps
│   └── qa_agent.py                 ← scores draft 1-10 across six grading axes
├── research/
│   └── coinbase_positioning.md     ← Prime positioning notes (cited sources)
├── skills/
│   └── coinbase-basis-challenge/
│       └── SKILL.md                ← the Claude skill that scopes the work
├── data/                           ← runtime sqlite snapshots (gitignored)
├── output/                         ← generated drafts (gitignored)
├── examples/                       ← redacted example outputs
├── main.py                         ← orchestrator
├── config.py
├── requirements.txt
└── .env.example
```

## How the agents coordinate

| Agent | Owns | Output |
|---|---|---|
| `market_data_agent` | BTC spot, futures basis, implied vol, CME open interest, perp funding | sqlite snapshot + bullet summary |
| `coinbase_research_agent` | Coinbase Prime positioning research using Claude web search | markdown memo with citations |
| `answer_generator` | Four exercise answers, each under its word cap | markdown sections |
| `qa_agent` | Word counts, scores against six grading criteria, flags edits | QA report appended to draft |

The orchestrator runs them in order, then assembles the final submission with an AI disclosure footer.

## Setup

```bash
git clone https://github.com/cesalas13/coinbase-challenge.git
cd coinbase-challenge
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Add your Anthropic key to `.env`:

```bash
export ANTHROPIC_API_KEY=sk-ant-...
export ANTHROPIC_MODEL=claude-sonnet-4-20250514
```

`sqlite3` is part of the Python standard library and does not need to be installed through pip.

## Usage

Run the full pipeline:

```bash
python3 main.py
```

Outputs (gitignored):

- `data/market_data.db`: persisted market snapshots, one row per run.
- `research/coinbase_positioning.md`: Coinbase Prime positioning research.
- `output/coinbase_challenge_submission.md`: Google-Doc-ready draft + QA report + AI disclosure.

Run individual agents:

```bash
python3 agents/market_data_agent.py
python3 agents/coinbase_research_agent.py
python3 agents/qa_agent.py < output/coinbase_challenge_submission.md
```

## Data sources

| Field | Source |
|---|---|
| BTC spot | Coinbase Exchange REST API |
| BTC futures basis | Deribit quarterly futures (proxy) |
| BTC implied volatility | Deribit volatility index |
| CME BTC futures open interest | Yahoo Finance metadata (BTC=F) |
| BTC perpetual funding | Binance perpetuals (leveraged-demand proxy) |
| Coinbase Prime positioning | Claude web search agent over Coinbase Institutional pages |

If any source is unreachable, the relevant agent falls back to a clearly labeled local placeholder so the pipeline still produces an editable output.

## Concepts the pipeline demonstrates

- Multi-agent decomposition with hard role separation
- Persistent snapshots in sqlite (the run is reproducible from the snapshot)
- Hard word caps enforced at generation time, not edit time
- QA as a separate agent with explicit grading criteria
- AI disclosure on every output by default
- Graceful degradation when an external data source is offline
- Structured-output expectations from each agent (markdown sections with predictable shape)

## Status

- ✅ Pipeline runs end-to-end
- ✅ All four agents working
- ✅ QA agent scoring against six grading criteria
- ✅ AI disclosure on output
- ⏳ Actual submission answers held until after the June 1, 2026 deadline (then either redacted or added as `examples/`)

## Submission self-rules

The pipeline is *infrastructure*, not the submission. Rules I held myself to:

1. Every fact in the submission must be human-verifiable against the snapshot in `data/market_data.db`.
2. The QA agent's score is informational, not gating. A human must read the full draft.
3. AI disclosure is mandatory on the submitted version, not optional.
4. Word caps are enforced at the generation step; the editor only tightens.

## License

MIT. See [LICENSE](LICENSE).

## Contact

cesalas13@gmail.com | linkedin.com/in/cesalas13 | github.com/cesalas13
