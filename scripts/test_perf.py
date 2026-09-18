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


if __name__ == "__main__":
    unittest.main()
