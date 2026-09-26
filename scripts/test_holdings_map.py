import sys
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
        self.assertEqual(set(v['held']['NVDA']), {'w', 'apr', 'bench', 'under', 'gain'})
        self.assertEqual(v['held']['NVDA']['gain'], 0.5)  # a ratio, never the cost itself
        self.assertNotIn('12345', str(v))
        self.assertNotIn('100.0', str(v['held']))



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


if __name__ == '__main__':
    unittest.main()
