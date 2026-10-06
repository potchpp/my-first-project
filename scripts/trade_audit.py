"""Trade audit: did each open, add, trim and exit beat the S&P 500 over the next 3 months?

For every trade, the stock's forward return is compared with ^SP500TR over the same trading days. A buy helped when
the stock then beat the index; a sell helped when the stock then lagged it. Impact = trade $ x (stock - index)
forward return, + for buys and - for sells, shown as % of today's book: the same frame as the KPI (your money vs the
same money in the S&P). Context = the stock's move against the index over the month before the trade.

  python3 scripts/trade_audit.py              # summary here, every trade in portfolio/trade-audit.md (private)
  python3 scripts/trade_audit.py --days 126   # 6-month horizon instead of 3

Reads the trade file and the price cache only (run perf.py first to refresh prices). Never writes outside portfolio/.
"""
import sys
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import perf  # noqa: E402

HORIZON = 63    # trading days after the trade, about 3 months
LOOKBACK = 21   # trading days before the trade, about a month
MOVE = 0.05     # a 5% move against the index in that month counts as "after a drop" / "after a rise"
REPORT = perf.PORTFOLIO_DIR / 'trade-audit.md'


def audit(trades, prices, horizon=HORIZON):
    """One row per trade: kind, context, and (when `horizon` days have passed) the forward edge and its impact."""
    days = sorted(prices[perf.BENCH])
    pos = {d: i for i, d in enumerate(days)}
    bench = prices[perf.BENCH]
    held, rows = defaultdict(float), []
    for t in perf.align_trades(trades, days):
        closes = prices[perf.yahoo_symbol(t.symbol)]
        px = lambda j: perf.last_close(closes, days[j])
        i, before = pos[t.date], held[t.symbol]
        held[t.symbol] += t.qty
        if t.is_sell:
            kind = 'exit' if abs(held[t.symbol]) < 1e-6 else 'trim'
        else:
            kind = 'open' if abs(before) < 1e-6 else 'add'
        p0, row = px(i), {'symbol': t.symbol, 'date': t.date, 'kind': kind, 'cash': t.cash, 'context': None}
        if i >= LOOKBACK and p0 and px(i - LOOKBACK):
            rel = p0 / px(i - LOOKBACK) - bench[days[i]] / bench[days[i - LOOKBACK]]
            row['context'] = 'after a drop' if rel <= -MOVE else 'after a rise' if rel >= MOVE else 'flat'
        if p0 and i + horizon < len(days):
            j = i + horizon
            stock, index = px(j) / p0 - 1, bench[days[j]] / bench[days[i]] - 1
            sign = -1 if t.is_sell else 1
            row.update(stock=stock, index=index, helped=sign * (stock - index) > 0,
                       impact=sign * t.cash * (stock - index))
        rows.append(row)
    return rows


def summarise(rows, key, book):
    """Groups by `key`: trades judged, share that helped, and impact as % of the book."""
    out = defaultdict(lambda: {'n': 0, 'judged': 0, 'helped': 0, 'impact': 0.0})
    for r in rows:
        g = out[key(r)]
        g['n'] += 1
        if 'impact' in r:
            g['judged'] += 1
            g['helped'] += r['helped']
            g['impact'] += r['impact']
    return {k: {**v, 'hit': v['helped'] / v['judged'] if v['judged'] else None, 'pct': v['impact'] / book * 100}
            for k, v in out.items()}


ADD_MIN, ADD_HIT = 4, 0.25  # the map flags a stock after this many judged adds with fewer than this share beating the index


def add_record(rows, since, book):
    """Adds since `since` that can be judged: per stock and in total, [judged, beat the index, impact % of book]."""
    per = defaultdict(lambda: [0, 0, 0.0])
    for r in rows:
        if r['kind'] == 'add' and r['date'] >= since and 'impact' in r:
            p = per[r['symbol'].replace('.', '').replace('-', '')]  # BRK-B -> BRKB, the brief's name
            p[0], p[1], p[2] = p[0] + 1, p[1] + r['helped'], p[2] + r['impact']
    out = lambda p: [p[0], p[1], round(p[2] / book * 100, 2)]
    return {t: out(p) for t, p in per.items()}, out([sum(p[i] for p in per.values()) for i in range(3)])


def stock_rows(rows, since, book):
    """The judged trades since `since`, per stock, newest first, as the map shows them for checking:
    [date, kind, month before, stock return, S&P return, helped (1/0), impact % of book]."""
    per = defaultdict(list)
    for r in sorted(rows, key=lambda r: r['date'], reverse=True):
        if r['date'] >= since and 'impact' in r:
            per[r['symbol'].replace('.', '').replace('-', '')].append(
                [r['date'].isoformat(), r['kind'], r['context'], round(r['stock'], 4), round(r['index'], 4),
                 int(r['helped']), round(r['impact'] / book * 100, 3)])
    return dict(per)


def load():
    """Trades that can be priced, the cached prices, and today's book value. No network."""
    trades = perf.load_trades(perf.DEFAULT_TRANSACTIONS)
    prices = perf.get_prices(sorted({perf.yahoo_symbol(t.symbol) for t in trades}) + [perf.BENCH],
                             trades[0].date - timedelta(days=60), date.today(), fetch=False)
    trades = [t for t in trades if perf.yahoo_symbol(t.symbol) in prices]
    days = sorted(prices[perf.BENCH])
    return trades, prices, perf.daily_values(perf.align_trades(trades, days), prices, days)['__total__'][-1]


def pc(x):
    return '—' if x is None else f'{x * 100:.0f}%'


def table(title, groups, order=None):
    keys = order or sorted(groups, key=lambda k: groups[k]['pct'])
    lines = [f'### {title}', '', '| | Trades | Judged | Helped | Impact, % of book |', '|---|---|---|---|---|']
    lines += [f"| {k} | {groups[k]['n']} | {groups[k]['judged']} | {pc(groups[k]['hit'])} | {groups[k]['pct']:+.2f} |"
              for k in keys if k in groups]
    return '\n'.join(lines) + '\n'


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    horizon = int(argv[argv.index('--days') + 1]) if '--days' in argv else HORIZON
    trades, prices, book = load()
    rows = audit(trades, prices, horizon)
    recent = [r for r in rows if r['date'] >= date.today() - timedelta(days=730)]
    kinds = ['open', 'add', 'trim', 'exit']
    by_move = lambda r: f"{r['kind']} {r['context'] or '(no prior month)'}"
    judged = [r for r in rows if 'impact' in r]
    out = [f'# Trade audit · {horizon} trading days after each trade vs the S&P 500 TR',
           f'*Generated {date.today()} by scripts/trade_audit.py. Private: lives in portfolio/, never commit.*', '',
           'Helped = a buy then beat the index, or a sell then lagged it. Impact = trade $ x (stock − index) over the',
           "horizon, + for buys and − for sells, as % of today's book. Trades too recent to judge are counted but not scored.", '',
           table('Since you started, by kind', summarise(rows, lambda r: r['kind'], book), kinds),
           table('Last 2 years, by kind', summarise(recent, lambda r: r['kind'], book), kinds),
           table('Last 2 years, by kind and the month before', summarise(recent, by_move, book)),
           table('Last 2 years, by stock (worst first)', summarise(recent, lambda r: r['symbol'], book)),
           '### Every judged trade, worst first', '',
           '| Date | Stock | Kind | Month before | Stock | S&P | Helped | Impact, % of book |', '|---|---|---|---|---|---|---|---|']
    out += [f"| {r['date']} | {r['symbol']} | {r['kind']} | {r['context'] or '—'} | {r['stock'] * 100:+.1f}% | "
            f"{r['index'] * 100:+.1f}% | {'yes' if r['helped'] else 'no'} | {r['impact'] / book * 100:+.2f} |"
            for r in sorted(judged, key=lambda r: r['impact'])]
    REPORT.write_text('\n'.join(out) + '\n', encoding='utf-8')
    k = summarise(recent, lambda r: r['kind'], book)
    print(f"Trade audit ({horizon} trading days), last 2 years: {len(recent)} trades, "
          f"{sum(v['judged'] for v in k.values())} judged")
    for kind in kinds:
        if kind in k:
            v = k[kind]
            print(f"  {kind:5} {v['n']:4} trades  helped {pc(v['hit']):>4}  impact {v['pct']:+.2f}% of book")
    print(f'Full table: {REPORT.relative_to(perf.ROOT)}')


if __name__ == '__main__':
    main()
