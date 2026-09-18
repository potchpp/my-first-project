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
