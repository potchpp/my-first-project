# Portfolio APR Core — Design

**Date:** 2026-09-18
**Status:** approved design, awaiting implementation plan
**Scope:** measurement core only (data model + private storage, return engine, benchmark source). Signal / opportunity / decision tools are separate follow-on specs that consume this one's outputs.

## 1. Goal

Answer, for the US-stock sleeve of the Dime! account, one question on every rolling window:
**did the active portfolio beat the S&P 500 over the same period, and which positions pulled the average up or down?**

The KPI is the owner's *Active Portfolio Return (APR) vs. a static benchmark*:
the index is a steady runner that runs the whole window; the portfolio is a relay
team whose members join, get cut, or get fed capital at any time. Late capital is
deliberately penalised (it is measured against the index's full-window run). This
is stricter than a shadow-portfolio / same-money-same-day comparison, and that is
intentional.

Non-goals: no trade execution, no broker connection, no financial advice framing.
Output is measurement and diagnostics only.

## 2. Decisions locked during design

| Decision | Choice | Why |
|---|---|---|
| Portfolio scope | US stocks only (Dime! sleeve) | Thai funds / gold / crypto vs. SPX is not a stock-picking test |
| Currency | USD; each trade = qty × USD price | KPI is stated in USD; FX moves are not picking skill |
| Cash flows | The trade rows themselves (buy = cash in, sell = cash out) | Matches how the account is funded (THB→USD auto-converts on purchase); avoids the messy currency rows |
| Benchmark | `^SP500TR` (S&P 500 Total Return index) from Yahoo Finance | Literal match to the KPI wording; dividends reinvested |
| Holding valuation | Unadjusted daily close | Dividends land as cash at Dime!, not reinvested; adjusted closes would overstate. Slightly understates return on dividend payers — conservative, documented |
| Input source of truth | The Google Sheet's Yahoo-Finance-format export, dropped into `portfolio/` under its own export name | Already exported from the owner's Google Sheet; normalised one-row-per-trade; no renaming step |
| Methodology | APR vs. static index as the KPI; TWR as a single diagnostic column | Owner's definition. Shadow-portfolio / XIRR explicitly dropped |

## 3. Input contract — the transactions file

Default path: `portfolio/My Asset Portfolio - Export - Yahoo Finance.csv` — the
Google Sheet's own export name, kept verbatim so the owner never renames anything
(override with `--transactions`). Yahoo Finance portfolio import format, exactly:

```
Symbol,Trade Date,Quantity,Purchase Price,Commission
AAPL,2022 12 15,0.1322706,141.15,0
RKLB,2025 07 22,-6,47.19,0
```

- `Symbol`: ticker as the owner writes it (`BRK.B` allowed). Mapped to Yahoo form for price lookup: `.` → `-` (`BRK.B` → `BRK-B`). Brief files use the stripped form (`BRKB.md`).
- `Trade Date`: `YYYY MM DD` (space-separated). Also accept `YYYY-MM-DD` and `YYYY/MM/DD`.
- `Quantity`: positive = buy, negative = sell. Fractional allowed. Zero is invalid.
- `Purchase Price`: USD per share, must be > 0.
- `Commission`: USD, ≥ 0, may be blank (treated as 0).

Validation happens once, at load, and is the only input validation in the system.
Any violation stops the run with the 1-based row number and the reason. Header
must match exactly (case-insensitive, whitespace-trimmed). Extra columns are an
error — the contract is the contract.

Trade cash value:
- buy: `cash_in = qty × price + commission`
- sell: `cash_out = |qty| × price − commission`

The owner re-exports the file whenever they trade. Known gap at design time: the
export has 3 sells while the Sheet shows 5 (RKLB 2025-12-22, KULR 2026-01-09);
the holdings table (§7) exists so such gaps are visible against the Dime! app.

## 4. Files

| Path | Role | Git |
|---|---|---|
| `portfolio/My Asset Portfolio - Export - Yahoo Finance.csv` | source of truth, owner-maintained (Sheet export, name kept verbatim) | ignored |
| `portfolio/cache/<YAHOO_SYMBOL>.csv` | daily closes per symbol, `date,close`, refreshed incrementally | ignored |
| `portfolio/report.md` | human report, regenerated every run | ignored |
| `portfolio/portfolio.json` | machine-readable output for other tools | ignored |
| `scripts/perf.py` | the entire engine, one file | tracked |
| `scripts/test_perf.py` | one stdlib `unittest` file, no network | tracked |
| `.gitignore` | already contains `portfolio/` | tracked |
| `.graphifyignore` | add `portfolio/` so private data never enters the knowledge graph | tracked |
| `.claude/skills/trading-desk/SKILL.md` | step 4 path changes from `portfolio.json` at root to `portfolio/portfolio.json` | tracked |

Only new dependency: `yfinance` (brings pandas). Everything else is stdlib.
Python 3.10.

## 5. Calculation

### 5.1 Calendar and prices

- Trading calendar = the dates on which `^SP500TR` has a close.
- For every held symbol and `^SP500TR`, fetch daily closes from (first trade date − 7 days) to as-of date. Cache per symbol; on a later run fetch only from the last cached date forward.
- A symbol with no price data at all (delisted / unknown to Yahoo — likely `DIPS`) is **excluded from every calculation** and listed in a warning at the top of the report. Its trades are ignored on both the portfolio and attribution side so totals stay internally consistent.
- Missing close on a trading day for a held symbol (holiday mismatch, gap) → carry the last known close forward.

### 5.2 Daily state

For each trading day `d` from the first trade to the as-of date:
- `qty[sym][d]` = cumulative signed quantity of trades dated ≤ d
- `value[sym][d]` = `qty × close(d)`
- `V[d]` = Σ over symbols

Trades dated on a non-trading day are treated as occurring on the next trading day.

### 5.3 Windows

Windows: `inception`, `6m`, `1y`, `2y`, `5y`. End `E` = last trading day ≤ as-of date (default: today).
Start `S`:
- rolling windows: last trading day ≤ (E − N months). Month arithmetic clamps to month end (e.g. 31 Aug − 6m → 28/29 Feb).
- `inception`: the trading day immediately before the first trade (so `V₀ = 0` and every trade is inside the window).

A rolling window whose nominal start precedes the first trade is reported as
`insufficient history` — no number.

Flows in a window are the trades with (adjusted) date in `(S, E]`. `V₀ = V[S]`, `V₁ = V[E]`.

### 5.4 APR — the KPI

Sell proceeds fund later buys before new money does. Process the window's trades
in date order with a cash bucket:

```
cash = 0; deposits = 0
for trade in window, date ascending:
    if sell:  cash += cash_out
    else:     use = min(cash, cash_in); cash -= use; deposits += cash_in - use
profit  = V1 + cash - V0 - deposits
capital = V0 + deposits
APR     = profit / capital          # undefined if capital == 0 → window skipped
```

Properties (all verified by tests in §9): a sell that is reinvested is not charged
as new capital; a sell that is not reinvested is returned capital and counts in
profit; a position opened and closed inside the window returns profit ÷ what was
put in; late capital sits in `capital` at full weight for the whole window.

Benchmark for the same window: `bench = SP500TR[E] / SP500TR[S] − 1`.

`alpha_pp = (APR − bench) × 100`. **KPI passes when `alpha_pp > 0`.**

### 5.5 Per-position attribution

Run §5.4 per symbol using only that symbol's trades and its own `V₀`, `V₁`:
- `apr_sym`
- `contribution_pp = profit_sym / capital_total × 100` — its share of the total APR in percentage points. Contributions sum exactly to total APR (the per-symbol ledgers only differ from the total ledger by cross-symbol recycling, which cancels).
- `underperformer = apr_sym < bench` for that window.

Positions are ranked by `contribution_pp` descending in the report.

### 5.6 TWR — diagnostic only, total portfolio

Daily chain-link over the window with flows assumed at end of day:
`r_d = (V[d] − F_d) / V[d−1] − 1`, `TWR = Π(1 + r_d) − 1`, where `F_d` = net cash in on day d (buys − sells). Days with `V[d−1] = 0` are skipped. Benchmark TWR = `bench`.

Reading: TWR > bench but APR < bench → picks were fine, deployment timing leaked.

## 6. CLI

```
python3 scripts/perf.py                 # refresh prices, compute, print, write report.md + portfolio.json
python3 scripts/perf.py --no-fetch      # cache only (offline)
python3 scripts/perf.py --as-of 2026-06-30
python3 scripts/perf.py --transactions path/to/other.csv
```

Exit code 0 on success, 1 on validation failure or when no symbol could be priced.

## 7. Outputs

### 7.1 Terminal / `portfolio/report.md`

```
Portfolio APR vs S&P 500 TR — as of 2026-09-18
Excluded (no price data): DIPS

Window     APR      S&P TR   Alpha    TWR      Verdict
inception  +41.2%   +38.0%   +3.2pp   +45.1%   BEAT
6m         +9.8%    +11.4%   -1.6pp   +10.2%   BEHIND
1y         +21.0%   +17.5%   +3.5pp   +19.9%   BEAT
2y         +38.7%   +35.2%   +3.5pp   +40.0%   BEAT
5y         insufficient history

Positions (1y window, ranked by contribution)
Symbol  Qty      Value    Weight  APR      vs S&P   Contrib   Flag
NVDA    12.31    $2,140   18.4%   +52.1%   +34.6pp  +4.9pp
RKLB    31.20    $2,005   17.2%   +88.3%   +70.8pp  +4.1pp
...
NFLX    14.02    $1,230   10.6%   -22.4%   -39.9pp  -2.7pp    UNDERPERFORM
PTON    29.32    $144     1.2%    -18.0%   -35.5pp  -0.2pp    UNDERPERFORM  no-brief

Holdings check (compare to the Dime! app)
Symbol  Qty        Avg cost   Last close
...
```

(Numbers above are illustrative, not real.)

### 7.2 `portfolio/portfolio.json`

```json
{
  "as_of": "2026-09-18",
  "benchmark": "^SP500TR",
  "excluded_symbols": ["DIPS"],
  "total_value_usd": 11640.5,
  "windows": {
    "inception": {"start": "2022-12-14", "end": "2026-09-18", "apr": 0.412, "bench": 0.380, "alpha_pp": 3.2, "twr": 0.451, "beat": true},
    "6m":        {"start": "2026-03-18", "end": "2026-09-18", "apr": 0.098, "bench": 0.114, "alpha_pp": -1.6, "twr": 0.102, "beat": false},
    "5y":        null
  },
  "positions": [
    {
      "symbol": "NVDA",
      "yahoo_symbol": "NVDA",
      "brief": "briefs/NVDA.md",
      "qty": 12.31,
      "avg_cost": 141.20,
      "last_close": 173.84,
      "value_usd": 2140.0,
      "weight": 0.184,
      "windows": {
        "inception": {"apr": 0.61, "bench": 0.380, "contribution_pp": 6.1, "underperformer": false},
        "1y":        {"apr": 0.521, "bench": 0.175, "contribution_pp": 4.9, "underperformer": false},
        "6m":        null
      }
    }
  ]
}
```

- `brief` is the path if `briefs/<SYMBOL-without-dots>.md` exists, else `null`. Downstream tools use this to enforce "only trade inside a thesis".
- A position's window is `null` when it had no value and no trades in that window.
- `positions` includes fully exited symbols only if they had activity inside at least one reported window (so a closed loser still shows its drag on 1y).
- Written atomically (write temp file, rename) so a consumer never reads a half-written file.

## 8. Errors and data quality

- `yfinance` missing → print `pip install yfinance` and exit 1.
- Yahoo unreachable → fall back to cache; symbols with no cache are excluded with a warning; if `^SP500TR` itself is unavailable, exit 1 (no benchmark, no KPI).
- Input validation: §3 only. Internal code is trusted; no defensive checks elsewhere.
- The tool never edits `transactions.csv`.

## 9. Testing

`scripts/test_perf.py`, stdlib `unittest`, synthetic trades and synthetic price
series injected directly (no network). The engine exposes pure functions that take
prices as a dict so tests never touch Yahoo:

1. **Late capital penalty**: index +20% over window; $100 held from start, $100 added on the last day, no price change on holdings → APR = 0% on $200, bench = 20%, alpha −20pp. (Confirms drag is charged.)
2. **Reinvested sell is not new capital**: sell $100 of A, buy $100 of B same window → `deposits` unchanged by that pair.
3. **Unreinvested sell is returned capital**: hold $100, sell all for $120, no other trades → APR = +20%.
4. **Round trip inside window**: buy $500, sell $600, nothing else, `V₀ = V₁ = 0` → APR = +20%.
5. **Contributions sum to total**: three symbols with mixed trades → Σ `contribution_pp` equals total APR × 100 within 1e-9.
6. **TWR ignores flows**: constant prices, a deposit mid-window → TWR = 0.
7. **Insufficient history**: as-of date 3 months after first trade → `6m` window is `None`.
8. **Validation**: a row with `Quantity = 0` → `ValueError` naming that row number.

## 10. Privacy

Everything the owner's data touches lives under `portfolio/`, which is in
`.gitignore` (verified: `git check-ignore` matches) and, after this work, in
`.graphifyignore`. The Stop hook stages only `briefs/`. `scripts/perf.py` and the
tests contain no real holdings. This spec contains no real amounts.

## 11. Deferred — next specs, in rough order of value

1. **Price-action signals** on the same price cache: distance from 52-week high, drawdown from peak, moving-average context — the "sell the spike / re-buy the dip" question the owner raised about RKLB.
2. **Portfolio-aware `trading-desk`**: risk manager reads `portfolio.json` for real weights, concentration, and the `underperformer` / `brief` flags.
3. **Kill-condition monitor**: cross `briefs/<SYMBOL>.md` kill conditions with news/sentiment for held positions.
4. Dime! PDF reconciliation (holdings snapshot vs. computed holdings), dividends and fees as explicit rows, cash-drag accounting via the currency rows.
