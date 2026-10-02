"""Verdict ledger: an append-only history of every brief's verdict, falsifier and kill conditions, so a change of
mind leaves a trail and the "ego pattern" gets caught instead of remembered.

Each entry is compared with the ticker's previous one and marked:
  accept     nothing material changed
  watch      verdict, falsifier or kill conditions changed, with a written reason in the brief
  rebaseline the previous version was the old short format (no verdict): a full rewrite, not a loosening. The kill
             conditions it no longer carries are listed once for review.
  ego-check  the view got friendlier (verdict up, kill condition dropped) with no written reason, or right after a
             big price rise. The brief needs a "*Verdict changed YYYY-MM-DD: ... because ...*" or
             "*Loosened YYYY-MM-DD: ...*" line ("*Reworded YYYY-MM-DD: ...*" if a condition was only re-phrased).

  python3 scripts/verdict_ledger.py TICKER     # log the current brief, print the coherence check (exit 2 = ego-check)
  python3 scripts/verdict_ledger.py --seed     # first run: backfill every brief from git history, then today
  python3 scripts/verdict_ledger.py --history TICKER

briefs/ledger.jsonl is tracked: it holds only what the public briefs already say (no positions, no cost basis).
"""
import difflib
import json
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import holdings_map as hm  # noqa: E402

LEDGER = hm.ROOT / 'briefs' / 'ledger.jsonl'
RANK = {'Ahead of itself': 0, 'Deserved': 1, 'Still underrated': 2}  # higher = friendlier to the stock
PRICE_RUN = 0.15  # a friendlier verdict after the price rose this much since the last entry gets a second look


def snapshot(text):
    """The parts of a brief that make up the decision."""
    secs = hm.sections(text)
    kills = [hm.clean(m.group(1)) for m in re.finditer(r'^\s*(?:-|\d+\.)\s+(.+)', hm.section(secs, 'kill'), re.M)]
    ver = re.search(r'Verdict[^A-Za-z\n]*(Ahead of itself|Deserved|Still underrated)', text)
    fals = re.search(r'Falsifying number:?\**\s*(.+)', text)
    return {'date': hm.frontmatter(text, 'updated'), 'verdict': ver.group(1) if ver else None,
            'falsifier': hm.clean(fals.group(1)) if fals else '', 'kills': kills}


def reasons(text, since):
    """Dated '*Verdict changed …' and '*Loosened …' lines written on or after `since`."""
    found = re.findall(r'\*(Verdict changed|Loosened|Reworded)\s+(\d{4}-\d{2}-\d{2})', text)
    out = {kind for kind, d in found if d >= (since or '')}
    return out | ({'Loosened'} if 'Reworded' in out else set())  # a re-phrased condition is not a dropped one


def kept(old, new_kills):
    """A prior kill condition survives if a new one starts the same way or reads mostly the same (tightening
    usually appends to the wording, so the opening survives)."""
    norm = lambda s: ' '.join(re.sub(r'\[(?:bounded|open-ended)[^\]]*\]', '', s).lower().split())  # tags move around
    old, head = norm(old), norm(old)[:40]
    return any(norm(k).startswith(head) or difflib.SequenceMatcher(None, old, norm(k)).ratio() > 0.6
               for k in new_kills)


def coherence(prev, cur, text, price_move=None):
    """(mark, notes) for cur against prev."""
    if prev is None:
        return 'accept', ['first entry']
    notes, friendlier = [], False
    written = reasons(text, prev.get('date'))
    a, b = RANK.get(prev['verdict']), RANK.get(cur['verdict'])
    if prev['verdict'] != cur['verdict']:
        notes.append(f"verdict {prev['verdict']} -> {cur['verdict']}")
        friendlier |= a is not None and b is not None and b > a
    dropped = [k for k in prev['kills'] if not kept(k, cur['kills'])]
    if dropped:
        notes.append(f'{len(dropped)} kill condition(s) gone: ' + '; '.join(k[:70] for k in dropped))
        friendlier = True
    added = [k for k in cur['kills'] if not kept(k, prev['kills'])]
    if added:
        notes.append(f'{len(added)} kill condition(s) added')  # tightening: allowed freely, still worth a trail
    if prev['falsifier'] != cur['falsifier']:
        notes.append('falsifier reworded')
    if not notes:
        return 'accept', []
    if prev['verdict'] is None:
        return 'rebaseline', notes
    missing = [w for w, need in (('Verdict changed', b is not None and a is not None and b > a),
                                 ('Loosened', bool(dropped))) if need and w not in written]
    if missing:
        return 'ego-check', notes + [f'no "*{w} {cur["date"]}: …*" line in the brief' for w in missing]
    if friendlier and price_move is not None and price_move >= PRICE_RUN:
        return 'ego-check', notes + [f'friendlier view right after a {price_move:+.0%} price move: '
                                     'check the reason is evidence, not the price']
    return 'watch', notes


def load():
    return [json.loads(l) for l in LEDGER.read_text(encoding='utf-8').splitlines() if l.strip()] if LEDGER.exists() else []


def last(entries, ticker):
    return next((e for e in reversed(entries) if e['ticker'] == ticker), None)


def record(ticker, text, entries, price=None, source='working copy', write=True):
    """Append one entry unless nothing changed since the last one. Returns (mark, notes) or None if unchanged."""
    cur = snapshot(text)
    prev = last(entries, ticker)
    if prev and all(prev.get(k) == cur[k] for k in ('date', 'verdict', 'falsifier', 'kills')):
        return None
    move = price / prev['price'] - 1 if price and prev and prev.get('price') else None
    mark, notes = coherence(prev, cur, text, move)
    entry = {'ticker': ticker, **cur, 'price': price, 'logged': date.today().isoformat(),
             'source': source, 'mark': mark, 'notes': notes}
    entries.append(entry)
    if write:
        with LEDGER.open('a', encoding='utf-8') as f:
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')
    return mark, notes


def price_now(ticker):
    r = hm.price_ranges([ticker]).get(ticker)
    return r['last'] if r else None


def git_versions(path):
    rel = str(path.relative_to(hm.ROOT))
    log = subprocess.run(['git', 'log', '--reverse', '--format=%h', '--', rel], cwd=hm.ROOT,
                         capture_output=True, text=True).stdout.split()
    for sha in log:
        text = subprocess.run(['git', 'show', f'{sha}:{rel}'], cwd=hm.ROOT, capture_output=True, text=True).stdout
        if text:
            yield sha, text


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    entries = load()
    if '--history' in sys.argv:
        for e in (e for e in entries if e['ticker'] == args[0].upper()):
            print(f"{e['date']}  {e['verdict'] or '—':17} {e['mark']:9} {'; '.join(e['notes'])}")
        return
    if '--seed' in sys.argv:
        if entries:
            sys.exit('ledger already has entries; --seed only runs once')
        for b in sorted((hm.ROOT / 'briefs').glob('*.md')):
            for sha, text in git_versions(b):
                record(b.stem, text, entries, source=f'git {sha}')
            record(b.stem, b.read_text(encoding='utf-8'), entries, price=price_now(b.stem))
        flagged = [e for e in entries if e['mark'] == 'ego-check']
        print(f'{len(entries)} entries for {len({e["ticker"] for e in entries})} briefs; {len(flagged)} ego-check')
        for e in flagged:
            print(f"  {e['ticker']} {e['date']}: {'; '.join(e['notes'])}")
        return
    t = args[0].upper()
    result = record(t, (hm.ROOT / 'briefs' / f'{t}.md').read_text(encoding='utf-8'), entries, price=price_now(t))
    if result is None:
        print(f'{t}: no change since the last entry')
        return
    mark, notes = result
    print(f'{t}: {mark}' + (''.join(f'\n  - {n}' for n in notes)))
    sys.exit(2 if mark == 'ego-check' else 0)


if __name__ == '__main__':
    main()
