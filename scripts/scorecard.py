"""Verdict scorecard: were the verdicts right? Two independent checks.

1. Falsifier results (the real test). When a falsifier's deadline passes and the company reports, record the number:
     python3 scripts/scorecard.py --record MU 46.3 --note "FQ4 revenue, 10-K line 412"
     python3 scripts/scorecard.py --record RKLB happened|not      # event falsifiers
   It reads the falsifier from briefs/monitor.json and the verdict from the ledger, decides whether the verdict held
   (the line was NOT crossed), and appends to briefs/outcomes.jsonl. Record BEFORE /deep rewrites the falsifier.

2. Market check (noisier, needs no reporting). For each ledger entry with a price, after 6 and 12 months compare the
   stock's return with the S&P 500 total return: "Ahead of itself" is right if it lagged, "Still underrated" if it led,
   "Deserved" if it stayed within 10 points.

  python3 scripts/scorecard.py            # print the scorecard
  python3 scripts/scorecard.py --write    # also save briefs/scorecard.md (tracked: verdicts and public prices only)
"""
import json
import sys
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import holdings_map as hm  # noqa: E402
import perf  # noqa: E402
import verdict_ledger as vl  # noqa: E402

OUTCOMES = hm.ROOT / 'briefs' / 'outcomes.jsonl'
REPORT = hm.ROOT / 'briefs' / 'scorecard.md'
HORIZONS = (182, 365)
DESERVED_BAND = 0.10  # "Deserved" means priced about right: within 10 points of the market
VERDICTS = ('Ahead of itself', 'Deserved', 'Still underrated')


def held(f, value):
    """True if the verdict survived: the falsifying line was not crossed (or the event did not happen)."""
    if f['type'] == 'event':
        return value != 'happened'
    return not (value < f['threshold'] if f['breaks'] == 'below' else value > f['threshold'])


def market_right(verdict, excess):
    return {'Ahead of itself': excess < 0, 'Still underrated': excess > 0,
            'Deserved': abs(excess) <= DESERVED_BAND}.get(verdict)


def load_outcomes():
    return [json.loads(l) for l in OUTCOMES.read_text(encoding='utf-8').splitlines() if l.strip()] \
        if OUTCOMES.exists() else []


def record(ticker, raw, note=''):
    f = (json.loads(hm.MONITOR.read_text(encoding='utf-8')).get(ticker) or {}).get('falsifier')
    if not f:
        sys.exit(f'{ticker}: no falsifier in briefs/monitor.json')
    if f['type'] == 'event':
        if raw not in ('happened', 'not'):
            sys.exit('event falsifier: record "happened" or "not"')
        value = raw
    else:
        value = float(raw)
    prev = vl.last(vl.load(), ticker)
    verdict = prev['verdict'] if prev else hm.brief_meta().get(ticker, {}).get('verdict')
    entry = {'ticker': ticker, 'verdict': verdict, 'metric': f['metric'], 'type': f['type'],
             'breaks': f.get('breaks'), 'threshold': f.get('threshold'), 'unit': f.get('unit', ''),
             'deadline': f.get('deadline'), 'value': value, 'held': held(f, value),
             'recorded': date.today().isoformat(), 'note': note}
    with OUTCOMES.open('a', encoding='utf-8') as out:
        out.write(json.dumps(entry, ensure_ascii=False) + '\n')
    print(f"{ticker}: verdict '{verdict}' {'HELD' if entry['held'] else 'BROKEN'} "
          f"({f['metric']}: {value}{entry['unit']} vs line {f.get('breaks', '')} {f.get('threshold', '')})")
    print('Next: set the new falsifier in briefs/monitor.json (the /deep run that follows does this).')


def close_on(series, d):
    """Last close on or before d, from {date: close}."""
    days = [x for x in series if x <= d]
    return series[max(days)] if days else None


def market_checks(entries, today, prices):
    """([(ticker, verdict, horizon, excess, right)], first date a pending check comes due).
    `prices` maps ticker -> {date: close} and 'BENCH' -> the S&P 500 total return series."""
    done, pending = [], []
    for e in entries:
        if not e.get('price') or e.get('verdict') not in VERDICTS:
            continue
        start = date.fromisoformat(e['logged'])
        for h in HORIZONS:
            end = start + timedelta(days=h)
            if end > today:
                pending.append(end)
                continue
            p, b = prices.get(e['ticker'], {}), prices.get('BENCH', {})
            p0, p1, b0, b1 = close_on(p, start), close_on(p, end), close_on(b, start), close_on(b, end)
            if None in (p0, p1, b0, b1):
                continue
            excess = (p1 / p0 - 1) - (b1 / b0 - 1)
            done.append((e['ticker'], e['verdict'], h, excess, market_right(e['verdict'], excess)))
    return done, (min(pending) if pending else None)


def cached_prices(tickers, since):
    """Closes from portfolio/cache (shared with perf.py and the map); no network."""
    ysym = {t: perf.yahoo_symbol({'BRKB': 'BRK.B'}.get(t, t)) for t in tickers}
    raw = perf.get_prices(set(ysym.values()) | {perf.BENCH}, since, date.today(), fetch=False)
    return {**{t: raw.get(y, {}) for t, y in ysym.items()}, 'BENCH': raw.get(perf.BENCH, {})}


def report(today):
    outcomes = load_outcomes()
    lines = ['# Verdict scorecard', f'*Generated {today.isoformat()} by `scripts/scorecard.py`.*', '',
             '## Falsifier results', '']
    if outcomes:
        lines += ['| Verdict | Resolved | Held | Broken | Held rate |', '|---|---|---|---|---|']
        for v in VERDICTS:
            rs = [o for o in outcomes if o['verdict'] == v]
            if rs:
                h = sum(o['held'] for o in rs)
                lines.append(f'| {v} | {len(rs)} | {h} | {len(rs) - h} | {h / len(rs):.0%} |')
        lines += ['', '| Ticker | Verdict | Metric | Result | Line | Outcome |', '|---|---|---|---|---|---|']
        for o in outcomes:
            line = 'event' if o['type'] == 'event' else f"{o['breaks']} {o['threshold']}{o['unit']}"
            lines.append(f"| {o['ticker']} | {o['verdict']} | {o['metric']} | {o['value']}{o['unit']} | {line} | "
                         f"{'held' if o['held'] else '**broken**'} |")
    else:
        lines.append('No falsifier results recorded yet.')
    mon = hm.monitor(sorted(hm.brief_meta()), {}, today)
    recorded = {(o['ticker'], o['deadline']) for o in outcomes}
    overdue = sorted((f['deadline'], t) for t, m in mon.items() for f in [m.get('falsifier') or {}]
                     if f.get('days') is not None and f['days'] < 0 and (t, f['deadline']) not in recorded)
    upcoming = sorted((f['deadline'], t, f['metric']) for t, m in mon.items() for f in [m.get('falsifier') or {}]
                      if f.get('days') is not None and f['days'] >= 0)[:8]
    lines += ['', '## Results due (deadline passed, nothing recorded)', '']
    lines += [f'- {t}: due since {d}' for d, t in overdue] or ['- none']
    lines += ['', '## Next falsifier dates', '']
    lines += [f'- {d} · {t}: {m}' for d, t, m in upcoming] or ['- none']
    entries = vl.load()
    priced = [e for e in entries if e.get('price')]
    since = min((date.fromisoformat(e['logged']) for e in priced), default=today) - timedelta(days=7)
    prices = cached_prices(sorted({e['ticker'] for e in priced}), since) if priced else {}
    done, first = market_checks(entries, today, prices)
    lines += ['', '## Market check (vs S&P 500 total return)', '']
    if done:
        lines += ['| Verdict | Horizon | Checked | Right | Hit rate |', '|---|---|---|---|---|']
        groups = defaultdict(list)
        for _, v, h, _, ok in done:
            groups[(v, h)].append(ok)
        for (v, h), oks in sorted(groups.items()):
            lines.append(f'| {v} | {h} days | {len(oks)} | {sum(oks)} | {sum(oks) / len(oks):.0%} |')
    else:
        lines.append(f'No verdict is old enough yet. First 6-month checks: {first.isoformat() if first else "n/a"}.')
    lines += ['', '*A falsifier result is the real test of a verdict. The market check is noisy over 6–12 months '
              'and says nothing about the business; read it as calibration, not proof.*']
    return '\n'.join(lines) + '\n'


def main():
    args = sys.argv[1:]
    if args[:1] == ['--record']:
        note = args[args.index('--note') + 1] if '--note' in args else ''
        record(args[1].upper(), args[2], note)
        REPORT.write_text(report(date.today()), encoding='utf-8')  # keep the tracked scorecard current
        return
    text = report(date.today())
    print(text)
    if '--write' in args:
        REPORT.write_text(text, encoding='utf-8')


if __name__ == '__main__':
    main()
