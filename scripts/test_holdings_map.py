import sys
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import holdings_map as hm  # noqa: E402

# Newer /deep format: bold Bull/Bear headers with bullets, Valuation section, tagged kill conditions.
NEW_FORMAT = """---
ticker: ABC
company: Abc Corp
updated: 2026-09-26
shared_driver: ai-capex
---

# ABC — Abc Corp

## Company Snapshot

Abc makes widgets for [[NVDA]] *(fundamentals agent, 10-K l.12)*

## Bull / Bear

**Bull** *(bull_researcher)*
- **Scale economies:** unit cost falls as volume grows *(earnings agent)*
- second bull point

**Bear** *(bear_researcher)*
- top customer is 40% of revenue

## Valuation

**Verdict: Deserved**

**Falsifying number:** revenue growth below 30%

## Kill Conditions

- **Top customer leaves** `[bounded ~40%]`
- **Export ban** `[open-ended]`

*Tightened 2026-09-26: not a condition, must be ignored*

## What to Ask

1. **Who else buys widgets?** and at what price
"""

# Older format: "What the company does", inline **Bull:** / **Bear:** lines, no valuation.
OLD_FORMAT = """---
ticker: XYZ
company: Xyz Inc
updated: 2026-06-01
---

## What the company does

Xyz sells soda in 200 countries.

## Bull case / Bear case

**Bull:** pricing power holds margins
**Bear:** volume falls as habits change

## Kill conditions

- volume declines three years running

## What to ask before owning it

1. How much volume comes from zero-sugar?
"""


class SummaryTests(unittest.TestCase):
    def test_new_format_reads_every_section_and_strips_markup(self):
        s = hm.summary(NEW_FORMAT)
        self.assertEqual((s['name'], s['date']), ('Abc Corp', '2026-09-26'))
        self.assertEqual(s['snap'], 'Abc makes widgets for NVDA')
        self.assertEqual(s['bull'], ['Scale economies: unit cost falls as volume grows', 'second bull point'])
        self.assertEqual(s['bear'], ['top customer is 40% of revenue'])
        self.assertEqual(s['kill'], ['Top customer leaves [bounded ~40%]', 'Export ban [open-ended]'])
        self.assertEqual(s['ask'], ['Who else buys widgets? and at what price'])
        self.assertEqual(s['fals'], 'revenue growth below 30%')

    def test_old_format_inline_bull_bear_and_no_valuation(self):
        s = hm.summary(OLD_FORMAT)
        self.assertEqual(s['snap'], 'Xyz sells soda in 200 countries.')
        self.assertEqual(s['bull'], ['pricing power holds margins'])
        self.assertEqual(s['bear'], ['volume falls as habits change'])
        self.assertEqual(s['kill'], ['volume declines three years running'])
        self.assertEqual(s['ask'], ['How much volume comes from zero-sugar?'])
        self.assertEqual(s['fals'], '')

    def test_long_text_is_cut_at_a_word_boundary(self):
        cut = hm.short('word ' * 100, 30)
        self.assertLessEqual(len(cut), 31)
        self.assertTrue(cut.endswith('word…'))

    def test_unreadable_brief_is_skipped_not_fatal(self):
        self.assertEqual(hm.summaries(['NO_SUCH_TICKER']), {})



class PortfolioViewTests(unittest.TestCase):
    PAGE = {'nodes': [{'t': 'NVDA', 'g': 'ai-capex'}, {'t': 'TSM', 'g': 'ai-capex'}, {'t': 'BRKB', 'g': 'diversified-us'}]}
    PORTFOLIO = {'as_of': '2026-09-25', 'positions': [
        {'symbol': 'NVDA', 'weight': 0.2, 'qty': 99, 'value_usd': 12345, 'avg_cost': 100.0, 'last_close': 150.0,
         'windows': {'1y': {'apr': 0.26, 'bench': 0.18, 'underperformer': False}}},
        {'symbol': 'TSM', 'weight': 0.05, 'windows': {'1y': None}},
        {'symbol': 'BRK.B', 'weight': 0.1, 'windows': {}},
        {'symbol': 'SDIV', 'weight': 0.02, 'windows': {}}]}

    def test_driver_exposure_is_share_of_total_assets(self):
        v = hm.portfolio_view(self.PAGE, self.PORTFOLIO, {'us_stock_share_of_total': 0.5, 'driver_cap_pct_total': 10})
        self.assertEqual(v['drivers'], [['ai-capex', 12.5], ['diversified-us', 5.0]])  # (0.2+0.05)*0.5*100
        self.assertEqual(v['cap'], 10)

    def test_dotted_symbol_matches_brief_and_unbriefed_holdings_are_listed(self):
        v = hm.portfolio_view(self.PAGE, self.PORTFOLIO, {})
        self.assertIn('BRKB', v['held'])
        self.assertEqual(v['no_brief'], ['SDIV'])

    def test_chain_splits_the_two_failure_modes(self):
        roles = [('spender', 'Pay', '', ['BRKB']), ('supplier', 'Sell', '', ['NVDA', 'AMD'])]
        held = {'BRKB': {'w': 0.1}, 'NVDA': {'w': 0.2}}
        c = hm.chain_exposure(roles, held, 0.5)
        self.assertEqual((c['cut'], c['demand']), (10.0, 15.0))  # spenders escape a discipline cut
        self.assertEqual(c['roles'][1]['watch'], ['AMD'])

    def test_only_percentages_leave_the_portfolio_file(self):
        v = hm.portfolio_view(self.PAGE, self.PORTFOLIO, {})
        self.assertEqual(set(v['held']['NVDA']), {'w', 'gain', 'g2', 'tm2', 'days2'})
        self.assertEqual(v['held']['NVDA']['gain'], 0.5)  # a ratio, never the cost itself
        self.assertNotIn('12345', str(v))
        self.assertNotIn('100.0', str(v['held']))


    def test_sold_names_explain_the_gap_but_are_not_held(self):
        two = lambda ex, usd: {'2y': {'gap_pp': 1.0, 'timing_pp': -2.0, 'held_days': 700, 'excess_pct_book': ex, 'excess_usd': usd}}
        pf = {'as_of': '2026-09-25', 'windows': {'2y': {'mwr': 0.18, 'shadow_mwr': 0.19, 'gap_pp': -0.6, 'twr_ann': 0.3,
                                                        'timing_pp': -12.0, 'start': '2024-09-25'}}, 'positions': [
            {'symbol': 'NVDA', 'weight': 0.9, 'qty': 5, 'value_usd': 900, 'windows': two(3.0, 30)},
            {'symbol': 'TSM', 'weight': 0.0, 'qty': 0, 'value_usd': 0, 'windows': two(-4.0, -40)},
            {'symbol': 'BRK.B', 'weight': 0.001, 'qty': 1, 'value_usd': 1, 'windows': two(0.1, 1)}]}
        v = hm.portfolio_view(self.PAGE, pf, {'us_stock_share_of_total': 0.5})
        self.assertNotIn('TSM', v['held'])
        self.assertEqual(v['attr'], [['NVDA', 3.0, False], ['small', 0.1, False, 1], ['TSM', -4.0, True]])
        self.assertEqual(v['drv2']['ai-capex'], round(-10 / 900 * 100, 2))  # sold TSM counts against the driver
        self.assertEqual(v['score']['2y']['gap_pp'], -0.6)

    def test_review_point_is_the_gap_about_120_days_back(self):
        with tempfile.TemporaryDirectory() as d:
            h = Path(d) / 'k.jsonl'
            h.write_text('{"date": "2026-05-01", "2y": -2.0}\n{"date": "2026-06-10", "2y": -1.0}\n{"date": "2026-09-30", "2y": -0.5}\n')
            self.assertEqual(hm.review_point('2026-10-01', h), {'date': '2026-05-01', 'gap': -2.0})
            self.assertIsNone(hm.review_point('2026-10-01', Path(d) / 'none.jsonl'))


class RangeTests(unittest.TestCase):
    TODAY = date(2026, 9, 26)

    def closes(self, last_day, n=30):
        return {last_day - timedelta(days=i): 100.0 + i for i in range(n)}  # falls toward today

    def test_low_high_and_latest_close(self):
        r = hm.range_52w(self.closes(self.TODAY - timedelta(days=1)), self.TODAY)
        self.assertEqual((r['lo'], r['hi'], r['last'], r['asof']), (100.0, 129.0, 100.0, '2026-09-25'))

    def test_ignores_closes_older_than_a_year(self):
        closes = {**self.closes(self.TODAY), date(2025, 1, 1): 999.0}
        self.assertEqual(hm.range_52w(closes, self.TODAY)['hi'], 129.0)

    def test_stale_or_thin_history_gives_no_range(self):
        self.assertIsNone(hm.range_52w(self.closes(self.TODAY - timedelta(days=30)), self.TODAY))
        self.assertIsNone(hm.range_52w(self.closes(self.TODAY, n=5), self.TODAY))



class MonitorTests(unittest.TestCase):
    TODAY = date(2026, 9, 26)

    def test_kill_condition_is_checked_on_brief_date_and_goes_stale(self):
        fresh = hm.kill_statuses(['Top customer leaves'], '2026-09-01', [], self.TODAY)[0]
        stale = hm.kill_statuses(['Top customer leaves'], '2026-01-01', [], self.TODAY)[0]
        self.assertEqual((fresh['status'], fresh['checked']), ('intact', '2026-09-01'))
        self.assertEqual(stale['status'], 'review')

    def test_review_entry_overrides_by_text_match(self):
        reviews = [{'match': 'customer', 'status': 'watch', 'checked': '2026-09-20', 'note': 'Q3 order cut'}]
        k = hm.kill_statuses(['Top customer leaves', 'Export ban'], '2026-09-01', reviews, self.TODAY)
        self.assertEqual([x['status'] for x in k], ['watch', 'intact'])
        self.assertEqual(k[0]['note'], 'Q3 order cut')

    def test_falsifier_room_in_both_directions(self):
        below = hm.falsifier_state({'type': 'number', 'breaks': 'below', 'threshold': 35, 'current': 43,
                                    'deadline': '2026-10-31'}, self.TODAY)
        self.assertEqual((below['state'], below['room'], below['days']), ('clear', 0.229, 35))
        above = hm.falsifier_state({'type': 'number', 'breaks': 'above', 'threshold': 15, 'current': 14}, self.TODAY)
        self.assertEqual(above['state'], 'close')
        crossed = hm.falsifier_state({'type': 'number', 'breaks': 'below', 'threshold': 35, 'current': 30}, self.TODAY)
        self.assertEqual(crossed['state'], 'crossed')

    def test_target_judged_at_deadline_is_pending_not_crossed(self):
        f = {'type': 'number', 'breaks': 'below', 'threshold': 3.6, 'current': 1, 'deadline': '2027-02-28',
             'judged': 'at deadline'}
        self.assertEqual(hm.falsifier_state(f, self.TODAY)['state'], 'pending')
        self.assertEqual(hm.falsifier_state(f, date(2027, 3, 15))['state'], 'due')

    def test_event_falsifier_becomes_due_after_deadline(self):
        f = {'type': 'event', 'metric': 'Neutron reaches orbit', 'deadline': '2026-09-01'}
        self.assertEqual(hm.falsifier_state(f, self.TODAY)['state'], 'due')


class MoveTests(unittest.TestCase):
    def test_spike_is_measured_against_the_stocks_own_volatility(self):
        start = date(2026, 1, 1)
        px = [100 * (1.01 if i % 2 else 0.99) ** (i % 2) for i in range(60)] + [100, 104, 108, 112, 116, 120]
        m = hm.recent_move({start + timedelta(days=i): p for i, p in enumerate(px)})
        self.assertAlmostEqual(m['r5'], 0.2, places=4)
        self.assertGreater(m['z5'], hm.SPIKE_SIGMA)

    def test_contributions_sum_to_the_book_move(self):
        c = hm.contributions({'A': 0.6, 'B': 0.4}, {'A': {'r1': 0.10}, 'B': {'r1': -0.05}}, 'r1')
        self.assertAlmostEqual(sum(v for _, v in c['by']), c['book'], places=1)
        self.assertEqual(c['by'][0][0], 'A')
        self.assertGreater(c['book'], 0)


class NeedsDeepTests(unittest.TestCase):
    def test_flags_only_what_needs_a_rerun_and_not_twice(self):
        import needs_deep as nd
        today = date(2026, 9, 30)
        kill = [{'status': 'intact'}]
        monitor = {'AAA': {'falsifier': {'state': 'crossed', 'metric': 'margin'}, 'kills': kill},
                   'BBB': {'falsifier': {'state': 'close', 'metric': 'growth'}, 'kills': kill},   # watch, not a rerun
                   'CCC': {'falsifier': None, 'kills': kill},
                   'DDD': {'falsifier': {'state': 'clear', 'metric': 'x'}, 'kills': kill},
                   'EEE': {'falsifier': {'state': 'due', 'metric': 'ARR', 'deadline': '2026-09-01'}, 'kills': kill}}
        ranges = {'BBB': {'z5': 1.0, 'r5': 0.03}, 'CCC': {'z5': -2.4, 'r5': -0.129}}
        briefs = {t: {'date': '2026-09-26'} for t in monitor} | {'DDD': {'date': '2026-05-01'}}
        found = nd.flags(monitor, ranges, briefs, today)
        self.assertEqual([(t, k) for t, k, _ in found],
                         [('AAA', 'crossed'), ('EEE', 'due'), ('CCC', 'move'), ('DDD', 'stale')])
        self.assertIn('-12.9%', found[2][2])
        seen = {'AAA|crossed': '2026-09-29', 'EEE|due': '2026-09-20'}  # told yesterday / told 10 days ago
        self.assertEqual([t for t, _, _ in nd.unseen(found, seen, today)], ['EEE', 'CCC', 'DDD'])


class NewsSpikeTests(unittest.TestCase):
    class R:  # stub response
        def __init__(self, code, items=0):
            self.status_code, self.text = code, '<item>' * items

    def test_count_and_failures(self):
        import needs_deep as nd
        self.assertEqual(nd.news_count('q', lambda *a, **k: self.R(200, 37)), 37)
        self.assertIsNone(nd.news_count('q', lambda *a, **k: self.R(429)))
        def boom(*a, **k):
            raise OSError('down')
        self.assertIsNone(nd.news_count('q', boom))

    def test_fetch_stops_after_three_misses(self):
        import needs_deep as nd
        calls = []
        def dead(*a, **k):
            calls.append(1)
            return self.R(503)
        self.assertEqual(nd.fetch_counts(['AAPL', 'AMD', 'ASML', 'GOOG', 'META'], dead, pause=0), {})
        self.assertEqual(len(calls), 3)

    def test_spike_rule(self):
        import needs_deep as nd
        hist = {f'2026-09-{d:02}': {'A': 10, 'B': 2, 'C': 40} for d in range(20, 27)}  # 7 prior days
        self.assertEqual(nd.news_spikes(hist, {'A': 35}), {'A': (35, 10)})
        self.assertEqual(nd.news_spikes(hist, {'A': 29}), {})            # under 3x
        self.assertEqual(nd.news_spikes(hist, {'B': 8}), {})             # below the floor of 10
        self.assertEqual(nd.news_spikes(hist, {'C': 100}), {})           # usual 40: can't show 3x under the cap
        short = dict(list(hist.items())[:6])
        self.assertEqual(nd.news_spikes(short, {'A': 50}), {})           # 6 days: not enough history
        gappy = {**hist, '2026-09-27': {'B': 3}}                        # a day without A doesn't count for A
        self.assertEqual(nd.news_spikes(dict(list(gappy.items())[1:]), {'A': 50}), {})

    def test_news_flag_precedence(self):
        import needs_deep as nd
        kill = [{'status': 'intact'}]
        monitor = {t: {'falsifier': None, 'kills': kill} for t in ('AAA', 'BBB')}
        ranges = {'AAA': {'z5': 2.5, 'r5': 0.11}}
        briefs = {t: {'date': '2026-09-26'} for t in monitor}
        news = {'AAA': (40, 10), 'BBB': (30, 8)}
        found = nd.flags(monitor, ranges, briefs, date(2026, 9, 30), news)
        self.assertEqual([(t, k) for t, k, _ in found], [('AAA', 'move'), ('BBB', 'news')])
        self.assertEqual(found[1][2], 'news spike (30 stories vs usual 8)')


class LedgerTests(unittest.TestCase):
    @staticmethod
    def brief(verdict, kills, updated='2026-10-01', extra=''):
        ks = '\n'.join(f'- {k}' for k in kills)
        return (f'---\nupdated: {updated}\n---\n## Valuation\n**Verdict: {verdict}**\n'
                f'**Falsifying number:** margin below 15%\n## Kill Conditions\n{ks}\n{extra}\n## What to Ask\n- q\n')

    def check(self, old, new, move=None):
        import verdict_ledger as vl
        return vl.coherence(vl.snapshot(old), vl.snapshot(new), new, move)

    def test_marks(self):
        k = ['Top customer cuts orders by half `[bounded ~50%]`', 'Regulator bans the product `[open-ended]`']
        base = self.brief('Ahead of itself', k, '2026-09-01')
        self.assertEqual(self.check(base, base)[0], 'accept')
        tightened = self.brief('Ahead of itself', [k[0] + ' within two quarters', k[1]])
        self.assertEqual(self.check(base, tightened)[0], 'accept')                    # tightening keeps the opening
        friendlier = self.brief('Deserved', k)
        self.assertEqual(self.check(base, friendlier)[0], 'ego-check')                # no written reason
        reasoned = self.brief('Deserved', k, extra='*Verdict changed 2026-10-01: margin guide beat the line*')
        self.assertEqual(self.check(base, reasoned)[0], 'watch')
        self.assertEqual(self.check(base, reasoned, move=0.22)[0], 'ego-check')       # right after a +22% run
        harsher = self.brief('Ahead of itself', k[:1] + ['Cash runs out before 2028 `[open-ended]`', k[1]])
        self.assertEqual(self.check(base, harsher)[0], 'watch')                       # added a condition: fine
        dropped = self.brief('Ahead of itself', k[:1])
        self.assertEqual(self.check(base, dropped)[0], 'ego-check')
        old_reason = self.brief('Ahead of itself', k[:1], extra='*Loosened 2026-08-01: stale*')
        self.assertEqual(self.check(base, old_reason)[0], 'ego-check')                # reason predates the last entry
        reworded = self.brief('Ahead of itself', k[:1], extra='*Reworded 2026-10-01: same ban risk, new wording*')
        self.assertEqual(self.check(base, reworded)[0], 'watch')
        legacy = '---\nupdated: 2026-09-18\n---\n## Kill Conditions\n- something vague\n## What to Ask\n'
        self.assertEqual(self.check(legacy, friendlier)[0], 'rebaseline')            # old short format, no verdict


class ScorecardTests(unittest.TestCase):
    def test_held_and_market_check(self):
        import scorecard as sc
        below = {'type': 'number', 'breaks': 'below', 'threshold': 7}
        above = {'type': 'number', 'breaks': 'above', 'threshold': 51.2}
        self.assertTrue(sc.held(below, 7.5))
        self.assertFalse(sc.held(below, 6.9))
        self.assertFalse(sc.held(above, 54.23))          # MU, 2026-09-30: Ahead of itself broken
        self.assertTrue(sc.held({'type': 'event'}, 'not'))
        self.assertFalse(sc.held({'type': 'event'}, 'happened'))
        self.assertTrue(sc.market_right('Ahead of itself', -0.05))
        self.assertFalse(sc.market_right('Still underrated', -0.05))
        self.assertTrue(sc.market_right('Deserved', 0.08))
        self.assertFalse(sc.market_right('Deserved', 0.15))

    def test_market_checks_wait_for_the_horizon(self):
        import scorecard as sc
        d = date(2026, 1, 2)
        series = lambda a, b: {d: a, d + timedelta(days=182): b, d + timedelta(days=365): b}
        prices = {'AAA': series(100, 90), 'BBB': series(100, 130), 'BENCH': series(100, 110)}
        entries = [{'ticker': 'AAA', 'verdict': 'Ahead of itself', 'price': 100, 'logged': d.isoformat()},
                   {'ticker': 'BBB', 'verdict': 'Still underrated', 'price': 100, 'logged': d.isoformat()},
                   {'ticker': 'CCC', 'verdict': 'Deserved', 'price': None, 'logged': d.isoformat()}]  # no price: skipped
        done, first = sc.market_checks(entries, d + timedelta(days=200), prices)
        self.assertEqual([(t, h, ok) for t, _, h, _, ok in done], [('AAA', 182, True), ('BBB', 182, True)])
        self.assertEqual(first, d + timedelta(days=365))     # 12-month checks still pending


if __name__ == '__main__':
    unittest.main()
