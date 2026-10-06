"""Stop hook: keep both Holdings Map pages in step with briefs/ and your portfolio.
About once a day, and whenever the holdings CSV is saved, it also runs perf.py, so the private page's weights and returns refresh
from the same price cache the public page uses.

When a brief (or the graph) is newer than graphify-out/holdings-map.html, rebuild it with
holdings_map.py. The claude.ai artifact carries the PRIVATE page (your allocation; the public map
lives on Vercel), so if the private page differs from what was last published, block the stop once
and ask Claude to republish it to the same artifact URL.

  python3 scripts/republish_map.py          # hook mode (reads hook JSON on stdin)
  python3 scripts/republish_map.py --mark   # record the current page as published
"""
import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGE = ROOT / 'graphify-out' / 'holdings-map.html'
PRIVATE = ROOT / 'graphify-out' / 'holdings-map-private.html'  # what the artifact shows (decided 2026-10-02)
MARK = ROOT / 'graphify-out' / '.holdings-map.published'
PRICE_CACHE = ROOT / 'portfolio' / 'cache'
PRICE_REFRESH_HOURS = 20  # 52-week bars refresh about once a day (~10s for 50 tickers)
DEFER = ROOT / 'graphify-out' / '.republish-deferred'  # touched by needs_deep.py: the unattended daily check can't approve a publish
DEFER_SECONDS = 900
NO_PUBLISH = ROOT / '.claude' / 'no-publish-orgs'  # gitignored: one org id per line whose sessions can't write the artifact (another org owns it)
URL = 'https://claude.ai/artifact/SUwuadkMdVBpPTn6VHiss8'  # private view: never share this link (it shows weights and cost basis)


def commit_site():
    """Commit index.html (the Vercel home page) when the map changed it. Never pushes:
    the repo is public, so the site goes live only when you run git push."""
    site = 'index.html'
    if subprocess.run(['git', 'diff', '--quiet', '--', site], cwd=ROOT).returncode == 0:
        return  # unchanged
    subprocess.run(['git', 'commit', '-q', '-m', 'Update Holdings Map (index.html)', '--', site],
                   cwd=ROOT, capture_output=True, text=True)


def published_page():
    return PRIVATE if PRIVATE.exists() else PAGE  # no portfolio.json yet: fall back to the public map


def digest():
    page = published_page()
    return hashlib.sha256(page.read_bytes()).hexdigest() if page.exists() else ''


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
    portfolio = ROOT / 'portfolio' / 'portfolio.json'
    holdings_edited = any(c.stat().st_mtime > (portfolio.stat().st_mtime if portfolio.exists() else 0)
                          for c in (ROOT / 'portfolio').glob('*.csv'))  # the Yahoo-format export you edit
    if prices_stale or holdings_edited:
        # One refresh feeds both pages: perf.py updates the shared price cache and portfolio.json
        # (private page); the map below then only fetches the watch-list names perf.py doesn't hold.
        subprocess.run([sys.executable, str(ROOT / 'scripts' / 'perf.py')], capture_output=True, text=True)
    if prices_stale or any(p.exists() and p.stat().st_mtime > built for p in inputs):
        flags = ['--prices'] if prices_stale else []
        run = subprocess.run([sys.executable, str(ROOT / 'scripts' / 'holdings_map.py'), *flags],
                             check=True, capture_output=True, text=True)
        warnings = '; '.join(l.strip() for l in run.stderr.splitlines() if 'skip summary' in l)  # not yfinance noise
    commit_site()
    if digest() == (MARK.read_text() if MARK.exists() else ''):
        return
    if DEFER.exists() and time.time() - DEFER.stat().st_mtime < DEFER_SECONDS:
        return  # the daily check just ran; the next interactive session will be asked instead
    if NO_PUBLISH.exists() and os.environ.get('CLAUDE_CODE_ORGANIZATION_UUID', '') in NO_PUBLISH.read_text().split():
        return  # this account can't write the artifact; the owner account's next session republishes
    print(json.dumps({'decision': 'block', 'reason': (
        f'Holdings Map changed. Read {published_page()} and republish it with the Artifact tool, url {URL} '
        f'(same artifact, no icon). Then run: python3 {ROOT}/scripts/republish_map.py --mark'
        + (f'. Tell the user these briefs were left out of the map: {warnings}' if warnings else ''))}))


if __name__ == '__main__':
    try:
        main()
    except Exception as e:  # a broken map must never block the session
        print(f'republish_map: {e}', file=sys.stderr)
