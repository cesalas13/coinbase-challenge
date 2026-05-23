---
name: coinbase-basis-challenge
description: Generate commercially sharp answers for the Coinbase Institutional Client Strategy Challenge, with Bitcoin basis trade mechanics, Coinbase Prime positioning, institutional discovery, market context, and QA criteria.
---

# Coinbase Institutional Client Strategy Challenge

## CRITICAL INSIGHTS (From Research)

### Hidden Equivalence
BlackRock contracts Coinbase Custody for IBIT. Both Path A (Coinbase direct) and Path B (IBIT + CME) end at the same Coinbase vault. The choice is wrapper economics, not counterparty diversification.

### Breakeven Analysis (calibrate per current market)

Build a net-return stack for both execution paths and compare:
- Path A (Coinbase Prime): annualized all-in cost = spot execution + custody + financing + slippage.
- Path B (IBIT + CME): annualized all-in cost = ETF expense ratio + CME margin drag + tracking error + creation/redemption friction.
- Breakeven basis: the level above which the trade clears the operational hurdle for the chosen route.
- Use the live market_data snapshot for current basis vs your breakeven.

### Coinbase Prime (verify against current public Institutional pages)

Categories to refresh before drafting:
- Execution model (agency vs principal).
- Cross-margin scope and asset coverage.
- Regulatory stack (state and federal).
- Headline scale stats (AUC, quarterly volume, asset count).
- Hedge fund / institutional adoption signals.

### Market Context (use live snapshot, not hardcodes)

Pull from market_data_agent at run time and interpret:
- BTC spot.
- BTC quarterly futures basis.
- BTC implied volatility.
- CME BTC futures open interest.
- BTC perpetual funding.

Use this skill to draft, critique, and refine a research submission for a Bitcoin basis-trade institutional challenge. Optimize for commercial judgment, client intuition, prioritization, questioning ability, market awareness, and structured thinking.

## Exercise Constraints (calibrate per challenge brief)

- Exercise 1: hard word cap. Compare a direct-execution route vs an ETF + listed-futures route for a sized cash-and-carry trade.
- Exercise 2: hard word cap. Prioritize competing client/product demands.
- Exercise 3: hard word cap. Ask high-signal discovery questions with brief rationale.
- Exercise 4: hard word cap. Use the live market snapshot. Format each point as `[Data point]: [Implication for basis trade]`.
- Total submission: under the brief's total cap. Leave room for an AI disclosure outside the main answer if allowed.
- Tone: commercial, precise, candid. Avoid fan language, generic institutional jargon, and unsupported claims.

## Basis Trade Mechanics

Classic cash-and-carry:
1. Buy spot BTC or spot exposure.
2. Short BTC futures or perpetuals.
3. Hold until convergence or actively manage margin and funding.
4. Gross spread = futures price - spot price.
5. Annualized basis = `(futures / spot - 1) * 365 / days_to_expiry`.
6. Net return = annualized basis minus financing, borrow, custody, execution, ETF fees, margin drag, operational costs, and slippage.

Coinbase Prime path:
- Buy spot BTC on Coinbase Prime or via algorithmic execution.
- Custody BTC in segregated institutional custody.
- Finance/margin through Prime where available.
- Hedge with listed futures, OTC derivatives, or venue-accessible instruments depending on client permissions.
- Benefits: direct BTC ownership, integrated execution/custody/financing/reporting, institutional controls, potential cross-margin efficiencies, lower ETF basis leakage, and cleaner operational chain.
- Costs/risks: spot execution fees, custody/financing charges, onboarding and legal review, exchange liquidity at target size, futures margin outside Coinbase if hedge is at CME, operational dependency on crypto-native infrastructure.

IBIT + CME path:
- Buy IBIT shares and short CME BTC futures.
- Benefits: familiar TradFi rails, existing brokerage/custody workflows, ETF operational simplicity, CME liquidity, no direct crypto custody.
- Costs/risks: IBIT expense ratio, ETF premium/discount and creation/redemption frictions, borrow/financing and margin drag, tracking error, less control over execution timing, weaker connection to broader crypto services, and less ability to use native BTC as collateral.

Decision rule:
- Prefer Coinbase if the client wants direct BTC exposure, broader crypto infrastructure, financing/custody integration, rapid expansion into other digital assets, or can monetize cross-margin/operational simplicity.
- Prefer IBIT+CME if the client cannot custody crypto, has a strict listed-securities mandate, wants the least new vendor risk, or the expected net basis is too small to compensate for onboarding.

## Cost Model Checklist

For each route, build a net return stack:
- Gross annualized basis.
- Spot or ETF execution spread.
- Commissions and exchange fees.
- Custody or ETF management fees.
- Financing rate on cash and margin.
- Futures initial/variation margin liquidity cost.
- Slippage at target size.
- Operational/legal cost of onboarding.
- Tax, accounting, and mandate constraints.

Use a threshold mindset: a basis trade is not attractive because the spread is positive; it is attractive only if net spread clears the client's cost of capital and operational hurdle after stress.

## Coinbase Prime Positioning

Position Coinbase Prime as an agency-only, institution-first platform. Do not claim principal risk-taking. Emphasize:
- Agency execution aligned with client outcomes.
- Integrated trading, custody, financing, staking where applicable, reporting, and governance controls.
- Segregated cold storage and institutional policy controls.
- Cross-margin and collateral efficiency where available.
- A bridge between crypto-native liquidity and institutional operating standards.
- A strategic platform for future crypto activity, not only a one-off trade venue.

Be honest:
- Coinbase may not be best for every mandate.
- CME and ETF rails can be simpler for clients whose investment policy excludes direct digital assets.
- The commercial role is to quantify the tradeoff, not force the venue.

## Institutional Decision Frameworks

Classify client intent:
- Strategic: building digital-asset operating capability, recurring allocation, multi-asset roadmap, custody and governance needs.
- Tactical: harvest a temporary basis spread, limited mandate, short holding period, minimal infrastructure appetite.

Assess constraints:
- Investment policy and eligible instruments.
- Custody permissions and wallet governance.
- Counterparty approvals.
- Margin and collateral treatment.
- Reporting, audit, tax, and compliance needs.
- Trade size, liquidity, slippage, and urgency.
- Decision-maker map: PM, treasury, risk, legal, ops, CIO.

Commercial prioritization:
- Expected revenue and wallet share.
- Probability of conversion.
- Strategic value and repeatability.
- Time sensitivity.
- Delegatability.
- Risk of disappointing a major client or internal stakeholder.

## Market Context Indicators

Use current data where possible:
- BTC spot price.
- Front/next quarterly futures price.
- Basis spread in dollars and annualized percentage.
- Bitcoin implied volatility.
- Perpetual funding rate as a proxy for leveraged demand.
- CME BTC futures open interest as institutional participation signal.
- ETF flows and basis compression/widening when available.

Interpretation patterns:
- Wide positive basis: carry may be attractive, but check margin cost and crowdedness.
- Low basis: operational frictions may erase returns; Coinbase pitch should shift to strategic infrastructure.
- High IV: execution and margin stress matter more; ask about drawdown and liquidity buffers.
- High OI: validates institutional depth but may signal crowded unwinds.
- Positive perp funding: leveraged long demand can support basis but can reverse sharply.

## Discovery Questions

Ask questions that change the recommendation:
1. Is this a tactical basis harvest or part of a broader digital-asset operating build?
2. Can your mandate hold spot BTC directly, or are ETF/listed instruments required?
3. What net annualized return hurdle do you need after financing, margin, custody, and slippage?
4. How will treasury fund variation margin and stress liquidity if BTC moves sharply?
5. Who must approve custody, counterparty, accounting, and reporting workflows before trade date?

## Reference Patterns From Basis Skills

Adapt these patterns from basis-trading skills:
- Start with the basis assessment, then show the calculation.
- Separate gross basis from net basis after carry/financing.
- Compare implied financing/repo/funding to the client's actual cost of capital.
- Identify whether the futures leg is rich, cheap, or fair versus spot.
- Include historical context or percentile when available.
- Treat execution mechanics and margin as first-order, not footnotes.

For perp-funding basis:
- Funding is floating and path-dependent.
- Positive funding can disappear or flip; use conservative scenarios.
- Venue risk, collateral haircuts, liquidation mechanics, and borrow/funding caps can dominate headline yield.

For futures basis:
- Expiry, roll schedule, contract liquidity, and margin requirements drive realized return.
- Annualized basis must be matched to days to expiry.
- Stress the unwind: convergence is not enough if margin calls force early exit.

## Writing Guidance

Good answer qualities:
- Makes a defensible recommendation with caveats.
- Uses numbers and trade mechanics.
- Shows how a client strategy associate thinks commercially.
- Balances Coinbase advantages with client constraints.
- Avoids generic "trusted partner" phrasing unless tied to a concrete workflow.

Bad answer signals:
- Pure sales pitch.
- Ignores IBIT+CME advantages.
- Talks about Bitcoin direction instead of basis economics.
- Lists questions without explaining why they matter.
- Prioritizes everything as urgent.
