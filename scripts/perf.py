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
