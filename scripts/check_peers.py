"""Check that every briefs/peers.json citation names what it is cited for.

Competitors: {rival: {holding: "file:line"}}. The cited line must name the rival, and the file must belong to the
holding (sources/<T>/ or briefs/<T>.md) or the line must name the holding too. A citation with no line number fails.
Risks: {"risk", "tickers": {T: phrase}, "cite": {T: "file:line"}}. The cited line, in T's own file, must share a word
with the risk name.

    python3 scripts/check_peers.py          # prints FAIL lines, exit 1 if any
    python3 scripts/check_peers.py --all    # also prints every OK line with the word it matched
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PEERS = ROOT / 'briefs' / 'peers.json'
# Names a line may use for a ticker beyond the brief's `company:` field.
ALIASES = {'GOOG': ['Google'], 'MSFT': ['Azure'], 'AMZN': ['AWS', 'Amazon Web Services'], 'META': ['Facebook'],
           'TSM': ['TSMC'], 'LLY': ['Lilly'], 'J&J': ['Johnson & Johnson', 'Janssen'],
           'SPCX': ['SpaceX', 'Starlink'], 'Yangtze Memory Technologies': ['YMTC'], 'SNDK': ['SanDisk'],
           'SK Hynix': ['Hynix'], 'PTON': ['Peloton'], 'IBM': ['International Business Machines']}
STOP = {'and', 'the', 'from', 'with', 'without', 'clear', 'risk', 'loss', 'entry', 'pressure', 'building', 'massive'}


def names(t):
    """Strings that count as naming ticker or company t."""
    out = [t] + ALIASES.get(t, [])
    brief = ROOT / 'briefs' / f'{t}.md'
    if brief.exists():
        m = re.search(r'^company:\s*(.+)$', brief.read_text(encoding='utf-8'), re.M)
        if m:
            full = m.group(1).strip()
            out += [full, re.split(r'[ ,]', full)[0]]  # "Garmin Ltd." -> also "Garmin"
    return [n for n in out if len(n) >= 2]


def hit(text, ns):
    for n in ns:
        if re.search(r'(?<![A-Za-z])' + re.escape(n), text, re.I if len(n) > 4 else 0):
            return n
    return None


def line_of(src):
    """(text of the cited line, error)."""
    path, _, ln = src.partition(':')
    f = ROOT / path
    if not f.exists():
        return None, f'missing file {path}'
    m = re.fullmatch(r'(\d+)(?:-(\d+))?', ln)
    if not m:
        return None, 'no line number'
    lines = f.read_text(encoding='utf-8').splitlines()
    a, b = int(m.group(1)), int(m.group(2) or m.group(1))  # "37-39" = a short range, read as one passage
    if not 1 <= a <= b <= len(lines) or b - a > 3:
        return None, f'bad line range {ln} ({len(lines)} lines)'
    return ' '.join(lines[a - 1:b]), None


def own_file(src, t):
    return src.startswith((f'sources/{t}/', f'briefs/{t}.md'))


def check(doc):
    """Yield (ok, label, src, detail) for every entry."""
    for rival, by in doc.get('competitors', {}).items():
        for t, src in by.items():
            label = f'{t} competes with {rival}'
            text, err = line_of(src)
            if err:
                yield False, label, src, err
                continue
            r = hit(text, names(rival))
            h = own_file(src, t) or hit(text, names(t))
            if r and h:
                yield True, label, src, f'names "{r}"'
            else:
                yield False, label, src, ('' if r else f'line does not name {rival}; ') + \
                    ('' if h else f'not {t}\'s file and line does not name {t}')
    for r in doc.get('risks', []):
        words = [w[:6] for w in re.findall(r'[A-Za-z]{4,}', r['risk']) if w.lower() not in STOP]
        for t in r['tickers']:
            label = f'{t} shares risk "{r["risk"]}"'
            src = r.get('cite', {}).get(t, '')
            if not src:
                yield False, label, '-', 'no citation'
                continue
            text, err = line_of(src)
            w = None if err else hit(text, words)  # 6-letter prefix: "concen", "diluti"
            if err or not w:
                yield False, label, src, err or f'line shares no word with "{r["risk"]}"'
            elif not own_file(src, t):
                yield False, label, src, f'not {t}\'s file'
            else:
                yield True, label, src, f'matches "{w}"'


def main():
    rows = list(check(json.loads(PEERS.read_text(encoding='utf-8'))))
    bad = [r for r in rows if not r[0]]
    for ok, label, src, detail in rows:
        if not ok or '--all' in sys.argv:
            print(f'{"OK  " if ok else "FAIL"}  {label}  [{src}]  {detail}')
    print(f'{len(rows) - len(bad)} of {len(rows)} entries supported by their cited line')
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
