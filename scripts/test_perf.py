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


class WindowTests(unittest.TestCase):
    def test_shift_months_clamps_to_month_end(self):
        self.assertEqual(perf.shift_months(date(2026, 8, 31), -6), date(2026, 2, 28))
        self.assertEqual(perf.shift_months(date(2026, 3, 31), -1), date(2026, 2, 28))
        self.assertEqual(perf.shift_months(date(2026, 1, 15), -12), date(2025, 1, 15))

    def test_index_at_or_before(self):
        cal = days(5)                                     # Mon..Fri
        self.assertEqual(perf.index_at_or_before(cal, cal[2]), 2)
        self.assertEqual(perf.index_at_or_before(cal, cal[2] + timedelta(days=1)), 3)
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


if __name__ == "__main__":
    unittest.main()
