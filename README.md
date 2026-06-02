# Institutional Crypto Strategy Research Pipeline

A small multi-agent research pipeline for producing institutional digital-asset strategy briefs.

The workflow is built around a practical analyst use case: collect a market snapshot, research an institutional positioning question, draft a concise memo, and run an independent QA pass before a human edits the final recommendation.

```text
market snapshot agent -> positioning research agent -> strategy memo generator -> QA reviewer
        |                         |                         |                    |
 BTC spot / basis / IV      cited institutional        concise draft       word counts,
 OI / funding snapshot      positioning memo           recommendation      scoring, edits
 sqlite persistence         source-backed notes        markdown output     review flags
```

This is not a trading bot and it does not make investment decisions. It is research infrastructure: the agents handle the repetitive work of snapshotting, drafting, formatting, and review so the operator can focus on judgment.

## Why This Is Useful

Someone trying to break into crypto markets, hedge fund research, fintech strategy, or institutional sales needs to show more than opinions. They need a repeatable way to turn market data and source research into a clear written view.

This repo demonstrates that workflow in a concrete way:

- Pull market data instead of hand-copying numbers from tabs.
- Store snapshots so a memo can be traced back to the data available at run time.
- Separate research, drafting, and QA into different agents with clear responsibilities.
- Enforce writing constraints before the human edit pass.
- Keep AI output human-in-the-loop, cited, and reviewable.

Example use cases:

- BTC basis-trade briefing for a hedge fund analyst.
- Digital-asset market note for a consultant or research associate.
- Institutional client prep for a crypto prime brokerage or fintech sales team.
- Investment committee first draft that needs fast data, tight structure, and clear caveats.
- Portfolio project for someone learning how market research workflows can use agents responsibly.

## Origin

The first version was built around an institutional client strategy exercise involving Bitcoin basis, Coinbase Prime positioning, and client prioritization. The public repo frames that work as reusable research infrastructure rather than a one-off answer.

Coinbase, Deribit, Binance, Yahoo Finance, and public web research are used as example sources. The same architecture can be adapted to other markets, instruments, or strategy questions.

## Architecture

```text
coinbase-challenge/
├── agents/
│   ├── market_data_agent.py        # BTC spot, futures basis, IV, OI, funding
│   ├── coinbase_research_agent.py  # institutional positioning research
│   ├── answer_generator.py         # concise strategy memo sections
│   └── qa_agent.py                 # word counts, scoring, review flags
├── research/
│   └── coinbase_positioning.md     # cited positioning notes
├── skills/
│   └── coinbase-basis-challenge/
│       └── SKILL.md                # workflow scope and role instructions
├── data/                           # runtime sqlite snapshots, gitignored
├── output/                         # generated drafts, gitignored
├── examples/                       # redacted example outputs
├── main.py                         # orchestrator
├── config.py
├── requirements.txt
└── .env.example
```

## Agent Roles

| Agent | Owns | Output |
|---|---|---|
| `market_data_agent` | BTC spot, futures basis, implied vol, CME open interest, perp funding | sqlite snapshot + bullet summary |
| `coinbase_research_agent` | Institutional positioning research using Claude web search | markdown memo with citations |
| `answer_generator` | Concise strategy sections under word caps | markdown draft |
| `qa_agent` | Word counts, scoring criteria, missing caveats, edit flags | QA report appended to the draft |

The orchestrator runs the agents in sequence and assembles a Google-Doc-ready markdown draft with a source note and AI disclosure.

## What A Beginner Can Learn From This

This repo is useful as a field-entry project because it shows the work behind a credible research memo:

- how to structure a market data snapshot
- how to keep generated analysis tied to reproducible inputs
- how to separate data collection from judgment
- how to use agents as reviewers, not just writers
- how to make AI-assisted work transparent with disclosure and source notes
- how to design a workflow that degrades gracefully when external data is unavailable

The goal is not to claim production-grade research coverage. The goal is to show a practical pattern that a junior analyst, consultant, or operator could build on.

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
export ANTHROPIC_API_KEY=<your_anthropic_api_key>
export ANTHROPIC_MODEL=claude-sonnet-4-20250514
```

`sqlite3` is part of the Python standard library and does not need to be installed through pip.

## Usage

Run the full pipeline:

```bash
python3 main.py
```

Outputs, which are gitignored:

- `data/market_data.db`: persisted market snapshots, one row per run.
- `research/coinbase_positioning.md`: institutional positioning research.
- `output/institutional_crypto_strategy_brief.md`: Google-Doc-ready draft + QA report + AI disclosure.

Run individual agents:

```bash
python3 agents/market_data_agent.py
python3 agents/coinbase_research_agent.py
python3 agents/qa_agent.py < output/institutional_crypto_strategy_brief.md
```

## Data Sources

| Field | Example source |
|---|---|
| BTC spot | Coinbase Exchange REST API |
| BTC futures basis | Deribit quarterly futures proxy |
| BTC implied volatility | Deribit volatility index |
| CME BTC futures open interest | Yahoo Finance metadata for `BTC=F` |
| BTC perpetual funding | Binance perpetuals as a leveraged-demand proxy |
| Institutional positioning | Claude web search over public institutional pages |

If a source is unreachable, the relevant agent falls back to a clearly labeled local placeholder so the pipeline still produces an editable output.

## Responsible Use

This project is for research workflow demonstration and education. It is not financial advice, not a live trading system, and not a substitute for human diligence.

Good use:

- generate a first-pass research brief
- compare market snapshots over time
- practice institutional-style writing
- test agent role separation and QA review
- create a portfolio artifact around practical AI-assisted research

Bad use:

- trade directly from generated text
- treat placeholder data as live market data
- publish a memo without checking sources
- remove the AI disclosure from generated output

## Concepts Demonstrated

- Multi-agent decomposition with hard role separation
- Persistent snapshots in sqlite
- Human-in-the-loop strategy research
- Word-cap and structure enforcement before editing
- QA as a separate review agent
- AI disclosure by default
- Graceful degradation when external sources are offline
- Structured markdown outputs that can move into a Doc or memo

## Status

- Pipeline runs end to end
- Four-agent workflow is implemented
- QA agent scores drafts against explicit criteria
- AI disclosure is included in generated output
- Examples are redacted or held back where needed

## License

MIT. See [LICENSE](LICENSE).

## Contact

github.com/cesalas13
