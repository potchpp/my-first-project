"""Daily check: which tickers need /deep, and why. Plain Python, no LLM, never edits briefs, never commits.

Refreshes prices and both map pages, then prints one line per NEW flag (TICKER<TAB>reason). Prints nothing when
there is nothing new, so the scheduled task can stay silent. A flag already reported is repeated only after
RENOTIFY_DAYS if it is still unresolved.

News spikes come from Google News RSS (free, no key), searched by company name. Only the daily COUNT is kept, in
portfolio/news-counts.json; no headline, text or link is stored or printed. A news flag that clears can fire again
on a later burst.

  python3 scripts/needs_deep.py             # refresh, print new flags, remember them
  python3 scripts/needs_deep.py --all       # every current flag, including ones already reported
  python3 scripts/needs_deep.py --dry-run   # no price or news fetch, no state written
"""
import json
import re
import statistics
import subprocess
import sys
import time
from datetime import date, timedelta
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent))
import holdings_map as hm  # noqa: E402

STATE = hm.ROOT / 'portfolio' / '.deep-notified.json'  # private folder, gitignored: {"TSLA|crossed": "2026-09-30"}
NEWS = hm.ROOT / 'portfolio' / 'news-counts.json'      # {"2026-10-01": {"RKLB": 53, ...}}
RENOTIFY_DAYS = 7
NEWS_FEED = 'https://news.google.com/rss/search'
NEWS_CAP = 100                     # the feed never returns more than 100 items
NEWS_RATIO, NEWS_FLOOR, NEWS_MIN_DAYS, NEWS_KEEP_DAYS = 3.0, 10, 7, 60
# Names that are ambiguous, too long, or better known another way. Everything else: intitle:"<company name>".
NEWS_QUERY = {
    'AAPL': 'intitle:Apple (iPhone OR stock OR Cook OR AI)', 'AMD': 'intitle:AMD', 'ASML': 'intitle:ASML',
    'CRCL': '(intitle:"Circle Internet" OR intitle:USDC)', 'FWONA': '(intitle:"Formula 1" OR intitle:"Liberty Media")',
    'GMAB': 'intitle:Genmab', 'GOOG': '(intitle:Alphabet OR intitle:Google)', 'META': '(intitle:Meta OR intitle:Zuckerberg)',
    'MU': 'intitle:Micron', 'PLTR': 'intitle:Palantir', 'PTON': 'intitle:Peloton', 'RGTI': 'intitle:Rigetti',
    'RKLB': 'intitle:"Rocket Lab"', 'SNOW': 'intitle:Snowflake (stock OR data OR AI)', 'SPCX': 'intitle:SpaceX',
    'TCOM': 'intitle:"Trip.com"', 'TSM': 'intitle:TSMC', 'WQEY': 'intitle:WISeQey OR intitle:WISeKey',
}


def news_query(ticker):
    if ticker in NEWS_QUERY:
        return NEWS_QUERY[ticker]
    name = hm.frontmatter((hm.ROOT / 'briefs' / f'{ticker}.md').read_text(encoding='utf-8'), 'company')
    name = re.sub(hm.SUFFIX, '', re.sub(r'\([^)]*\)', '', name), flags=re.I)
    return f'intitle:"{" ".join(name.replace(",", " ").split()).strip(" .")}"'  # "Garmin Ltd." -> "Garmin"


def news_count(query, get=requests.get):
    """Stories in the last day, 0-100, or None when the feed can't be read (error, 429, timeout)."""
    try:
        r = get(NEWS_FEED, params={'q': f'{query} when:1d', 'hl': 'en-US', 'gl': 'US', 'ceid': 'US:en'},
                headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
        return r.text.count('<item>') if r.status_code == 200 else None
    except Exception:
        return None


def fetch_counts(tickers, get=requests.get, pause=1.0):
    """{ticker: count}; stops after 3 failures in a row so a dead network costs seconds, not an hour."""
    out, misses = {}, 0
    for t in tickers:
        n = news_count(news_query(t), get)
        misses = misses + 1 if n is None else 0
        if n is not None:
            out[t] = n
        if misses >= 3:
            break
        time.sleep(pause)
    return out


def news_spikes(history, today_counts):
    """{ticker: (today, usual)} where today is NEWS_RATIO x the ticker's own median over the days it has data.
    Tickers whose usual is already >= NEWS_CAP / NEWS_RATIO can't show a spike under the feed's cap: skipped."""
    out = {}
    for t, n in today_counts.items():
        prior = [day[t] for day in history.values() if t in day]
        if len(prior) < NEWS_MIN_DAYS:
            continue
        usual = statistics.median(prior)
        if usual < NEWS_CAP / NEWS_RATIO and n >= NEWS_FLOOR and n >= NEWS_RATIO * usual:
            out[t] = (n, usual)
    return out


def update_news(tickers, today, get=requests.get):
    """Fetch today's counts, store them, return spikes. Writes nothing when the feed looks broken."""
    history = json.loads(NEWS.read_text()) if NEWS.exists() else {}
    history.pop(today.isoformat(), None)  # a re-run today replaces today's counts, not compares against them
    counts = fetch_counts(tickers, get)
    if len(counts) < len(tickers) / 2 or not any(counts.values()):
        print(f'news: feed unreadable ({len(counts)}/{len(tickers)} counts), skipped today', file=sys.stderr)
        return {}
    spikes = news_spikes(history, counts)
    keep = (today - timedelta(days=NEWS_KEEP_DAYS)).isoformat()
    NEWS.write_text(json.dumps({**{d: v for d, v in history.items() if d >= keep}, today.isoformat(): counts},
                               indent=1, sort_keys=True))
    return spikes


def flags(monitor, ranges, briefs, today, news=None):
    """[(ticker, kind, reason)], one per ticker, most serious first. 'close to the line' is a watch state on the
    map, not a reason to re-run, so it is not flagged here."""
    out, news = [], news or {}
    for t in sorted(monitor):
        f, r, when = monitor[t].get('falsifier') or {}, ranges.get(t) or {}, (briefs.get(t) or {}).get('date')
        old = bool(when) and (today - date.fromisoformat(when)).days > hm.REVIEW_DAYS
        if f.get('state') == 'crossed':
            out.append((t, 'crossed', f"falsifier line crossed ({f['metric']})"))
        elif f.get('state') == 'due':
            out.append((t, 'due', f"falsifier result due since {f['deadline']} ({f['metric']})"))
        elif abs(r.get('z5') or 0) >= hm.SPIKE_SIGMA:
            out.append((t, 'move', f"unusual 5-day move {r['r5'] * 100:+.1f}%"))
        elif t in news:
            out.append((t, 'news', f'news spike ({news[t][0]} stories vs usual {news[t][1]:.0f})'))
        elif old or any(k['status'] == 'review' for k in monitor[t]['kills']):
            out.append((t, 'stale', f'brief not re-checked for over {hm.REVIEW_DAYS} days (last {when or "never"})'))
    order = {'crossed': 0, 'due': 1, 'move': 2, 'news': 3, 'stale': 4}
    return sorted(out, key=lambda x: order[x[1]])


def unseen(found, seen, today):
    """Flags not reported in the last RENOTIFY_DAYS."""
    return [x for x in found if f'{x[0]}|{x[1]}' not in seen
            or (today - date.fromisoformat(seen[f'{x[0]}|{x[1]}'])).days >= RENOTIFY_DAYS]


def main():
    dry, today = '--dry-run' in sys.argv, date.today()
    if not dry:  # same refresh the Stop hook does: prices, portfolio.json, then both map pages
        for script, *args in (['perf.py'], ['holdings_map.py', '--prices']):
            subprocess.run([sys.executable, str(hm.ROOT / 'scripts' / script), *args], capture_output=True, text=True)
        (hm.ROOT / 'graphify-out' / '.republish-deferred').touch()  # republish_map.py: don't ask this unattended run
    tickers = sorted(hm.brief_meta())
    briefs = hm.summaries(tickers)
    news = {}
    if not dry and NEWS.parent.exists():
        try:
            news = update_news(tickers, today)
        except Exception as e:  # the news feed is unofficial; never let it stop the other triggers
            print(f'news: {e}', file=sys.stderr)
    found = flags(hm.monitor(tickers, briefs, today), hm.price_ranges(tickers), briefs, today, news)
    seen = json.loads(STATE.read_text()) if STATE.exists() else {}
    new = found if '--all' in sys.argv else unseen(found, seen, today)
    for t, _, reason in new:
        print(f'{t}\t{reason}')
    if not dry and STATE.parent.exists():
        current = {f'{t}|{k}' for t, k, _ in found}  # forget resolved flags so they can fire again later
        STATE.write_text(json.dumps({**{k: v for k, v in seen.items() if k in current},
                                     **{f'{t}|{k}': today.isoformat() for t, k, _ in new}}, indent=1))


if __name__ == '__main__':
    main()
