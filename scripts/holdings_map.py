"""Holdings map: an Obsidian canvas of how the briefs connect to each other.

Reads graphify-out/graph.json + briefs/*.md, writes graphify-out/Holdings Map.canvas and
graphify-out/holdings-map.html (the published artifact page; both gitignored, stay local).
A brief newer than the graph still appears, with 0 links, until `/graphify --update` runs.
Node size  = number of other holdings reachable within 2 hops (not raw edge count,
             which mostly measures how long a company's own 10-K is).
Groups     = shared_driver (one bet, several tickers).
Colour     = valuation verdict (red Ahead of itself, green Deserved, cyan Still underrated).
Edge label = the shared entity that links two holdings.
Never reads portfolio/.

Run after each graphify update:  python3 scripts/holdings_map.py
Fetch brand marks once (Simple Icons, pinned):  python3 scripts/holdings_map.py --logos
Refresh 52-week ranges (perf.py's yfinance cache):  python3 scripts/holdings_map.py --prices
"""
import hashlib
import json
import re
import subprocess
import sys
from datetime import date, timedelta
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GRAPH = ROOT / 'graphify-out' / 'graph.json'
OUT = ROOT / 'graphify-out' / 'Holdings Map.canvas'  # local only (gitignored)
PAGE = ROOT / 'graphify-out' / 'holdings-map.html'
# local only: carries your allocation — republish_map.py publishes PAGE, never this one
PRIVATE_PAGE = ROOT / 'graphify-out' / 'holdings-map-private.html'
PORTFOLIO = ROOT / 'portfolio' / 'portfolio.json'
POLICY = ROOT / 'portfolio' / 'policy.json'
# falsifier thresholds and kill-condition reviews, per ticker; about the stock, not your holdings, so tracked in git
MONITOR = ROOT / 'briefs' / 'monitor.json'
TEMPLATE = Path(__file__).with_name('holdings_map.html')
LOGOS = ROOT / 'graphify-out' / 'logos.json'  # {ticker: {hex, d}}; tickers not listed get a letter badge
SIMPLE_ICONS = 'https://cdn.jsdelivr.net/npm/simple-icons@16.32.0'
# ponytail: hand-kept map; only brands Simple Icons carries under the right company (its "circle" is circle.so, not CRCL)
LOGO_SLUGS = {'NVDA': 'nvidia', 'AMD': 'amd', 'AVGO': 'broadcom', 'SPCX': 'spacex', 'AAPL': 'apple',
              'GRMN': 'garmin', 'NFLX': 'netflix', 'PTON': 'peloton', 'FWONA': 'f1', 'TCOM': 'tripdotcom',
              'TEAM': 'atlassian', 'PLTR': 'palantir', 'SNOW': 'snowflake', 'INTC': 'intel', 'ABBV': 'abbvie',
              'GOOG': 'google', 'META': 'meta', 'KO': 'cocacola', 'MMM': '3m', 'TSLA': 'tesla'}
EDGES_PER_NODE = 4          # strongest links kept per ticker, so the map stays readable
# side-panel summary limits: enough to understand a ticker at a glance, the brief has the rest
SNAPSHOT_CHARS, POINT_CHARS, FALSIFIER_CHARS = 420, 240, 200
POINTS_PER_SIDE, KILL_CONDITIONS, QUESTIONS = 3, 4, 3
# brand names research uses that differ from the brief's legal company name
COMMON_NAMES = {'google': 'GOOG', 'facebook': 'META', 'berkshire': 'BRKB'}
# one economic chain, four roles: judged from the briefs (who pays for AI data centers, who sells into them).
# Driver tags split this chain across ai-capex / cloud-hyperscale / digital-ads / energy; this view puts it back together.
CHAINS = {'hyperscaler-capex': [
    ('spender', 'Pay the capex', 'Cash flow improves if capex is cut, but the thesis that AI capex pays off weakens',
     ['GOOG', 'MSFT', 'AMZN', 'META', 'ORCL']),
    ('supplier', 'Revenue is the capex', 'Revenue falls directly when capex is cut',
     ['NVDA', 'AVGO', 'TSM', 'MU', 'ASML', 'AMD', 'LITE', 'SNDK']),
    ('builder', 'Rent out AI capacity', 'Contracts shrink, and these carry debt',
     ['IREN', 'NBIS', 'SPCX']),
    ('second', 'Power, steel, chips for data centers', 'Orders slow as builds slow',
     ['GEV', 'INTC', 'NUE']),
]}
VERDICT_COLOR = {'Ahead of itself': '1', 'Deserved': '4', 'Still underrated': '5'}


def hid(s):
    return hashlib.sha1(s.encode()).hexdigest()[:16]


def load():
    g = json.loads(GRAPH.read_text(encoding='utf-8'))
    nodes = {n['id']: n for n in g['nodes']}
    edges = g.get('links') or g['edges']
    adj = defaultdict(set)
    for e in edges:
        if e.get('confidence') == 'AMBIGUOUS' or e.get('relation') == 'semantically_similar_to':
            continue  # "looks similar" is not a business relationship
        adj[e['source']].add(e['target'])
        adj[e['target']].add(e['source'])
    return nodes, adj, edges


SUFFIX = r'\b(inc|incorporated|corp|corporation|company|companies|co|ltd|limited|plc|group|holdings|nv|the|and)\b'


def name_key(s):
    s = re.sub(r'\(.*?\)', '', s.lower())
    return re.sub(r'[^a-z0-9]', '', re.sub(SUFFIX, '', s))


def brief_meta():
    meta = {}
    for b in sorted((ROOT / 'briefs').glob('*.md')):
        text = b.read_text(encoding='utf-8')
        drv = re.search(r'^shared_driver:\s*(\S+)', text, re.M)
        ver = re.search(r'Verdict[^A-Za-z]*(Ahead of itself|Deserved|Still underrated)', text)
        com = re.search(r'^company:\s*(.+)$', text, re.M)
        meta[b.stem] = {'driver': drv.group(1) if drv else 'other', 'verdict': ver.group(1) if ver else None,
                        'name': name_key(com.group(1)) if com else None}
    return meta


def owner(node):
    """ticker whose research file this node came from (briefs/T.md or sources/T/...)."""
    m = re.match(r'(?:briefs/([A-Z.]+)\.md|sources/([A-Z.-]+)/)', node.get('source_file') or '')
    return (m.group(1) or m.group(2)).replace('-', '') if m else None


def links(nodes, adj, edges, meta):
    """Ticker pairs that are really related.

    Every name variant of a held company ("Nvidia", "NVIDIA (partner)", "GOOG brief") counts as
    that company. A–B is a link when A's research names B, or A and B share a concept (a product,
    contract, risk). Two companies that merely both name a third holding are NOT linked.
    """
    hubs = {n for n in nodes if n.startswith('shared_driver_')}
    rep = {}  # node id -> ticker it stands for
    for h in hubs:
        for a in adj[h]:
            m = re.match(r'briefs/([A-Z.]+)\.md$', nodes[a].get('source_file') or '')
            if m:
                rep[a] = m.group(1)
    main = dict(rep)
    by_ticker = {t: a for a, t in main.items()}
    for e in edges:  # alias edges written by the graph clean-up
        if e.get('note') == 'same company as held brief' and e['target'] in main:
            rep[e['source']] = main[e['target']]
    for nid, n in nodes.items():  # stub nodes like briefs_goog / "GOOG brief"
        m = re.fullmatch(r'briefs_([a-z0-9]+)', nid) or re.fullmatch(r'([A-Z.]+) brief', n.get('label', ''), re.I)
        if m and m.group(1).upper() in by_ticker:
            rep.setdefault(nid, m.group(1).upper())
        # alias nodes from the extraction convention: briefs_<brief>_<ticker> labelled with that ticker
        m = re.fullmatch(r'briefs_[a-z0-9]+_([a-z0-9]+)', nid)
        if m and n.get('label', '').upper() == m.group(1).upper() and m.group(1).upper() in by_ticker:
            rep.setdefault(nid, m.group(1).upper())
    names = {v['name']: t for t, v in meta.items() if v['name'] and t in by_ticker}
    names.update({k: t for k, t in COMMON_NAMES.items() if t in by_ticker})
    for nid, n in nodes.items():  # "Rigetti Computing, Inc." etc.
        t = names.get(name_key(n.get('label', '')))
        if t:
            rep.setdefault(nid, t)

    def research(x):  # only research content, never code/scripts
        return (nodes[x].get('source_file') or '').startswith(('briefs/', 'sources/'))

    pairs = defaultdict(list)  # (A, B) -> labels of what connects them
    own = defaultdict(set)  # every entity extracted from a ticker's brief or sources/ is part of its research
    for nid, n in nodes.items():
        if research(nid) and owner(n) in by_ticker:
            own[owner(n)].add(nid)
    for a, ta in main.items():
        for x in (adj[a] | own[ta]) - hubs - {a}:
            if not research(x):
                continue
            tx = rep.get(x)
            if tx and tx != ta:          # A's research names B
                lab = nodes[x].get('label', x)
                via = 'direct' if x in main else lab if '(' in lab else f'{tx} named in {ta} research'
                pairs[tuple(sorted((ta, tx)))].append(via)
                continue
            for y in adj[x] - hubs:       # A — concept/own-alias — B
                ty = rep.get(y)
                if not ty or ty == ta:
                    continue
                if tx == ta or owner(nodes[x]) == ty:  # A's name inside B's research
                    via = f'{ta} named in {ty} research'
                elif owner(nodes[x]) == ta or owner(nodes[y]) == ta:  # B's name inside A's research
                    via = f'{ty} named in {ta} research'
                else:                                 # a real shared concept
                    via = nodes[x].get('label', x)
                pairs[tuple(sorted((ta, ty)))].append(via)
    return set(main.values()), pairs


def label(vias):
    # prefer a descriptive concept ("Microsoft GB300 5-year contract") over a bare alias or "direct"
    best = max(sorted(set(vias)), key=lambda v: (v != 'direct', '(' in v or len(v.split()) > 2, -len(v)))
    return best if len(best) <= 42 else best[:40] + '…'


def build():
    nodes, adj, edges = load()
    meta = brief_meta()
    tickers, pairs = links(nodes, adj, edges, meta)
    partners = defaultdict(set)
    for a, b in pairs:
        partners[a].add(b)
        partners[b].add(a)

    ungraphed = set(meta) - tickers  # briefs written since the last graphify run
    groups = defaultdict(list)
    for t in sorted(tickers | ungraphed):
        if t in meta:
            groups[meta[t]['driver']].append(t)

    canvas_nodes, canvas_edges, pos = [], [], {}
    page = {'nodes': [], 'edges': []}
    cell_w, cell_h, cols, gap, row_w = 330, 190, 3, 120, 3200
    x0 = y0 = row_h = 0
    for drv, ts in sorted(groups.items(), key=lambda kv: -len(kv[1])):
        ts.sort(key=lambda t: -len(partners[t]))
        c = min(cols, len(ts))
        gw, gh = c * cell_w + 40, -(-len(ts) // c) * cell_h + 60
        if x0 and x0 + gw > row_w:
            x0, y0, row_h = 0, y0 + row_h + gap, 0
        canvas_nodes.append({'id': hid('g:' + drv), 'type': 'group', 'x': x0, 'y': y0,
                             'width': gw, 'height': gh, 'label': f'{drv} ({len(ts)})'})
        for i, t in enumerate(ts):
            n = len(partners[t])
            w, h = 150 + 9 * n, 70 + 5 * n
            x = x0 + 20 + (i % c) * cell_w + (cell_w - w) // 2
            y = y0 + 50 + (i // c) * cell_h + (cell_h - h) // 2
            v = meta[t]['verdict']
            node = {'id': hid('t:' + t), 'type': 'text', 'x': x, 'y': y, 'width': w, 'height': h,
                    'text': f'### [[{t}]]\n{n} links' + (f' · {v}' if v else '')
                    + (' · not in graph yet' if t in ungraphed else '')}
            page['nodes'].append({'t': t, 'g': drv, 'k': n, 'v': v or '', 'new': t in ungraphed})
            if v:
                node['color'] = VERDICT_COLOR[v]
            canvas_nodes.append(node)
            pos[t] = (x + w / 2, y + h / 2)
        x0 += gw + gap
        row_h = max(row_h, gh)

    # keep each ticker's strongest links (strength = number of shared entities)
    strength = {p: len(set(v)) + (3 if 'direct' in v else 0) for p, v in pairs.items()}
    keep = set()
    for t in tickers:
        mine = sorted((p for p in pairs if t in p), key=lambda p: (-strength[p], p))
        keep.update(mine[:EDGES_PER_NODE])
    for a, b in sorted(keep):
        if a not in pos or b not in pos:
            continue
        (ax, ay), (bx, by) = pos[a], pos[b]
        horiz = abs(bx - ax) >= abs(by - ay)
        canvas_edges.append({
            'id': hid(f'e:{a}:{b}'), 'fromNode': hid('t:' + a), 'toNode': hid('t:' + b),
            'fromSide': ('right' if bx > ax else 'left') if horiz else ('bottom' if by > ay else 'top'),
            'toSide': ('left' if bx > ax else 'right') if horiz else ('top' if by > ay else 'bottom'),
            'toEnd': 'none', 'label': label(pairs[(a, b)])})
        page['edges'].append({'s': a, 'd': b, 'l': canvas_edges[-1]['label']})

    legend = ('## Holdings map\nSize = links to **other holdings** (2 hops), not filing length.\n'
              'Colour: 🔴 Ahead of itself · 🟢 Deserved · 🔵 Still underrated · grey = no verdict yet.\n'
              f'Lines: each ticker\'s {EDGES_PER_NODE} strongest links, labelled with what connects them.\n'
              'Central ≠ buy more — a hub is where one shock hits many theses.\n'
              'Regenerate: `python3 scripts/holdings_map.py`')
    canvas_nodes.insert(0, {'id': hid('legend'), 'type': 'text', 'x': 0, 'y': -330,
                            'width': 760, 'height': 260, 'text': legend})
    return {'nodes': canvas_nodes, 'edges': canvas_edges}, page


def clean(text):
    text = re.sub(r'\s*\*\((?:[^()]|\([^()]*\))*\)\*', '', text)  # *(source …)* citations
    text = re.sub(r'\[\[(?:[^\]|]*/)?([^\]|]+)\]\]', r'\1', text)  # [[TICKER]] / [[sources/x/y]]
    text = re.sub(r'[*`]', '', text)
    return re.sub(r'\s+', ' ', text).strip()


def short(text, n=POINT_CHARS):
    return text if len(text) <= n else text[:text.rfind(' ', 0, n)] + '…'


def sections(text):
    out = {}
    for block in re.split(r'^## ', text, flags=re.M)[1:]:
        head, _, body = block.partition('\n')
        out.setdefault(head.strip().lower(), body)
    return out


def section(secs, *starts):
    return next((b for h, b in secs.items() if h.startswith(starts)), '')


def bullets(body, n):
    found = [m.group(1) for m in re.finditer(r'^\s*(?:-|\d+\.)\s+(.+)', body, re.M)]
    return [short(clean(b)) for b in found[:n]]


def frontmatter(text, key):
    m = re.search(rf'^{key}:\s*(.+)$', text, re.M)
    return m.group(1).strip() if m else ''


def summary(text):
    """The parts of a brief a reader needs first. Handles both brief formats."""
    secs = sections(text)
    snap = section(secs, 'company snapshot', 'what the company does')
    para = next((p for p in snap.split('\n\n') if p.strip() and not p.startswith(('---', '>'))), '')
    bull, bear, side = [], [], None
    for line in section(secs, 'bull').splitlines():
        m = re.match(r'\s*\*\*(Bull|Bear)\b[^*]*\*\*:?\s*(.*)', line)
        if m:
            side = bull if m.group(1) == 'Bull' else bear
            rest = clean(m.group(2))
            if rest:
                side.append(short(rest))
            continue
        m = re.match(r'\s*-\s+(.+)', line)
        if m and side is not None:
            side.append(short(clean(m.group(1))))
    fals = re.search(r'Falsifying number:?\**\s*(.+)', text)
    return {'name': frontmatter(text, 'company'), 'date': frontmatter(text, 'updated'),
            'snap': short(clean(para), SNAPSHOT_CHARS),
            'bull': bull[:POINTS_PER_SIDE], 'bear': bear[:POINTS_PER_SIDE],
            'kill': bullets(section(secs, 'kill'), KILL_CONDITIONS),
            'ask': bullets(section(secs, 'what to ask'), QUESTIONS),
            'fals': short(clean(fals.group(1)), FALSIFIER_CHARS) if fals else ''}


def summaries(tickers):
    """One summary per brief; a brief that won't parse is skipped loudly, never fails the whole map."""
    out = {}
    for t in tickers:
        try:
            out[t] = summary((ROOT / 'briefs' / f'{t}.md').read_text(encoding='utf-8'))
        except Exception as e:
            print(f'  skip summary {t}: {e}', file=sys.stderr)
    return out


STALE_PRICE_DAYS = 10  # a cache this old means the ticker stopped updating; show no range rather than a wrong one


REVIEW_DAYS = 120          # a kill condition not re-checked for this long needs review (same line as update_index.py)
FALSIFIER_CLOSE = 0.15     # within 15% of the falsifying line counts as "close"
SPIKE_SIGMA = 2.0          # a 5-day move beyond 2 standard deviations of the stock's own daily moves is unusual


def kill_statuses(kills, checked, reviews, today):
    """Each kill condition with a status. A condition counts as checked on the brief's date (writing the brief
    re-examines it); monitor.json 'kills' entries [{match, status, checked, note}] override by text match."""
    out = []
    for text in kills:
        r = next((r for r in reviews if r['match'] in text), {})
        when = r.get('checked', checked)
        stale = bool(when) and (today - date.fromisoformat(when)).days > REVIEW_DAYS
        out.append({'text': text, 'status': r.get('status') or ('review' if stale or not when else 'intact'),
                    'checked': when, 'note': r.get('note', '')})
    return out


def falsifier_state(f, today):
    """How close the verdict is to being proven wrong: clear / close / crossed, or pending / due for an event."""
    days = (date.fromisoformat(f['deadline']) - today).days if f.get('deadline') else None
    if f['type'] == 'event':
        return {**f, 'state': 'due' if days is not None and days < 0 else 'pending', 'days': days}
    if f.get('current') is None:
        return {**f, 'state': 'no data', 'days': days}
    gap = f['current'] - f['threshold'] if f['breaks'] == 'below' else f['threshold'] - f['current']
    room = gap / abs(f['threshold']) if f['threshold'] else gap
    state = 'crossed' if room < 0 else 'close' if room < FALSIFIER_CLOSE else 'clear'
    if f.get('judged') == 'at deadline' and state != 'clear':
        state = 'due' if days is not None and days < 0 else 'pending'  # a target still being built toward
    return {**f, 'state': state, 'room': round(room, 3), 'days': days}


def monitor(tickers, briefs, today):
    """Per ticker: kill conditions with status, plus the falsifier's distance to its line."""
    watched = json.loads(MONITOR.read_text(encoding='utf-8')) if MONITOR.exists() else {}
    out = {}
    for t in tickers:
        w, b = watched.get(t, {}), briefs.get(t, {})
        out[t] = {'kills': kill_statuses(b.get('kill', []), b.get('date', ''), w.get('kills', []), today),
                  'falsifier': falsifier_state(w['falsifier'], today) if w.get('falsifier') else None}
    return out


def recent_move(closes):
    """1-day and 5-day return, and the 5-day move in units of the stock's own daily volatility."""
    days = sorted(closes)[-253:]
    if len(days) < 30:
        return {}
    px = [closes[d] for d in days]
    daily = [b / a - 1 for a, b in zip(px, px[1:])]
    mean = sum(daily) / len(daily)
    sd = (sum((x - mean) ** 2 for x in daily) / (len(daily) - 1)) ** 0.5
    r5 = px[-1] / px[-6] - 1
    return {'r1': round(px[-1] / px[-2] - 1, 4), 'r5': round(r5, 4), 'z5': round(r5 / (sd * 5 ** 0.5), 2) if sd else 0}


def range_52w(closes, today):
    """52-week closing low/high and the latest close, from {date: close}. None if too little or too stale."""
    year = {d: c for d, c in closes.items() if d > today - timedelta(days=365)}
    if len(year) < 20 or (today - max(year)).days > STALE_PRICE_DAYS:
        return None
    last = max(year)
    return {'lo': round(min(year.values()), 2), 'hi': round(max(year.values()), 2),
            'last': round(year[last], 2), 'asof': last.isoformat()}


def price_ranges(tickers, fetch=False):
    """52-week ranges from portfolio/cache (shared with perf.py). Prices are public data, safe to publish."""
    import perf  # same folder; its yfinance import only happens when fetching
    today = date.today()
    ysym = {t: perf.yahoo_symbol({'BRKB': 'BRK.B'}.get(t, t)) for t in tickers}
    prices = perf.get_prices(set(ysym.values()), today - timedelta(days=372), today, fetch=fetch)
    ranges = {t: range_52w(prices.get(y, {}), today) for t, y in ysym.items()}
    return {t: {**r, **recent_move(prices[ysym[t]])} for t, r in ranges.items() if r}


def contributions(weights, moves, period):
    """Each holding's share of the book's move over `period` ('r1' or 'r5'), in percentage points.
    Start weights are backed out from today's: w0 ∝ w / (1 + r)."""
    start = {t: w / (1 + moves[t][period]) for t, w in weights.items() if period in moves.get(t, {})}
    total = sum(start.values())
    pp = {t: w0 / total * moves[t][period] * 100 for t, w0 in start.items()} if total else {}
    return {'book': round(sum(pp.values()), 2), 'by': sorted(([t, round(v, 2)] for t, v in pp.items()), key=lambda x: -x[1])}


def chain_exposure(roles, held, us_share):
    """% of total assets per role, plus the two failure modes: capex cut for discipline (everyone but spenders
    loses) and AI demand disappointing (the whole chain loses)."""
    out, cut, demand = [], 0.0, 0.0
    for key, name, hit, tickers in roles:
        mine = sorted(([t, round(held[t]['w'] * 100, 2)] for t in tickers if t in held), key=lambda x: -x[1])
        pct = sum(held[t]['w'] for t in tickers if t in held) * us_share * 100
        out.append({'key': key, 'name': name, 'hit': hit, 'pct': round(pct, 2), 'held': mine,
                    'watch': [t for t in tickers if t not in held]})
        demand += pct
        cut += 0 if key == 'spender' else pct
    return {'roles': out, 'cut': round(cut, 2), 'demand': round(demand, 2)}


def portfolio_view(page, portfolio, policy, moves=None):
    """Per held ticker: weight, 1y return vs benchmark, gain vs cost; per driver: % of total assets vs cap;
    the book's 1-day and 5-day move by holding. Percentages only — never dollar amounts or share counts."""
    moves = moves or {}
    driver_of = {n['t']: n['g'] for n in page['nodes']}
    us_share = policy.get('us_stock_share_of_total', 1)
    held, no_brief, exposure = {}, [], defaultdict(float)
    for p in portfolio['positions']:
        t = p['symbol'].replace('.', '')  # BRK.B -> BRKB, the brief's name
        year = (p.get('windows') or {}).get('1y') or {}  # null for positions held < 1 year
        gain = p['last_close'] / p['avg_cost'] - 1 if p.get('avg_cost') and p.get('last_close') else None
        held[t] = {'w': p['weight'], 'apr': year.get('apr'), 'bench': year.get('bench'), 'under': year.get('underperformer'),
                   'gain': round(gain, 4) if gain is not None else None}
        if t in driver_of:
            exposure[driver_of[t]] += p['weight'] * us_share * 100
        else:
            no_brief.append(t)
    return {'as_of': portfolio.get('as_of', ''), 'cap': policy.get('driver_cap_pct_total'), 'held': held,
            'no_brief': sorted(no_brief), 'drivers': sorted(([g, round(v, 2)] for g, v in exposure.items()), key=lambda d: -d[1]),
            'moves': {p: contributions({t: h['w'] for t, h in held.items()}, moves, p) for p in ('r1', 'r5')},
            'chains': {name: chain_exposure(roles, held, us_share) for name, roles in CHAINS.items()}}


# the Artifact host wraps the published page in its own <head>; the local page opens straight from disk
# and needs its own, or Safari decodes the UTF-8 (Thai, ·, —) as Latin-1
STANDALONE_HEAD = '<!doctype html>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1">\n'


def render(page, standalone=False):
    data = json.dumps(page, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
    return (STANDALONE_HEAD if standalone else '') + TEMPLATE.read_text(encoding='utf-8').replace('__DATA__', data)


def fetch_logos():
    # curl, not urllib: this Python has no CA bundle and certificate checks must stay on
    get = lambda path: subprocess.run(['curl', '-fsSL', '--max-time', '30', f'{SIMPLE_ICONS}/{path}'],
                                      check=True, capture_output=True, text=True).stdout
    data = json.loads(get('data/simple-icons.json'))
    hexes = {i.get('slug'): i['hex'] for i in (data if isinstance(data, list) else data['icons'])}
    logos = {}
    for t, slug in LOGO_SLUGS.items():
        logos[t] = {'hex': hexes[slug], 'd': re.search(r' d="([^"]+)"', get(f'icons/{slug}.svg')).group(1)}
    LOGOS.write_text(json.dumps(logos), encoding='utf-8')
    print(f'{LOGOS.relative_to(ROOT)}: {len(logos)} logos')


def check(c):
    ids = [n['id'] for n in c['nodes']] + [e['id'] for e in c['edges']]
    assert len(ids) == len(set(ids)), 'duplicate ids'
    nid = {n['id'] for n in c['nodes']}
    assert all(e['fromNode'] in nid and e['toNode'] in nid for e in c['edges']), 'dangling edge'
    assert 'portfolio' not in json.dumps(c).lower(), 'portfolio data must never reach the canvas'
    for t in re.findall(r'\[\[([A-Z.]+)\]\]', json.dumps(c)):
        assert (ROOT / 'briefs' / f'{t}.md').exists(), f'link to missing brief {t}'


if __name__ == '__main__':
    if '--logos' in sys.argv:
        fetch_logos()
    canvas, page = build()
    page['briefs'] = summaries(n['t'] for n in page['nodes'])
    page['logos'] = json.loads(LOGOS.read_text(encoding='utf-8')) if LOGOS.exists() else {}
    page['ranges'] = price_ranges([n['t'] for n in page['nodes']], fetch='--prices' in sys.argv)
    page['monitor'] = monitor([n['t'] for n in page['nodes']], page['briefs'], date.today())
    check(canvas)
    OUT.write_text(json.dumps(canvas, indent=1, ensure_ascii=False), encoding='utf-8')
    assert 'portfolio' not in page, 'the published page must never carry portfolio data'
    PAGE.write_text(render(page), encoding='utf-8')
    if PORTFOLIO.exists():
        policy = json.loads(POLICY.read_text(encoding='utf-8')) if POLICY.exists() else {}
        portfolio = json.loads(PORTFOLIO.read_text(encoding='utf-8'))
        held = [p['symbol'].replace('.', '') for p in portfolio['positions']]
        moves = {**price_ranges([t for t in held if t not in page['ranges']]), **page['ranges']}  # unbriefed holdings too
        view = portfolio_view(page, portfolio, policy, moves)
        PRIVATE_PAGE.write_text(render({**page, 'portfolio': view}, standalone=True), encoding='utf-8')
    tickers = sum(1 for n in canvas['nodes'] if n['type'] == 'text') - 1
    print(f'{OUT.relative_to(ROOT)}: {tickers} tickers, {len(canvas["edges"])} links')
