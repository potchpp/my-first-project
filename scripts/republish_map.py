"""Stop hook: keep the published Holdings Map artifact in step with briefs/.

When a brief (or the graph) is newer than graphify-out/holdings-map.html, rebuild it with
holdings_map.py. If the page differs from what was last published, block the stop once and
ask Claude to republish it to the same artifact URL.

  python3 scripts/republish_map.py          # hook mode (reads hook JSON on stdin)
  python3 scripts/republish_map.py --mark   # record the current page as published
"""
import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGE = ROOT / 'graphify-out' / 'holdings-map.html'
MARK = ROOT / 'graphify-out' / '.holdings-map.published'
PRICE_CACHE = ROOT / 'portfolio' / 'cache'
PRICE_REFRESH_HOURS = 20  # 52-week bars refresh about once a day (~10s for 50 tickers)
URL = 'https://claude.ai/artifact/SUwuadkMdVBpPTn6VHiss8'  # owned by potchpurana@gmail.com


def digest():
    return hashlib.sha256(PAGE.read_bytes()).hexdigest() if PAGE.exists() else ''


def main():
    if '--mark' in sys.argv:
        MARK.write_text(digest())
        return
    try:
        hook = json.load(sys.stdin)
    except ValueError:
        hook = {}
    if hook.get('stop_hook_active'):
        return  # already asked this turn; never loop
    # portfolio.json only refreshes the local private page; the published page never reads it
    inputs = [*(ROOT / 'briefs').glob('*.md'), ROOT / 'graphify-out' / 'graph.json',
              Path(__file__).with_name('holdings_map.html'), ROOT / 'portfolio' / 'portfolio.json']
    built = PAGE.stat().st_mtime if PAGE.exists() else 0
    warnings = ''
    newest_price = max((p.stat().st_mtime for p in PRICE_CACHE.glob('*.csv')), default=0)
    prices_stale = time.time() - newest_price > PRICE_REFRESH_HOURS * 3600
    if prices_stale or any(p.exists() and p.stat().st_mtime > built for p in inputs):
        flags = ['--prices'] if prices_stale else []
        run = subprocess.run([sys.executable, str(ROOT / 'scripts' / 'holdings_map.py'), *flags],
                             check=True, capture_output=True, text=True)
        warnings = '; '.join(l.strip() for l in run.stderr.splitlines() if 'skip summary' in l)  # not yfinance noise
    if digest() == (MARK.read_text() if MARK.exists() else ''):
        return
    print(json.dumps({'decision': 'block', 'reason': (
        f'Holdings Map changed. Read {PAGE} and republish it with the Artifact tool, url {URL} '
        f'(same artifact, no icon). Then run: python3 {ROOT}/scripts/republish_map.py --mark'
        + (f'. Tell the user these briefs were left out of the map: {warnings}' if warnings else ''))}))


if __name__ == '__main__':
    try:
        main()
    except Exception as e:  # a broken map must never block the session
        print(f'republish_map: {e}', file=sys.stderr)
