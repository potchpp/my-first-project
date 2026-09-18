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


def negative_holdings_symbols(trades: List[Trade]) -> List[str]:
    """Symbols whose running signed quantity ever dips negative (data-quality bug,
    e.g. a duplicated sell row or a missing buy in the export)."""
    qty: Dict[str, float] = defaultdict(float)
    bad = []
    for t in sorted(trades, key=lambda t: t.date):
        qty[t.symbol] += t.qty
        if qty[t.symbol] < -1e-6 and t.symbol not in bad:
            bad.append(t.symbol)
    return sorted(bad)


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


def twr(total: List[float], flows: Dict[int, float], s: int, e: int) -> Optional[float]:
    growth, any_day = 1.0, False
    for i in range(s + 1, e + 1):
        prev = total[i - 1]
        if prev <= 1e-9:
            continue
        growth *= (total[i] - flows.get(i, 0.0)) / prev
        any_day = True
    return growth - 1 if any_day else None


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
            since = max(closes) if closes else start
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

    try:
        result = compute(trades, prices, args.as_of, excluded=excluded)
    except (ValueError, TypeError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    report = render_report(result)
    neg = negative_holdings_symbols(trades)
    if neg:
        report += f"Negative holdings detected (check the export): {', '.join(neg)}\n"
    print(report, end="")
    PORTFOLIO_DIR.mkdir(parents=True, exist_ok=True)
    (PORTFOLIO_DIR / "report.md").write_text(report, encoding="utf-8")
    write_json_atomic(PORTFOLIO_DIR / "portfolio.json", result)
    return 0


if __name__ == "__main__":
    sys.exit(main())
