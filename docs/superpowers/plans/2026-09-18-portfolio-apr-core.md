# Portfolio APR Core Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** A single script that reads the owner's trade log, prices it against Yahoo Finance, and reports Active Portfolio Return vs. the static S&P 500 TR benchmark on rolling windows with per-position underperformer flags — written to `portfolio/report.md` and `portfolio/portfolio.json`.

**Architecture:** One engine file `scripts/perf.py` built from pure functions (trades + a prices dict in → results out) so every calculation is testable without network; a thin I/O layer (CSV loader, Yahoo fetch with per-symbol cache, report renderer, atomic JSON writer) around it. One stdlib `unittest` file drives all logic with synthetic prices.

**Tech Stack:** Python 3.10, stdlib (`csv`, `json`, `dataclasses`, `bisect`, `calendar`, `argparse`, `tempfile`), `yfinance` (the only new dependency, used solely inside one downloader function).

**Spec:** `docs/superpowers/specs/2026-09-18-portfolio-apr-core-design.md` — read it first; every formula below comes from §5 and every output shape from §7.

## Global Constraints

- Python 3.10 (`python3 --version` → 3.10.4). No `match` statements, no 3.11+ stdlib.
- Only new dependency: `yfinance`. Import it **only** inside `yahoo_download()` so tests and `--no-fetch` never need it.
- Never write real holdings, amounts, or tickers-with-quantities into any tracked file, test, or commit message. Tests use symbols `AAA`, `BBB`, `CCC`, `DDD` and made-up prices.
- Tests must never touch `portfolio/` — they use `tempfile.TemporaryDirectory()` and patch `perf.CACHE_DIR`.
- `portfolio/` is gitignored. Every commit below stages named files only; never `git add -A`.
- Default input path is exactly `portfolio/My Asset Portfolio - Export - Yahoo Finance.csv` (spaces included). Do not rename the owner's file.
- Benchmark symbol is the literal string `^SP500TR`.
- Commit messages end with the `Co-Authored-By:` line your session's attribution reminder specifies.
- Run tests with: `python3 scripts/test_perf.py -v` (the test file puts `scripts/` on `sys.path` and calls `unittest.main()`).
- Do not execute this plan on the Fable model (owner's rule). Execute on Sonnet; Haiku is acceptable for Tasks 8–9.

---

## File structure

| File | Responsibility |
|---|---|
| `scripts/perf.py` | Everything: `Trade` model, CSV loader + validation, calendar/window math, daily valuation, APR ledger, TWR, `compute()` assembling the result dict, price cache + Yahoo download, report renderer, atomic JSON writer, `main()`. Created in Task 1, extended in each task. Sections are separated by `# ---- <name> ----` comment lines in the order tasks add them. |
| `scripts/test_perf.py` | One `unittest` module. Created in Task 1, one `TestCase` class appended per task. Shared helpers `days()`, `series()`, `write_csv()` live at the top. |
| `.graphifyignore` | Gains `portfolio/` (Task 9). |
| `.claude/skills/trading-desk/SKILL.md` | Step 4/5 path changes to `portfolio/portfolio.json` (Task 9). |

Data shapes used across tasks (all tasks rely on these exact names):

- `Trade(symbol: str, date: datetime.date, qty: float, price: float, commission: float)` — frozen dataclass; `qty < 0` is a sell. Properties `is_sell -> bool`, `cash -> float` (positive: buy cost incl. commission, or sell proceeds net of commission).
- `Prices = Dict[str, Dict[date, float]]` — Yahoo symbol → `{trading date: unadjusted close}`. Must contain key `perf.BENCH`.
- `days: List[date]` — sorted trading calendar, always `sorted(prices[BENCH])`.
- Window bounds are index pairs `(s, e)` into `days`; flows in a window are trades with `days[s] < t.date <= days[e]`; `V0 = total[s]`, `V1 = total[e]`.

---

### Task 1: Trade model, CSV loader, validation, symbol helpers

**Files:**
- Create: `scripts/perf.py`
- Create: `scripts/test_perf.py`

**Interfaces:**
- Produces: `Trade` dataclass; `parse_date(text) -> date`; `load_trades(path: Path) -> List[Trade]` (sorted by date, raises `ValueError("row N: ...")`); `yahoo_symbol(symbol) -> str`; `brief_path(symbol) -> Optional[str]`; constants `ROOT`, `PORTFOLIO_DIR`, `DEFAULT_TRANSACTIONS`, `CACHE_DIR`, `BENCH`, `WINDOWS`.

- [ ] **Step 1: Write the failing tests**

Create `scripts/test_perf.py`:

```python
import json
import sys
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import perf  # noqa: E402
from perf import Trade  # noqa: E402


def days(n, start=date(2025, 1, 6)):
    """n consecutive weekdays starting at `start` (a Monday by default)."""
    out, d = [], start
    while len(out) < n:
        if d.weekday() < 5:
            out.append(d)
        d += timedelta(days=1)
    return out


def series(dates, closes):
    return dict(zip(dates, closes))


def write_csv(tmpdir, text):
    p = Path(tmpdir) / "t.csv"
    p.write_text(text, encoding="utf-8")
    return p


HEADER = "Symbol,Trade Date,Quantity,Purchase Price,Commission\n"


class LoadTests(unittest.TestCase):
    def test_parses_three_date_formats(self):
        for s in ("2025 01 15", "2025-01-15", "2025/01/15"):
            self.assertEqual(perf.parse_date(s), date(2025, 1, 15))

    def test_loads_buy_and_sell_sorted_with_cash(self):
        with tempfile.TemporaryDirectory() as d:
            p = write_csv(d, HEADER + "BRK.B,2025 01 15,2,100,1\nRKLB,2025 01 10,-3,50,1\n")
            trades = perf.load_trades(p)
        self.assertEqual([t.symbol for t in trades], ["RKLB", "BRK.B"])
        self.assertTrue(trades[0].is_sell)
        self.assertAlmostEqual(trades[0].cash, 149.0)   # 3*50 - 1 commission
        self.assertAlmostEqual(trades[1].cash, 201.0)   # 2*100 + 1 commission

    def test_blank_commission_is_zero_and_bom_is_ignored(self):
        with tempfile.TemporaryDirectory() as d:
            p = write_csv(d, "﻿" + HEADER + "AAPL,2025 01 15,1,10,\n")
            trades = perf.load_trades(p)
        self.assertEqual(trades[0].commission, 0.0)

    def test_zero_quantity_names_row(self):
        with tempfile.TemporaryDirectory() as d:
            p = write_csv(d, HEADER + "AAPL,2025 01 15,1,10,0\nAAPL,2025 01 16,0,10,0\n")
            with self.assertRaises(ValueError) as cm:
                perf.load_trades(p)
        self.assertIn("row 3", str(cm.exception))

    def test_extra_column_is_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p = write_csv(d, "Symbol,Trade Date,Quantity,Purchase Price,Commission,Extra\nAAPL,2025 01 15,1,10,0,x\n")
            with self.assertRaises(ValueError) as cm:
                perf.load_trades(p)
        self.assertIn("row 1", str(cm.exception))

    def test_yahoo_symbol_and_brief_path(self):
        self.assertEqual(perf.yahoo_symbol("BRK.B"), "BRK-B")
        self.assertEqual(perf.yahoo_symbol("NVDA"), "NVDA")
        self.assertIsNone(perf.brief_path("ZZZZNOTREAL"))
        self.assertEqual(perf.brief_path("NVDA"), "briefs/NVDA.md")   # exists in this repo
        self.assertEqual(perf.brief_path("BRK.B"), "briefs/BRKB.md")  # dot stripped


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 scripts/test_perf.py -v`
Expected: FAIL at import — `ModuleNotFoundError: No module named 'perf'`

- [ ] **Step 3: Write the implementation**

Create `scripts/perf.py`:

```python
#!/usr/bin/env python3
"""Portfolio APR vs S&P 500 TR.

Spec: docs/superpowers/specs/2026-09-18-portfolio-apr-core-design.md
"""
import argparse
import bisect
import calendar
import csv
import json
import os
import sys
import tempfile
from collections import defaultdict
from dataclasses import dataclass, replace
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

ROOT = Path(__file__).resolve().parent.parent
PORTFOLIO_DIR = ROOT / "portfolio"
DEFAULT_TRANSACTIONS = PORTFOLIO_DIR / "My Asset Portfolio - Export - Yahoo Finance.csv"
CACHE_DIR = PORTFOLIO_DIR / "cache"
BENCH = "^SP500TR"
WINDOWS = {"inception": None, "6m": 6, "1y": 12, "2y": 24, "5y": 60}

Prices = Dict[str, Dict[date, float]]


# ---- trades ----

@dataclass(frozen=True)
class Trade:
    symbol: str
    date: date
    qty: float
    price: float
    commission: float

    @property
    def is_sell(self) -> bool:
        return self.qty < 0

    @property
    def cash(self) -> float:
        gross = abs(self.qty) * self.price
        return gross - self.commission if self.is_sell else gross + self.commission


DATE_FORMATS = ("%Y %m %d", "%Y-%m-%d", "%Y/%m/%d")
EXPECTED_HEADER = ["symbol", "trade date", "quantity", "purchase price", "commission"]


def parse_date(text: str) -> date:
    text = text.strip()
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    raise ValueError(f"bad date {text!r} (expected YYYY MM DD)")


def load_trades(path: Path) -> List[Trade]:
    with open(path, newline="", encoding="utf-8-sig") as f:
        rows = list(csv.reader(f))
    if not rows:
        raise ValueError("row 1: empty file")
    header = [h.strip().lower() for h in rows[0]]
    if header != EXPECTED_HEADER:
        raise ValueError(f"row 1: header must be {EXPECTED_HEADER}, got {header}")
    trades = []
    for n, row in enumerate(rows[1:], start=2):
        if not any(cell.strip() for cell in row):
            continue
        try:
            sym, d, q, p, c = [cell.strip() for cell in row]
            qty, price = float(q), float(p)
            comm = float(c) if c else 0.0
            when = parse_date(d)
        except ValueError as e:
            raise ValueError(f"row {n}: {e}") from None
        if not sym:
            raise ValueError(f"row {n}: empty symbol")
        if qty == 0:
            raise ValueError(f"row {n}: quantity must not be 0")
        if price <= 0:
            raise ValueError(f"row {n}: price must be > 0")
        if comm < 0:
            raise ValueError(f"row {n}: commission must be >= 0")
        trades.append(Trade(sym.upper(), when, qty, price, comm))
    trades.sort(key=lambda t: t.date)
    return trades


def yahoo_symbol(symbol: str) -> str:
    return symbol.replace(".", "-")


def brief_path(symbol: str) -> Optional[str]:
    p = ROOT / "briefs" / f"{symbol.replace('.', '')}.md"
    return str(p.relative_to(ROOT)) if p.exists() else None
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 scripts/test_perf.py -v`
Expected: 6 tests, `OK`

- [ ] **Step 5: Commit**

```bash
git add scripts/perf.py scripts/test_perf.py
git commit -m "perf: trade model, CSV loader with row-numbered validation, symbol helpers"
```

---

### Task 2: Calendar and window bounds

**Files:**
- Modify: `scripts/perf.py` (append section `# ---- calendar ----`)
- Modify: `scripts/test_perf.py` (append `WindowTests`)

**Interfaces:**
- Consumes: nothing from Task 1 beyond the imports already present.
- Produces: `shift_months(d: date, months: int) -> date`; `index_at_or_before(days: List[date], target: date) -> Optional[int]`; `window_bounds(days, first_trade: date, as_of: date, months: Optional[int]) -> Optional[Tuple[int, int]]`.

- [ ] **Step 1: Write the failing tests**

Append to `scripts/test_perf.py` before the `if __name__` block:

```python
class WindowTests(unittest.TestCase):
    def test_shift_months_clamps_to_month_end(self):
        self.assertEqual(perf.shift_months(date(2026, 8, 31), -6), date(2026, 2, 28))
        self.assertEqual(perf.shift_months(date(2026, 3, 31), -1), date(2026, 2, 28))
        self.assertEqual(perf.shift_months(date(2026, 1, 15), -12), date(2025, 1, 15))

    def test_index_at_or_before(self):
        cal = days(5)                                     # Mon..Fri
        self.assertEqual(perf.index_at_or_before(cal, cal[2]), 2)
        self.assertEqual(perf.index_at_or_before(cal, cal[4] + timedelta(days=1)), 4)   # Saturday → Friday
        self.assertIsNone(perf.index_at_or_before(cal, cal[0] - timedelta(days=1)))

    def test_inception_window_starts_day_before_first_trade(self):
        cal = days(70)
        self.assertEqual(perf.window_bounds(cal, cal[1], cal[-1], None), (0, len(cal) - 1))
        self.assertIsNone(perf.window_bounds(cal, cal[0], cal[-1], None))  # no trading day before first trade

    def test_rolling_window_needs_enough_history(self):
        cal = days(70)   # ~3 months of weekdays
        self.assertIsNone(perf.window_bounds(cal, cal[1], cal[-1], 6))
        cal = days(300)  # ~14 months
        s, e = perf.window_bounds(cal, cal[1], cal[-1], 6)
        self.assertEqual(e, len(cal) - 1)
        target = perf.shift_months(cal[e], -6)
        self.assertLessEqual(cal[s], target)
        self.assertGreater(cal[s + 1], target)
        self.assertIsNone(perf.window_bounds(cal, cal[1], cal[-1], 24))
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 scripts/test_perf.py -v`
Expected: `WindowTests` fail with `AttributeError: module 'perf' has no attribute 'shift_months'`

- [ ] **Step 3: Write the implementation**

Append to `scripts/perf.py`:

```python
# ---- calendar ----

def shift_months(d: date, months: int) -> date:
    m = d.month - 1 + months
    y = d.year + m // 12
    m = m % 12 + 1
    return date(y, m, min(d.day, calendar.monthrange(y, m)[1]))


def index_at_or_before(days: List[date], target: date) -> Optional[int]:
    i = bisect.bisect_right(days, target) - 1
    return i if i >= 0 else None


def window_bounds(days: List[date], first_trade: date, as_of: date,
                  months: Optional[int]) -> Optional[Tuple[int, int]]:
    e = index_at_or_before(days, as_of)
    inception_s = index_at_or_before(days, first_trade - timedelta(days=1))
    if e is None or inception_s is None:
        return None
    if months is None:
        return (inception_s, e)
    s = index_at_or_before(days, shift_months(days[e], -months))
    if s is None or s < inception_s or s >= e:
        return None
    return (s, e)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 scripts/test_perf.py -v`
Expected: 10 tests, `OK`

- [ ] **Step 5: Commit**

```bash
git add scripts/perf.py scripts/test_perf.py
git commit -m "perf: trading calendar helpers and rolling window bounds"
```

---

### Task 3: Trade alignment and daily valuation

**Files:**
- Modify: `scripts/perf.py` (append section `# ---- valuation ----`)
- Modify: `scripts/test_perf.py` (append `ValuationTests`)

**Interfaces:**
- Consumes: `Trade`, `yahoo_symbol` (Task 1).
- Produces: `align_trades(trades, days) -> List[Trade]` (each trade moved to the first trading day ≥ its date; sorted by date); `daily_values(trades, prices, days) -> Dict[str, List[float]]` keyed by owner symbol plus `"__total__"`, one float per day index.

- [ ] **Step 1: Write the failing tests**

Append to `scripts/test_perf.py`:

```python
class ValuationTests(unittest.TestCase):
    def test_align_moves_weekend_trade_to_next_trading_day(self):
        cal = days(10)                       # Mon 6 Jan .. Fri 17 Jan 2025
        t = Trade("AAA", date(2025, 1, 11), 1, 1, 0)   # Saturday
        self.assertEqual(perf.align_trades([t], cal)[0].date, date(2025, 1, 13))
        late = Trade("AAA", date(2025, 1, 20), 1, 1, 0)  # after the calendar
        with self.assertRaises(ValueError):
            perf.align_trades([late], cal)

    def test_sell_reduces_holdings_and_missing_close_carries_forward(self):
        cal = days(5)
        prices = {perf.BENCH: series(cal, [100.0] * 5),
                  "AAA": {cal[0]: 10.0, cal[1]: 12.0, cal[3]: 20.0, cal[4]: 20.0}}  # cal[2] missing
        trades = [Trade("AAA", cal[0], 3, 10, 0), Trade("AAA", cal[3], -1, 20, 0)]
        v = perf.daily_values(trades, prices, cal)
        self.assertEqual(v["AAA"], [30.0, 36.0, 36.0, 40.0, 40.0])
        self.assertEqual(v["__total__"], v["AAA"])

    def test_fully_sold_position_values_to_zero(self):
        cal = days(3)
        prices = {perf.BENCH: series(cal, [1.0] * 3), "AAA": series(cal, [10.0] * 3)}
        trades = [Trade("AAA", cal[0], 0.3, 10, 0), Trade("AAA", cal[1], -0.1, 10, 0),
                  Trade("AAA", cal[1], -0.2, 10, 0)]
        v = perf.daily_values(trades, prices, cal)
        self.assertEqual(v["AAA"], [3.0, 0.0, 0.0])
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 scripts/test_perf.py -v`
Expected: `ValuationTests` fail with `AttributeError: ... 'align_trades'`

- [ ] **Step 3: Write the implementation**

Append to `scripts/perf.py`:

```python
# ---- valuation ----

def align_trades(trades: List[Trade], days: List[date]) -> List[Trade]:
    out = []
    for t in trades:
        i = bisect.bisect_left(days, t.date)
        if i >= len(days):
            raise ValueError(f"trade on {t.date} is after the last price date {days[-1]}")
        out.append(replace(t, date=days[i]))
    out.sort(key=lambda t: t.date)
    return out


def daily_values(trades: List[Trade], prices: Prices, days: List[date]) -> Dict[str, List[float]]:
    by_sym: Dict[str, List[Trade]] = defaultdict(list)
    for t in trades:
        by_sym[t.symbol].append(t)
    values: Dict[str, List[float]] = {}
    total = [0.0] * len(days)
    for sym, ts in by_sym.items():
        closes = prices[yahoo_symbol(sym)]
        qty, last_close, ti = 0.0, None, 0
        vals = []
        for i, d in enumerate(days):
            while ti < len(ts) and ts[ti].date == d:
                qty += ts[ti].qty
                ti += 1
            if d in closes:
                last_close = closes[d]
            v = qty * last_close if abs(qty) > 1e-9 and last_close is not None else 0.0
            vals.append(v)
            total[i] += v
        values[sym] = vals
    values["__total__"] = total
    return values
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 scripts/test_perf.py -v`
Expected: 13 tests, `OK`

- [ ] **Step 5: Commit**

```bash
git add scripts/perf.py scripts/test_perf.py
git commit -m "perf: align trades to trading days and value holdings daily"
```

---

### Task 4: APR ledger (the KPI)

**Files:**
- Modify: `scripts/perf.py` (append section `# ---- returns ----`)
- Modify: `scripts/test_perf.py` (append `AprTests`)

**Interfaces:**
- Consumes: `Trade` (Task 1).
- Produces: `apr(trades: List[Trade], v0: float, v1: float) -> Optional[dict]` returning `{"profit": float, "capital": float, "apr": float}` or `None` when capital is zero. Implements spec §5.4 exactly.

- [ ] **Step 1: Write the failing tests**

Append to `scripts/test_perf.py`:

```python
class AprTests(unittest.TestCase):
    def test_late_capital_is_charged_for_the_full_window(self):
        # $100 held all window, $100 added on the last day, prices flat
        a = perf.apr([Trade("A", date(2025, 6, 30), 1, 100, 0)], v0=100, v1=200)
        self.assertAlmostEqual(a["apr"], 0.0)
        self.assertEqual(a["capital"], 200)

    def test_reinvested_sell_is_not_new_capital(self):
        t = [Trade("A", date(2025, 3, 1), -1, 100, 0), Trade("B", date(2025, 3, 2), 1, 100, 0)]
        a = perf.apr(t, v0=100, v1=100)
        self.assertEqual(a["capital"], 100)
        self.assertAlmostEqual(a["apr"], 0.0)

    def test_unreinvested_sell_is_returned_capital(self):
        a = perf.apr([Trade("A", date(2025, 3, 1), -1, 120, 0)], v0=100, v1=0)
        self.assertAlmostEqual(a["apr"], 0.20)

    def test_round_trip_inside_window(self):
        t = [Trade("A", date(2025, 3, 1), 5, 100, 0), Trade("A", date(2025, 4, 1), -5, 120, 0)]
        a = perf.apr(t, v0=0, v1=0)
        self.assertAlmostEqual(a["apr"], 0.20)
        self.assertEqual(a["capital"], 500)

    def test_partial_recycle_then_new_money(self):
        # sell 100, buy 250 → 100 recycled, 150 new capital
        t = [Trade("A", date(2025, 3, 1), -1, 100, 0), Trade("B", date(2025, 3, 2), 1, 250, 0)]
        a = perf.apr(t, v0=100, v1=250)
        self.assertEqual(a["capital"], 250)
        self.assertAlmostEqual(a["profit"], 0.0)

    def test_order_matters_buy_before_sell_is_not_recycled(self):
        t = [Trade("B", date(2025, 3, 1), 1, 100, 0), Trade("A", date(2025, 3, 5), -1, 100, 0)]
        a = perf.apr(t, v0=100, v1=100)
        self.assertEqual(a["capital"], 200)   # the buy came first, so it is new money
        self.assertAlmostEqual(a["profit"], 100 + 100 - 100 - 100)

    def test_no_capital_returns_none(self):
        self.assertIsNone(perf.apr([], v0=0, v1=0))
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 scripts/test_perf.py -v`
Expected: `AprTests` fail with `AttributeError: ... 'apr'`

- [ ] **Step 3: Write the implementation**

Append to `scripts/perf.py`:

```python
# ---- returns ----

def apr(trades: List[Trade], v0: float, v1: float) -> Optional[dict]:
    """Spec §5.4: sell proceeds fund later buys before new money does."""
    cash, deposits = 0.0, 0.0
    for t in sorted(trades, key=lambda t: t.date):
        if t.is_sell:
            cash += t.cash
        else:
            use = min(cash, t.cash)
            cash -= use
            deposits += t.cash - use
    capital = v0 + deposits
    if capital <= 1e-9:
        return None
    profit = v1 + cash - v0 - deposits
    return {"profit": profit, "capital": capital, "apr": profit / capital}
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 scripts/test_perf.py -v`
Expected: 20 tests, `OK`

- [ ] **Step 5: Commit**

```bash
git add scripts/perf.py scripts/test_perf.py
git commit -m "perf: APR ledger with sell-proceeds-first capital accounting"
```

---

### Task 5: TWR diagnostic

**Files:**
- Modify: `scripts/perf.py` (append to `# ---- returns ----`)
- Modify: `scripts/test_perf.py` (append `TwrTests`)

**Interfaces:**
- Produces: `twr(total: List[float], flows: Dict[int, float], s: int, e: int) -> Optional[float]` — `flows[i]` is net cash in (buys − sells) on day index `i`; days where `total[i-1]` is ~0 are skipped; `None` if no day contributed. Spec §5.6.

- [ ] **Step 1: Write the failing tests**

Append to `scripts/test_perf.py`:

```python
class TwrTests(unittest.TestCase):
    def test_deposit_does_not_move_twr(self):
        total = [100.0, 100.0, 200.0, 200.0, 200.0]
        self.assertAlmostEqual(perf.twr(total, {2: 100.0}, 0, 4), 0.0)

    def test_twr_tracks_price_growth(self):
        self.assertAlmostEqual(perf.twr([100.0, 110.0, 121.0], {}, 0, 2), 0.21)

    def test_twr_skips_days_with_no_prior_value(self):
        total = [0.0, 100.0, 110.0]          # position opened on day 1 with a 100 deposit
        self.assertAlmostEqual(perf.twr(total, {1: 100.0}, 0, 2), 0.10)

    def test_twr_none_when_never_invested(self):
        self.assertIsNone(perf.twr([0.0, 0.0, 0.0], {}, 0, 2))
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 scripts/test_perf.py -v`
Expected: `TwrTests` fail with `AttributeError: ... 'twr'`

- [ ] **Step 3: Write the implementation**

Append to `scripts/perf.py`:

```python
def twr(total: List[float], flows: Dict[int, float], s: int, e: int) -> Optional[float]:
    growth, any_day = 1.0, False
    for i in range(s + 1, e + 1):
        prev = total[i - 1]
        if prev <= 1e-9:
            continue
        growth *= (total[i] - flows.get(i, 0.0)) / prev
        any_day = True
    return growth - 1 if any_day else None
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 scripts/test_perf.py -v`
Expected: 24 tests, `OK`

- [ ] **Step 5: Commit**

```bash
git add scripts/perf.py scripts/test_perf.py
git commit -m "perf: time-weighted return diagnostic"
```

---

### Task 6: `compute()` — windows, positions, attribution

**Files:**
- Modify: `scripts/perf.py` (append section `# ---- compute ----`)
- Modify: `scripts/test_perf.py` (append `ComputeTests`)

**Interfaces:**
- Consumes: `align_trades`, `daily_values` (Task 3), `window_bounds`, `index_at_or_before` (Task 2), `apr` (Task 4), `twr` (Task 5), `yahoo_symbol`, `brief_path`, `BENCH`, `WINDOWS` (Task 1).
- Produces: `compute(trades, prices, as_of, excluded=()) -> dict` in the exact `portfolio.json` shape of spec §7.2 (with `start`/`end`/`as_of` as ISO strings); `avg_cost(sym_trades, upto) -> Optional[float]`; `last_close(closes, d) -> Optional[float]`; `rank_window(result) -> str` (`"1y"` if that window exists else `"inception"`).

- [ ] **Step 1: Write the failing tests**

Append to `scripts/test_perf.py`:

```python
class ComputeTests(unittest.TestCase):
    def setUp(self):
        self.cal = c = days(300)             # ~14 months of weekdays
        n = len(c)
        self.prices = {
            perf.BENCH: series(c, [100 + i * 0.1 for i in range(n)]),   # +~30%
            "AAA": series(c, [10 + i * 0.05 for i in range(n)]),          # strong winner
            "BBB": series(c, [50 - i * 0.05 for i in range(n)]),          # loser
            "CCC": series(c, [20.0] * n),                                  # flat
            "DDD": series(c, [5.0] * n),                                   # round-tripped early
        }
        self.trades = [
            Trade("AAA", c[1], 10, 10.05, 0),
            Trade("BBB", c[1], 2, 49.95, 0),
            Trade("DDD", c[10], 4, 5, 0),
            Trade("DDD", c[20], -4, 5, 0),
            Trade("CCC", c[100], 5, 20, 0),
            Trade("BBB", c[150], -1, 50 - 150 * 0.05, 0),
            Trade("AAA", c[200], 5, 10 + 200 * 0.05, 0),
        ]

    def test_windows_present_or_null_by_history(self):
        r = perf.compute(self.trades, self.prices, self.cal[-1])
        self.assertEqual(r["as_of"], self.cal[-1].isoformat())
        self.assertEqual(r["benchmark"], perf.BENCH)
        for name in ("inception", "6m", "1y"):
            self.assertIsNotNone(r["windows"][name], name)
        self.assertIsNone(r["windows"]["2y"])
        self.assertIsNone(r["windows"]["5y"])
        w = r["windows"]["inception"]
        self.assertEqual(w["start"], self.cal[0].isoformat())
        self.assertEqual(set(w), {"start", "end", "apr", "bench", "alpha_pp", "twr", "beat"})
        self.assertAlmostEqual(w["alpha_pp"], (w["apr"] - w["bench"]) * 100)
        self.assertEqual(w["beat"], w["apr"] > w["bench"])

    def test_contributions_sum_to_total_apr(self):
        r = perf.compute(self.trades, self.prices, self.cal[-1])
        for name in ("inception", "6m", "1y"):
            w = r["windows"][name]
            total_pp = sum(p["windows"][name]["contribution_pp"]
                           for p in r["positions"] if p["windows"][name])
            self.assertAlmostEqual(total_pp, w["apr"] * 100, places=9, msg=name)

    def test_underperformer_flags_and_inactive_windows(self):
        r = perf.compute(self.trades, self.prices, self.cal[-1])
        by = {p["symbol"]: p for p in r["positions"]}
        self.assertTrue(by["BBB"]["windows"]["inception"]["underperformer"])
        self.assertFalse(by["AAA"]["windows"]["inception"]["underperformer"])
        self.assertIn("DDD", by)                                  # exited, but active at inception
        self.assertIsNone(by["DDD"]["windows"]["6m"])             # no value, no trades in 6m
        self.assertIsNone(by["DDD"]["brief"])
        self.assertAlmostEqual(by["DDD"]["qty"], 0.0)
        self.assertEqual(by["AAA"]["yahoo_symbol"], "AAA")
        self.assertAlmostEqual(by["AAA"]["qty"], 15.0)
        self.assertAlmostEqual(by["AAA"]["avg_cost"], (10 * 10.05 + 5 * 20.0) / 15)
        self.assertAlmostEqual(sum(p["weight"] for p in r["positions"]), 1.0)
        self.assertEqual(r["positions"][0]["symbol"], "AAA")      # ranked by 1y contribution

    def test_late_capital_alpha_matches_spec_example(self):
        cal = days(300)
        n = len(cal)
        prices = {perf.BENCH: series(cal, [100.0] * (n - 1) + [120.0]),
                  "AAA": series(cal, [10.0] * n)}
        trades = [Trade("AAA", cal[1], 10, 10, 0), Trade("AAA", cal[-1], 10, 10, 0)]
        r = perf.compute(trades, prices, cal[-1], excluded=["ZZZ"])
        w = r["windows"]["inception"]
        self.assertAlmostEqual(w["apr"], 0.0)
        self.assertAlmostEqual(w["bench"], 0.20)
        self.assertAlmostEqual(w["alpha_pp"], -20.0)
        self.assertFalse(w["beat"])
        self.assertEqual(r["excluded_symbols"], ["ZZZ"])
        self.assertEqual(perf.rank_window(r), "1y")

    def test_helpers(self):
        cal = days(3)
        closes = {cal[0]: 1.0, cal[2]: 3.0}
        self.assertEqual(perf.last_close(closes, cal[1]), 1.0)
        self.assertEqual(perf.last_close(closes, cal[2]), 3.0)
        self.assertIsNone(perf.last_close({}, cal[0]))
        ts = [Trade("A", cal[0], 2, 10, 1), Trade("A", cal[1], -1, 50, 0), Trade("A", cal[2], 2, 20, 0)]
        self.assertAlmostEqual(perf.avg_cost(ts, cal[1]), 21 / 2)        # sells don't change avg cost
        self.assertAlmostEqual(perf.avg_cost(ts, cal[2]), (21 + 40) / 4)
        self.assertIsNone(perf.avg_cost([], cal[0]))
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 scripts/test_perf.py -v`
Expected: `ComputeTests` fail with `AttributeError: ... 'compute'`

- [ ] **Step 3: Write the implementation**

Append to `scripts/perf.py`:

```python
# ---- compute ----

def avg_cost(sym_trades: List[Trade], upto: date) -> Optional[float]:
    buys = [t for t in sym_trades if not t.is_sell and t.date <= upto]
    q = sum(t.qty for t in buys)
    return sum(t.cash for t in buys) / q if q else None


def last_close(closes: Dict[date, float], d: date) -> Optional[float]:
    if d in closes:
        return closes[d]
    prior = [k for k in closes if k <= d]
    return closes[max(prior)] if prior else None


def rank_window(result: dict) -> str:
    return "1y" if result["windows"].get("1y") else "inception"


def compute(trades: List[Trade], prices: Prices, as_of: date, excluded=()) -> dict:
    days = sorted(prices[BENCH])
    trades = align_trades(trades, days)
    first = trades[0].date
    values = daily_values(trades, prices, days)
    total = values["__total__"]
    bench = prices[BENCH]
    day_index = {d: i for i, d in enumerate(days)}
    flows: Dict[int, float] = defaultdict(float)
    for t in trades:
        flows[day_index[t.date]] += -t.cash if t.is_sell else t.cash
    e_idx = index_at_or_before(days, as_of)

    result = {
        "as_of": days[e_idx].isoformat(),
        "benchmark": BENCH,
        "excluded_symbols": list(excluded),
        "total_value_usd": round(total[e_idx], 2),
        "windows": {},
        "positions": [],
    }
    bounds = {}
    capital_total = {}
    for name, months in WINDOWS.items():
        b = window_bounds(days, first, as_of, months)
        bounds[name] = b
        if b is None:
            result["windows"][name] = None
            continue
        s, e = b
        in_win = [t for t in trades if days[s] < t.date <= days[e]]
        a = apr(in_win, total[s], total[e])
        if a is None:
            result["windows"][name] = None
            continue
        br = bench[days[e]] / bench[days[s]] - 1
        capital_total[name] = a["capital"]
        result["windows"][name] = {
            "start": days[s].isoformat(), "end": days[e].isoformat(),
            "apr": a["apr"], "bench": br, "alpha_pp": (a["apr"] - br) * 100,
            "twr": twr(total, flows, s, e), "beat": a["apr"] > br,
        }

    for sym in sorted({t.symbol for t in trades}):
        sym_trades = [t for t in trades if t.symbol == sym]
        vals = values[sym]
        pos = {
            "symbol": sym,
            "yahoo_symbol": yahoo_symbol(sym),
            "brief": brief_path(sym),
            "qty": sum(t.qty for t in sym_trades if t.date <= days[e_idx]),
            "avg_cost": avg_cost(sym_trades, days[e_idx]),
            "last_close": last_close(prices[yahoo_symbol(sym)], days[e_idx]),
            "value_usd": vals[e_idx],
            "weight": vals[e_idx] / total[e_idx] if total[e_idx] else 0.0,
            "windows": {},
        }
        active = False
        for name, b in bounds.items():
            w = result["windows"][name]
            if b is None or w is None:
                pos["windows"][name] = None
                continue
            s, e = b
            in_win = [t for t in sym_trades if days[s] < t.date <= days[e]]
            if not in_win and vals[s] == 0 and vals[e] == 0:
                pos["windows"][name] = None
                continue
            a = apr(in_win, vals[s], vals[e])
            if a is None:
                pos["windows"][name] = None
                continue
            active = True
            pos["windows"][name] = {
                "apr": a["apr"], "bench": w["bench"],
                "contribution_pp": a["profit"] / capital_total[name] * 100,
                "underperformer": a["apr"] < w["bench"],
            }
        if active:
            result["positions"].append(pos)

    rw = rank_window(result)
    result["positions"].sort(
        key=lambda p: (0, -p["windows"][rw]["contribution_pp"]) if p["windows"][rw] else (1, 0.0))
    return result
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 scripts/test_perf.py -v`
Expected: 29 tests, `OK`

If `test_contributions_sum_to_total_apr` fails on `6m`/`1y` by more than 1e-9: the per-symbol `vals[s]` sums must equal `total[s]` — they do by construction in `daily_values`; check you did not round anything inside `compute` except `total_value_usd`.

- [ ] **Step 5: Commit**

```bash
git add scripts/perf.py scripts/test_perf.py
git commit -m "perf: compute windows, per-position attribution and underperformer flags"
```

---

### Task 7: Price cache and Yahoo download

**Files:**
- Modify: `scripts/perf.py` (append section `# ---- prices ----`)
- Modify: `scripts/test_perf.py` (append `PriceCacheTests`)

**Interfaces:**
- Consumes: `CACHE_DIR` (Task 1) — functions read the module global at call time so tests can patch it.
- Produces: `load_cache(ysym) -> Dict[date, float]`; `save_cache(ysym, closes) -> None`; `yahoo_download(ysym, start, end) -> Dict[date, float]` (the only place `yfinance` is imported); `get_prices(ysymbols, start, end, fetch=True, downloader=yahoo_download) -> Prices` (symbols with no data are simply absent from the result).

- [ ] **Step 1: Write the failing tests**

Append to `scripts/test_perf.py`:

```python
class PriceCacheTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self._orig = perf.CACHE_DIR
        perf.CACHE_DIR = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)
        self.addCleanup(setattr, perf, "CACHE_DIR", self._orig)

    def test_cache_roundtrip_and_incremental_fetch(self):
        cal = days(4)
        calls = []

        def fake(ysym, start, end):
            calls.append((ysym, start, end))
            return {x: 1.5 for x in cal if start <= x <= end}

        p1 = perf.get_prices(["AAA"], cal[0], cal[1], fetch=True, downloader=fake)
        self.assertEqual(sorted(p1["AAA"]), cal[:2])
        self.assertEqual(perf.load_cache("AAA")[cal[0]], 1.5)
        p2 = perf.get_prices(["AAA"], cal[0], cal[3], fetch=True, downloader=fake)
        self.assertEqual(sorted(p2["AAA"]), cal[:4])
        self.assertEqual(calls[1][1], cal[1] + timedelta(days=1))   # only the tail was fetched
        p3 = perf.get_prices(["AAA", "NOPE"], cal[0], cal[3], fetch=False, downloader=fake)
        self.assertIn("AAA", p3)
        self.assertNotIn("NOPE", p3)
        self.assertEqual(len(calls), 2)

    def test_failed_or_empty_fetch_keeps_cache_and_excludes_unknown(self):
        cal = days(2)
        perf.save_cache("AAA", {cal[0]: 2.0})

        def boom(ysym, start, end):
            if ysym == "AAA":
                raise RuntimeError("network down")
            return {}

        p = perf.get_prices(["AAA", "GONE"], cal[0], cal[1], fetch=True, downloader=boom)
        self.assertEqual(p["AAA"], {cal[0]: 2.0})
        self.assertNotIn("GONE", p)

    def test_up_to_date_cache_is_not_refetched(self):
        cal = days(2)
        perf.save_cache("AAA", {cal[0]: 2.0, cal[1]: 2.5})
        calls = []
        perf.get_prices(["AAA"], cal[0], cal[1], fetch=True,
                        downloader=lambda *a: calls.append(a) or {})
        self.assertEqual(calls, [])
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 scripts/test_perf.py -v`
Expected: `PriceCacheTests` fail with `AttributeError: ... 'get_prices'`

- [ ] **Step 3: Write the implementation**

Append to `scripts/perf.py`:

```python
# ---- prices ----

def load_cache(ysym: str) -> Dict[date, float]:
    p = CACHE_DIR / f"{ysym}.csv"
    if not p.exists():
        return {}
    with open(p, newline="", encoding="utf-8") as f:
        return {date.fromisoformat(r["date"]): float(r["close"]) for r in csv.DictReader(f)}


def save_cache(ysym: str, closes: Dict[date, float]) -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    with open(CACHE_DIR / f"{ysym}.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["date", "close"])
        for d in sorted(closes):
            w.writerow([d.isoformat(), f"{closes[d]:.6f}"])


def yahoo_download(ysym: str, start: date, end: date) -> Dict[date, float]:
    import yfinance as yf  # only import site; keeps tests and --no-fetch dependency-free
    df = yf.download(ysym, start=start.isoformat(), end=(end + timedelta(days=1)).isoformat(),
                     progress=False, auto_adjust=False)
    if df is None or df.empty:
        return {}
    close = df["Close"]
    if hasattr(close, "columns"):          # newer yfinance returns MultiIndex columns
        close = close.iloc[:, 0]
    return {idx.date(): float(v) for idx, v in close.dropna().items()}


def get_prices(ysymbols, start: date, end: date, fetch: bool = True,
               downloader=yahoo_download) -> Prices:
    prices: Prices = {}
    for ysym in ysymbols:
        closes = load_cache(ysym)
        if fetch:
            since = max(closes) + timedelta(days=1) if closes else start
            if since <= end:
                try:
                    new = downloader(ysym, since, end)
                except Exception as exc:  # network / yfinance failure → keep what we have
                    print(f"warning: fetch failed for {ysym}: {exc}", file=sys.stderr)
                    new = {}
                if new:
                    closes.update(new)
                    save_cache(ysym, closes)
        if closes:
            prices[ysym] = closes
    return prices
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 scripts/test_perf.py -v`
Expected: 32 tests, `OK`

- [ ] **Step 5: Commit**

```bash
git add scripts/perf.py scripts/test_perf.py
git commit -m "perf: per-symbol price cache with incremental Yahoo Finance download"
```

---

### Task 8: Report, atomic outputs, CLI

**Files:**
- Modify: `scripts/perf.py` (append sections `# ---- report ----` and `# ---- main ----`)
- Modify: `scripts/test_perf.py` (append `OutputTests`)

**Interfaces:**
- Consumes: `compute`, `rank_window` (Task 6), `get_prices`, `load_trades`, `yahoo_symbol`, constants.
- Produces: `render_report(result) -> str`; `write_json_atomic(path, data) -> None`; `main(argv=None) -> int` (exit code).

- [ ] **Step 1: Write the failing tests**

Append to `scripts/test_perf.py`:

```python
class OutputTests(unittest.TestCase):
    def _result(self):
        cal = days(300)
        n = len(cal)
        prices = {perf.BENCH: series(cal, [100 + i * 0.1 for i in range(n)]),
                  "AAA": series(cal, [10 + i * 0.05 for i in range(n)]),
                  "BBB": series(cal, [50 - i * 0.05 for i in range(n)])}
        trades = [Trade("AAA", cal[1], 10, 10.05, 0), Trade("BBB", cal[1], 2, 49.95, 0)]
        return perf.compute(trades, prices, cal[-1], excluded=["ZZZ"])

    def test_report_contents(self):
        rep = perf.render_report(self._result())
        self.assertIn("Excluded (no price data): ZZZ", rep)
        self.assertIn("insufficient history", rep)          # 5y
        self.assertRegex(rep, r"inception .*(BEAT|BEHIND)")
        self.assertIn("UNDERPERFORM", rep)                    # BBB
        self.assertIn("no-brief", rep)                        # AAA/BBB have no briefs
        self.assertIn("Holdings check", rep)
        self.assertTrue(rep.endswith("\n"))

    def test_json_is_written_atomically(self):
        r = self._result()
        with tempfile.TemporaryDirectory() as d:
            out = Path(d) / "portfolio.json"
            perf.write_json_atomic(out, r)
            self.assertEqual(json.loads(out.read_text())["as_of"], r["as_of"])
            self.assertEqual([p.name for p in Path(d).iterdir()], ["portfolio.json"])

    def test_main_reports_missing_file(self):
        self.assertEqual(perf.main(["--transactions", "/nonexistent/none.csv", "--no-fetch"]), 1)

    def test_main_reports_bad_row(self):
        with tempfile.TemporaryDirectory() as d:
            p = write_csv(d, HEADER + "AAPL,2025 01 15,0,10,0\n")
            self.assertEqual(perf.main(["--transactions", str(p), "--no-fetch"]), 1)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 scripts/test_perf.py -v`
Expected: `OutputTests` fail with `AttributeError: ... 'render_report'`

- [ ] **Step 3: Write the implementation**

Append to `scripts/perf.py`:

```python
# ---- report ----

def _pct(x: Optional[float]) -> str:
    return "n/a" if x is None else f"{x * 100:+.1f}%"


def _pp(x: Optional[float]) -> str:
    return "n/a" if x is None else f"{x:+.1f}pp"


def render_report(r: dict) -> str:
    lines = [f"Portfolio APR vs S&P 500 TR — as of {r['as_of']}"]
    if r["excluded_symbols"]:
        lines.append("Excluded (no price data): " + ", ".join(r["excluded_symbols"]))
    lines += ["", f"{'Window':<10}{'APR':>9}{'S&P TR':>9}{'Alpha':>9}{'TWR':>9}  Verdict"]
    for name in WINDOWS:
        w = r["windows"][name]
        if w is None:
            lines.append(f"{name:<10} insufficient history")
            continue
        verdict = "BEAT" if w["beat"] else "BEHIND"
        lines.append(f"{name:<10}{_pct(w['apr']):>9}{_pct(w['bench']):>9}"
                     f"{_pp(w['alpha_pp']):>9}{_pct(w['twr']):>9}  {verdict}")

    rw = rank_window(r)
    lines += ["", f"Positions ({rw} window, ranked by contribution)",
              f"{'Symbol':<8}{'Qty':>11}{'Value':>10}{'Weight':>8}{'APR':>9}{'vs S&P':>9}{'Contrib':>9}  Flag"]
    for p in r["positions"]:
        w = p["windows"].get(rw)
        flags = []
        if w and w["underperformer"]:
            flags.append("UNDERPERFORM")
        if p["brief"] is None:
            flags.append("no-brief")
        base = f"{p['symbol']:<8}{p['qty']:>11.4f}{p['value_usd']:>10,.0f}{p['weight'] * 100:>7.1f}%"
        if w is None:
            lines.append(f"{base}{'n/a':>9}{'':>9}{'':>9}  {' '.join(flags)}".rstrip())
        else:
            lines.append(f"{base}{_pct(w['apr']):>9}{_pp((w['apr'] - w['bench']) * 100):>9}"
                         f"{_pp(w['contribution_pp']):>9}  {' '.join(flags)}".rstrip())

    lines += ["", "Holdings check (compare to the Dime! app)",
              f"{'Symbol':<8}{'Qty':>11}{'Avg cost':>10}{'Last close':>11}"]
    for p in r["positions"]:
        if abs(p["qty"]) < 1e-9:
            continue
        lines.append(f"{p['symbol']:<8}{p['qty']:>11.4f}{(p['avg_cost'] or 0):>10.2f}"
                     f"{(p['last_close'] or 0):>11.2f}")
    return "\n".join(lines) + "\n"


def write_json_atomic(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=".tmp-", suffix=".json")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    os.replace(tmp, path)


# ---- main ----

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Portfolio APR vs S&P 500 TR")
    ap.add_argument("--transactions", type=Path, default=DEFAULT_TRANSACTIONS)
    ap.add_argument("--as-of", type=date.fromisoformat, default=date.today())
    ap.add_argument("--no-fetch", action="store_true", help="use the price cache only")
    args = ap.parse_args(argv)

    try:
        trades = load_trades(args.transactions)
    except (OSError, ValueError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    if not trades:
        print("error: no trades in file", file=sys.stderr)
        return 1
    if not args.no_fetch:
        try:
            import yfinance  # noqa: F401
        except ImportError:
            print("error: yfinance not installed. Run: python3 -m pip install yfinance", file=sys.stderr)
            return 1

    ysyms = sorted({yahoo_symbol(t.symbol) for t in trades}) + [BENCH]
    prices = get_prices(ysyms, trades[0].date - timedelta(days=7), args.as_of, fetch=not args.no_fetch)
    if BENCH not in prices:
        print(f"error: no price data for {BENCH}; cannot compute the benchmark", file=sys.stderr)
        return 1
    excluded = sorted({t.symbol for t in trades if yahoo_symbol(t.symbol) not in prices})
    trades = [t for t in trades if yahoo_symbol(t.symbol) in prices]
    if not trades:
        print("error: no symbol could be priced", file=sys.stderr)
        return 1

    result = compute(trades, prices, args.as_of, excluded=excluded)
    report = render_report(result)
    print(report, end="")
    PORTFOLIO_DIR.mkdir(parents=True, exist_ok=True)
    (PORTFOLIO_DIR / "report.md").write_text(report, encoding="utf-8")
    write_json_atomic(PORTFOLIO_DIR / "portfolio.json", result)
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 scripts/test_perf.py -v`
Expected: 36 tests, `OK`

- [ ] **Step 5: Commit**

```bash
git add scripts/perf.py scripts/test_perf.py
git commit -m "perf: report rendering, atomic JSON output and CLI"
```

---

### Task 9: Integration — ignore rules, trading-desk path, first real run

**Files:**
- Modify: `.graphifyignore` (currently empty)
- Modify: `.claude/skills/trading-desk/SKILL.md` (steps 4–5)
- Runs: `scripts/perf.py` against the owner's real file (output stays under `portfolio/`, never committed)

**Interfaces:**
- Consumes: `portfolio/portfolio.json` shape from Task 6 (the trading-desk skill only needs to know the path).

- [ ] **Step 1: Add `portfolio/` to `.graphifyignore`**

Write `.graphifyignore` so it contains exactly:

```
portfolio/
```

Verify: `cat .graphifyignore` prints `portfolio/`.

- [ ] **Step 2: Point trading-desk at the new file**

In `.claude/skills/trading-desk/SKILL.md`, replace the step 4 line

```
4. **Check for `portfolio.json`** at project root. It almost certainly won't exist — that's fine, note it in step 6 rather than fabricating position sizes.
```

with

```
4. **Check for `portfolio/portfolio.json`** (written by `python3 scripts/perf.py`). If it is missing, note that in step 6 rather than fabricating position sizes. If present, pass the matching entry from its `positions` array (weight, value_usd, per-window `apr`/`underperformer`) to the risk_manager agent.
```

and in step 5, replace `If no \`portfolio.json\` exists` with `If no \`portfolio/portfolio.json\` exists`. Verify with `grep -n "portfolio" .claude/skills/trading-desk/SKILL.md` — every mention should now say `portfolio/portfolio.json`.

- [ ] **Step 3: Install the one dependency and run the tests one more time**

```bash
python3 -m pip install yfinance
python3 scripts/test_perf.py -v
```

Expected: install succeeds; 36 tests `OK` (tests never import yfinance, so this only proves nothing broke).

- [ ] **Step 4: First real run**

```bash
python3 scripts/perf.py
```

Expected: the report prints; `portfolio/report.md`, `portfolio/portfolio.json`, and `portfolio/cache/*.csv` now exist. If a symbol appears under "Excluded (no price data)", that is expected for delisted tickers (the design anticipates `DIPS`). If `^SP500TR` fails, retry once with `python3 scripts/perf.py` — Yahoo occasionally rate-limits — and if it still fails, report that to the owner instead of changing the benchmark.

Then confirm privacy: `git status --short` must show **no** `portfolio/` paths (it is gitignored) — only `.graphifyignore` and the SKILL.md as modified.

- [ ] **Step 5: Ask the owner to reconcile**

Show the owner only the **Holdings check** section of the printed report and ask them to compare the `Qty` column against the Dime! app. Do not paste holdings into any file or commit. The report already lives in `portfolio/report.md` for their reference.

- [ ] **Step 6: Commit the tracked changes only**

```bash
git add .graphifyignore .claude/skills/trading-desk/SKILL.md
git commit -m "Keep portfolio data out of the knowledge graph; trading-desk reads portfolio/portfolio.json"
```

Note: `.claude/` is in `.gitignore`; if `git add` reports the SKILL.md path is ignored, commit `.graphifyignore` alone and leave the SKILL.md change uncommitted — that is the existing repo convention for `.claude/` files.

---

## Self-review (done at planning time)

**Spec coverage:** §3 loader/validation → Task 1. §5.1 calendar, carry-forward, exclusion → Tasks 2, 3, 7, 8 (`main` excludes unpriced symbols). §5.2 daily state → Task 3. §5.3 windows → Task 2. §5.4 APR → Task 4. §5.5 attribution/underperformer/ranking → Task 6. §5.6 TWR → Task 5. §6 CLI → Task 8. §7 report and JSON shape (incl. `brief`, `null` windows, exited positions, atomic write) → Tasks 6, 8. §8 errors → Task 8 (`main`) and Task 7 (fetch failure). §9 tests 1–8 → AprTests (1–4), ComputeTests (5, 7), TwrTests (6), LoadTests (8). §10 privacy → Global Constraints + Task 9 steps 1, 4, 6. §4 trading-desk path → Task 9 step 2.

**Type consistency:** `Prices` is `Dict[str, Dict[date, float]]` everywhere; `daily_values` returns `Dict[str, List[float]]` with `"__total__"`; `window_bounds` returns index pairs consumed by `compute`; `apr` takes `(trades, v0, v1)` and returns the dict `compute` reads `profit`/`capital`/`apr` from; `twr` takes `(total, flows, s, e)` exactly as `compute` calls it; `get_prices(..., downloader=)` matches both the test fakes and `yahoo_download`'s signature.

**Placeholders:** none. Every code step is complete.
