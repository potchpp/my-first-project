#!/usr/bin/env python3
"""
fetch_transcript.py — Fetches the latest earnings call transcript for a ticker
                      and saves to sources/<TICKER>/q<N>-<YEAR>-call.md

Source strategy:
  1. Search The Motley Fool (fool.com) for the transcript URL
  2. Fallback: DuckDuckGo HTML search (site:fool.com) to discover the URL
  3. Download and parse the transcript page

Usage:
    python fetch_transcript.py AAPL
    python fetch_transcript.py NVDA TSLA          # multiple tickers

Output example: sources/AAPL/q2-2026-call.md

Requirements: Python 3.10+ stdlib only (no pip install)
"""

import sys
import re
import time
import gzip
import ssl
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError
from html.parser import HTMLParser
from urllib.parse import quote_plus

# macOS Python often ships without root certs configured — use unverified context
_SSL = ssl._create_unverified_context()

SCRIPT_DIR    = Path(__file__).parent
OUTPUT_DIR    = SCRIPT_DIR.parent / "sources"
REQUEST_DELAY = 1.5   # seconds between requests (be polite)

# Realistic browser User-Agent — required by most sites to avoid 403
_UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)
_HEADERS = {
    "User-Agent": _UA,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate",
}

# Pattern that matches a Motley Fool transcript URL
FOOL_URL_RE = re.compile(
    r"https://www\.fool\.com/earnings/call-transcripts/"
    r"(\d{4})/(\d{2})/(\d{2})/([\w-]+earnings-call[\w-]*)/"
)


# ── HTTP ───────────────────────────────────────────────────────────────────

def web_get(url: str, extra_headers: dict | None = None) -> str:
    h = dict(_HEADERS)
    if extra_headers:
        h.update(extra_headers)
    req = Request(url, headers=h)
    try:
        with urlopen(req, timeout=30, context=_SSL) as resp:
            raw = resp.read()
            if resp.info().get("Content-Encoding") == "gzip" or raw[:2] == b"\x1f\x8b":
                raw = gzip.decompress(raw)
        try:
            return raw.decode("utf-8")
        except UnicodeDecodeError:
            return raw.decode("latin-1", errors="replace")
    except HTTPError as e:
        raise RuntimeError(f"HTTP {e.code}: {url}") from e
    except URLError as e:
        raise RuntimeError(f"Network error: {url} — {e.reason}") from e


# ── Transcript URL discovery ───────────────────────────────────────────────

def _find_fool_urls_in_html(html: str) -> list[str]:
    """Return all unique Motley Fool transcript URLs found in HTML, newest first."""
    matches = FOOL_URL_RE.findall(html)
    seen: set[str] = set()
    results: list[tuple] = []
    for year, month, day, slug in matches:
        url = f"https://www.fool.com/earnings/call-transcripts/{year}/{month}/{day}/{slug}/"
        if url not in seen:
            seen.add(url)
            results.append((year, month, day, url))
    # Sort newest first
    results.sort(key=lambda x: (x[0], x[1], x[2]), reverse=True)
    return [r[3] for r in results]


def find_transcript_url_fool(ticker: str) -> str | None:
    """Search Motley Fool for the ticker's latest transcript."""
    query = quote_plus(f"{ticker} earnings call transcript")
    url   = f"https://www.fool.com/search/?q={query}&source=eustranscripts"
    _log(f"Searching Motley Fool: {url}")
    try:
        html = web_get(url, extra_headers={"Referer": "https://www.fool.com/"})
        time.sleep(REQUEST_DELAY)
        urls = _find_fool_urls_in_html(html)
        # Filter to only URLs containing the ticker (case-insensitive)
        ticker_lower = ticker.lower()
        relevant = [u for u in urls if ticker_lower in u.lower()]
        if relevant:
            _log(f"Found via Fool search: {relevant[0]}")
            return relevant[0]
    except Exception as e:
        _log(f"Fool search failed: {e}")
    return None


def find_transcript_url_ddg(ticker: str) -> str | None:
    """Fallback: DuckDuckGo HTML search to find the Motley Fool transcript URL."""
    query = quote_plus(f"site:fool.com/earnings/call-transcripts {ticker} earnings call transcript")
    url   = f"https://html.duckduckgo.com/html/?q={query}"
    _log(f"Searching DuckDuckGo (fallback): {url}")
    try:
        html = web_get(url, extra_headers={"Referer": "https://duckduckgo.com/"})
        time.sleep(REQUEST_DELAY)
        urls = _find_fool_urls_in_html(html)
        ticker_lower = ticker.lower()
        relevant = [u for u in urls if ticker_lower in u.lower()]
        if relevant:
            _log(f"Found via DuckDuckGo: {relevant[0]}")
            return relevant[0]
    except Exception as e:
        _log(f"DuckDuckGo search failed: {e}")
    return None


def find_transcript_url(ticker: str) -> str:
    """Return the Motley Fool URL for the latest earnings transcript, or raise."""
    url = find_transcript_url_fool(ticker) or find_transcript_url_ddg(ticker)
    if url:
        return url
    raise RuntimeError(
        f"Could not find a Motley Fool transcript for {ticker}.\n"
        f"  Try manually: https://www.fool.com/search/?q={ticker}+earnings+call+transcript"
    )


# ── HTML → plain text ──────────────────────────────────────────────────────

class _TextExtractor(HTMLParser):
    """Strips HTML; inserts newlines at block boundaries."""
    _SKIP  = {"script", "style", "noscript", "head", "meta", "link", "nav",
               "footer", "aside", "form", "button"}
    _BLOCK = {"p", "div", "section", "article", "h1", "h2", "h3", "h4",
               "h5", "h6", "li", "tr", "blockquote"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self._depth = 0

    def handle_starttag(self, tag, attrs):
        t = tag.lower()
        if t in self._SKIP:
            self._depth += 1
        elif self._depth == 0 and (t in self._BLOCK or t == "br"):
            self.parts.append("\n")

    def handle_endtag(self, tag):
        t = tag.lower()
        if t in self._SKIP:
            self._depth = max(0, self._depth - 1)
        elif self._depth == 0 and t in self._BLOCK:
            self.parts.append("\n")

    def handle_data(self, data):
        if self._depth == 0:
            self.parts.append(data)

    def result(self) -> str:
        text = "".join(self.parts)
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()


def html_to_text(html: str) -> str:
    p = _TextExtractor()
    p.feed(html)
    return p.result()


# ── Parse transcript page ──────────────────────────────────────────────────

def _parse_slug(slug: str) -> tuple[str, str]:
    """
    Extract quarter and fiscal year from URL slug.
    e.g. 'apple-aapl-q2-2026-earnings-call-transcript' → ('2', '2026')
    """
    m = re.search(r"-q(\d)-(\d{4})-earnings", slug, re.IGNORECASE)
    if m:
        return m.group(1), m.group(2)
    # Fallback: try to find any q\d and year in slug
    q = re.search(r"q(\d)", slug, re.IGNORECASE)
    y = re.search(r"(\d{4})", slug)
    return (q.group(1) if q else "?"), (y.group(1) if y else "????")


def _extract_transcript_body(html: str) -> str:
    """
    Extract just the article body from a Motley Fool transcript page.
    Tries to isolate the main content area to strip nav/ads.
    """
    # Try to find article content between known landmark patterns
    # Motley Fool article body usually starts after the author byline
    # and ends before 'related articles' / 'fool.com premium' sections.

    text = html_to_text(html)

    # Find start: first paragraph that reads like transcript content
    # (first line that isn't a header/nav — look for earnings/revenue language)
    lines = text.split("\n")

    start_idx = 0
    # Skip until we hit a line that looks like the beginning of the call
    # (contains "quarter", "revenue", "fiscal", or is CEO/CFO speech)
    for i, line in enumerate(lines):
        stripped = line.strip()
        if len(stripped) > 80 and any(kw in stripped.lower() for kw in
           ["quarter", "revenue", "earnings", "fiscal", "thank you", "thanks"]):
            start_idx = i
            break

    # Find end: cut at "related articles", "premium", or "fool.com" boilerplate
    end_idx = len(lines)
    for i in range(len(lines) - 1, start_idx, -1):
        stripped = lines[i].strip().lower()
        if any(kw in stripped for kw in
               ["related articles", "fool.com premium", "motley fool",
                "premium services", "sign up", "subscribe", "disclosures"]):
            end_idx = i
            break

    body = "\n".join(lines[start_idx:end_idx]).strip()

    # Clean up artifacts
    body = re.sub(r"\n{3,}", "\n\n", body)
    return body


def fetch_transcript(transcript_url: str) -> tuple[str, str]:
    """
    Download transcript page and return (title, body_text).
    """
    _log(f"Downloading transcript: {transcript_url}")
    html = web_get(transcript_url, extra_headers={"Referer": "https://www.fool.com/"})
    time.sleep(REQUEST_DELAY)

    # Extract page title
    title_m = re.search(r"<title>([^<]+)</title>", html, re.IGNORECASE)
    page_title = title_m.group(1).strip() if title_m else "Earnings Call Transcript"
    # Clean " | The Motley Fool" suffix
    page_title = re.sub(r"\s*\|.*$", "", page_title).strip()

    body = _extract_transcript_body(html)
    if len(body) < 200:
        raise RuntimeError(
            f"Transcript body too short ({len(body)} chars) — page may require login or is unavailable."
        )

    return page_title, body


# ── Output ─────────────────────────────────────────────────────────────────

def build_md(ticker: str, quarter: str, year: str, title: str,
             transcript_url: str, body: str) -> str:
    return (
        f"---\n"
        f"ticker: {ticker.upper()}\n"
        f"source_type: earnings_call_transcript\n"
        f"quarter: Q{quarter} FY{year}\n"
        f"source_url: {transcript_url}\n"
        f"---\n\n"
        f"# {title}\n\n"
        f"{body}\n"
    )


def save(ticker: str, quarter: str, year: str, content: str) -> Path:
    out_dir = OUTPUT_DIR / ticker.upper()
    out_dir.mkdir(parents=True, exist_ok=True)
    filename = f"q{quarter}-{year}-call.md"
    path = out_dir / filename
    path.write_text(content, encoding="utf-8")
    return path


# ── Logging ────────────────────────────────────────────────────────────────

_current = ""

def _log(msg: str):
    print(f"  [{_current}] {msg}")


# ── Per-ticker pipeline ────────────────────────────────────────────────────

def fetch_one(ticker: str) -> None:
    global _current
    _current = ticker.upper()

    print(f"\n{'─' * 50}")
    print(f"  Ticker: {_current}")
    print(f"{'─' * 50}")

    # 1. Discover transcript URL
    transcript_url = find_transcript_url(ticker)

    # 2. Parse quarter/year from slug
    slug = transcript_url.rstrip("/").split("/")[-1]
    quarter, year = _parse_slug(slug)
    _log(f"Quarter: Q{quarter} FY{year}  (from slug: {slug})")

    # 3. Check if file already exists
    out_path = OUTPUT_DIR / _current / f"q{quarter}-{year}-call.md"
    if out_path.exists():
        _log(f"File already exists: {out_path.relative_to(SCRIPT_DIR.parent)} — skipping.")
        _log("Delete the file first if you want to re-fetch.")
        return

    # 4. Download and parse transcript
    title, body = fetch_transcript(transcript_url)
    _log(f"Extracted {len(body):,} chars of transcript")

    # 5. Build and save
    content = build_md(_current, quarter, year, title, transcript_url, body)
    path    = save(_current, quarter, year, content)
    _log(f"Saved → {path.relative_to(SCRIPT_DIR.parent)}  ({path.stat().st_size:,} bytes)")


# ── Main ───────────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    tickers = [t.upper() for t in sys.argv[1:]]
    errors  = []

    for ticker in tickers:
        try:
            fetch_one(ticker)
        except Exception as e:
            print(f"\n  [ERROR] {ticker}: {e}")
            errors.append(ticker)

    print(f"\n{'─' * 50}")
    done = [t for t in tickers if t not in errors]
    if done:
        print(f"  Done:   {', '.join(done)}")
    if errors:
        print(f"  Failed: {', '.join(errors)}")
        print(
            "\n  Tip: If search fails, find the Motley Fool URL manually and run:\n"
            "  python fetch_transcript.py <TICKER>  (after adding URL to the script)\n"
            "  Or paste the transcript into sources/<TICKER>/q<N>-<YEAR>-call.md directly."
        )


if __name__ == "__main__":
    main()
