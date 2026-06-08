#!/usr/bin/env python3
"""
fetch_sources.py — Fetch 10-K + earnings transcript for one or more tickers.

Sources:
  10-K:        SEC EDGAR (always free)
  Transcript:  1. SEC EDGAR 8-K exhibit (companies that file transcript via EDGAR)
               2. Motley Fool search
               3. DuckDuckGo → Motley Fool fallback
               4. Placeholder with manual-paste instructions (if all fail)

Usage:
    python scripts/fetch_sources.py AAPL
    python scripts/fetch_sources.py NVDA TSLA RKLB    # multiple tickers
    python scripts/fetch_sources.py AAPL --10k-only
    python scripts/fetch_sources.py AAPL --transcript-only

Output:
    sources/<TICKER>/10-k-fy<YEAR>.md
    sources/<TICKER>/q<N>-<YEAR>-call.md
"""

import sys
import re
import json
import time
import gzip
import ssl
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError
from urllib.parse import quote_plus

_SSL        = ssl._create_unverified_context()
SCRIPT_DIR  = Path(__file__).parent
OUTPUT_DIR  = SCRIPT_DIR.parent / "sources"

EDGAR_AGENT   = "stock-research-tool potchpurana@gmail.com"
BROWSER_UA    = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)
EDGAR_DELAY   = 0.5    # seconds between EDGAR requests
WEB_DELAY     = 1.5    # seconds between web requests
MAX_ITEM_CHARS = 60_000

_current_ticker = ""

def _log(msg: str):
    print(f"  [{_current_ticker}] {msg}")

def _section(ticker: str, label: str):
    print(f"\n{'─' * 52}")
    print(f"  {ticker}  ·  {label}")
    print(f"{'─' * 52}")


# ══════════════════════════════════════════════════════
# Shared HTTP
# ══════════════════════════════════════════════════════

def _get(url: str, headers: dict) -> str:
    req = Request(url, headers=headers)
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
        raise RuntimeError(f"Network: {url} — {e.reason}") from e

def edgar_get(url: str) -> str:
    return _get(url, {"User-Agent": EDGAR_AGENT, "Accept-Encoding": "gzip, deflate"})

def web_get(url: str, referer: str = "") -> str:
    h = {
        "User-Agent": BROWSER_UA,
        "Accept": "text/html,application/xhtml+xml,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate",
    }
    if referer:
        h["Referer"] = referer
    return _get(url, h)


# ══════════════════════════════════════════════════════
# HTML → plain text
# ══════════════════════════════════════════════════════

from html.parser import HTMLParser

class _StripHTML(HTMLParser):
    _SKIP  = {"script","style","noscript","head","meta","link","nav","footer","aside","form","button"}
    _BLOCK = {"p","div","section","article","h1","h2","h3","h4","h5","h6","li","tr","blockquote","br"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self._d = 0

    def handle_starttag(self, tag, _):
        t = tag.lower()
        if t in self._SKIP:   self._d += 1
        elif self._d == 0 and t in self._BLOCK: self.parts.append("\n")

    def handle_endtag(self, tag):
        t = tag.lower()
        if t in self._SKIP:   self._d = max(0, self._d - 1)
        elif self._d == 0 and t in self._BLOCK: self.parts.append("\n")

    def handle_data(self, data):
        if self._d == 0: self.parts.append(data)

    def result(self) -> str:
        t = "".join(self.parts)
        t = re.sub(r"[ \t]+", " ", t)
        t = re.sub(r"\n{3,}", "\n\n", t)
        return t.strip()

def html_to_text(html: str) -> str:
    p = _StripHTML(); p.feed(html); return p.result()


# ══════════════════════════════════════════════════════
# EDGAR — CIK + filing lookup
# ══════════════════════════════════════════════════════

def get_cik(ticker: str) -> tuple[str, str]:
    """Return (cik_padded, company_name)."""
    _log("Looking up CIK...")
    data = json.loads(edgar_get("https://www.sec.gov/files/company_tickers.json"))
    time.sleep(EDGAR_DELAY)
    for entry in data.values():
        if entry["ticker"] == ticker.upper():
            cik = str(entry["cik_str"]).zfill(10)
            _log(f"CIK {cik}  ({entry['title']})")
            return cik, entry["title"]
    raise RuntimeError(f"Ticker '{ticker}' not found in EDGAR.")

def get_recent_filings(cik: str) -> dict:
    url  = f"https://data.sec.gov/submissions/CIK{cik}.json"
    subs = json.loads(edgar_get(url))
    time.sleep(EDGAR_DELAY)
    return subs


# ══════════════════════════════════════════════════════
# 10-K fetch
# ══════════════════════════════════════════════════════

_10K_PATTERNS = {
    "item1":      r"\n[ \t]*item\s+1[\.\s]+business[^\n]*\n",
    "item1a":     r"\n[ \t]*item\s+1a[\.\s]+risk\s+factors[^\n]*\n",
    "item1b":     r"\n[ \t]*item\s+1b[\.\s]+",
    "item2":      r"\n[ \t]*item\s+2[\.\s]+",
    "item7":      r"\n[ \t]*item\s+7[\.\s]+management",
    "item7a":     r"\n[ \t]*item\s+7a[\.\s]+",
    "item8":      r"\n[ \t]*item\s+8[\.\s]+",
    "signatures": r"\n[ \t]*signatures\b",
}

def _find_all(text: str, pattern: str) -> list[int]:
    return [m.start() for m in re.finditer(pattern, text, re.IGNORECASE)]

def _last(positions: list[int]) -> int | None:
    return positions[-1] if positions else None

def extract_10k_items(text: str) -> dict[str, str]:
    pos = {k: _find_all(text, p) for k, p in _10K_PATTERNS.items()}
    s1  = _last(pos["item1"])
    s1a = _last(pos["item1a"])
    s7  = _last(pos["item7"])
    missing = [n for n, v in [("Item 1", s1),("Item 1A", s1a),("Item 7", s7)] if v is None]
    if missing:
        raise RuntimeError(f"Cannot find: {', '.join(missing)}")

    e1   = s1a
    aft1a = sorted(p for k in ("item1b","item2") for p in pos[k] if p > s1a)
    e1a  = aft1a[0] if aft1a else s7
    aft7  = sorted(p for k in ("item7a","item8","signatures") for p in pos[k] if p > s7)
    e7   = aft7[0] if aft7 else s7 + MAX_ITEM_CHARS

    def clip(s):
        s = s.strip()
        return s if len(s) <= MAX_ITEM_CHARS else s[:MAX_ITEM_CHARS] + f"\n\n[truncated at {MAX_ITEM_CHARS:,} chars]"

    return {"item1": clip(text[s1:e1]), "item1a": clip(text[s1a:e1a]), "item7": clip(text[s7:e7])}

def fetch_10k(ticker: str, subs: dict) -> Path:
    company = subs.get("name","Unknown")
    recent  = subs["filings"]["recent"]
    forms   = recent["form"]
    accnums = recent["accessionNumber"]
    fdates  = recent["filingDate"]
    rpdates = recent.get("reportDate", [""] * len(forms))
    pdocs   = recent.get("primaryDocument", [""] * len(forms))
    cik_int = int(subs["cik"])

    idx = next((i for i, f in enumerate(forms) if f == "10-K"), None)
    if idx is None:
        raise RuntimeError("No 10-K found.")

    acc       = accnums[idx]
    acc_nd    = acc.replace("-","")
    rep_date  = rpdates[idx] or fdates[idx]
    fy        = rep_date[:4]
    pdoc      = pdocs[idx]

    _log(f"10-K filed {fdates[idx]}  (period {rep_date})")

    # Resolve document URL
    if pdoc:
        doc_url = f"https://www.sec.gov/Archives/edgar/data/{cik_int}/{acc_nd}/{pdoc}"
    else:
        idx_url  = f"https://www.sec.gov/Archives/edgar/data/{cik_int}/{acc_nd}/{acc_nd}-index.htm"
        idx_html = edgar_get(idx_url); time.sleep(EDGAR_DELAY)
        hrefs    = re.findall(rf'href="(/Archives/edgar/data/{cik_int}/{acc_nd}/[^"]+\.htm)"', idx_html, re.IGNORECASE)
        hrefs    = [h for h in hrefs if "index" not in Path(h).name.lower()]
        if not hrefs: raise RuntimeError("Cannot find 10-K document in filing index.")
        doc_url  = "https://www.sec.gov" + hrefs[0]

    _log(f"Downloading {doc_url.split('/')[-1]}...")
    html = edgar_get(doc_url); time.sleep(EDGAR_DELAY)

    _log(f"Extracting items from {len(html):,} chars...")
    text  = html_to_text(html)
    items = extract_10k_items(text)

    content = (
        f"---\n"
        f"ticker: {ticker}\n"
        f"source_type: 10k_excerpt\n"
        f"fiscal_year: FY{fy}\n"
        f"filing_date: {fdates[idx]}\n"
        f"source_url: {doc_url}\n"
        f"sections: Item 1 (Business), Item 1A (Risk Factors), Item 7 (MD&A)\n"
        f"---\n\n"
        f"# {company} 10-K FY{fy} (excerpt)\n\n"
        f"{items['item1']}\n\n"
        f"{items['item1a']}\n\n"
        f"{items['item7']}\n"
    )
    out = OUTPUT_DIR / ticker / f"10-k-fy{fy}.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(content, encoding="utf-8")
    _log(f"Saved → {out.relative_to(SCRIPT_DIR.parent)}  ({out.stat().st_size:,} bytes)")
    return out


# ══════════════════════════════════════════════════════
# Transcript — Strategy 1: EDGAR 8-K exhibit
# ══════════════════════════════════════════════════════

def _find_transcript_in_8k(subs: dict, ticker: str) -> str | None:
    """
    Look for a recent 8-K that has a transcript exhibit.
    Companies that file transcripts via EDGAR use Item 7.01 +
    an exhibit whose description/name contains 'transcript'.
    Returns the URL of the exhibit document, or None.
    """
    recent  = subs["filings"]["recent"]
    forms   = recent["form"]
    accnums = recent["accessionNumber"]
    fdates  = recent["filingDate"]
    cik_int = int(subs["cik"])

    # Check only 8-K filings from last 180 days
    from datetime import datetime, timezone, timedelta
    cutoff  = datetime.now(timezone.utc) - timedelta(days=180)

    for i, form in enumerate(forms):
        if form not in ("8-K", "8-K/A"):
            continue
        try:
            fdate = datetime.strptime(fdates[i], "%Y-%m-%d").replace(tzinfo=timezone.utc)
        except ValueError:
            continue
        if fdate < cutoff:
            break  # filings are newest-first; stop when too old

        acc    = accnums[i].replace("-","")
        idx_url = f"https://data.sec.gov/Archives/edgar/data/{cik_int}/{acc}/{accnums[i]}-index.json"

        try:
            idx_data = json.loads(edgar_get(idx_url))
            time.sleep(EDGAR_DELAY)
        except Exception:
            continue

        docs = idx_data.get("documents", [])
        for doc in docs:
            desc = (doc.get("description","") + " " + doc.get("name","")).lower()
            if "transcript" in desc:
                doc_url = (
                    f"https://www.sec.gov/Archives/edgar/data/{cik_int}/{acc}/{doc['name']}"
                )
                _log(f"Found transcript exhibit in 8-K ({fdates[i]}): {doc['name']}")
                return doc_url

    return None

def _fetch_edgar_transcript(doc_url: str) -> str:
    """Download and extract text from an EDGAR transcript exhibit (htm/txt)."""
    _log(f"Downloading EDGAR exhibit: {doc_url.split('/')[-1]}")
    raw = edgar_get(doc_url)
    time.sleep(EDGAR_DELAY)
    if "<html" in raw.lower() or "<!doctype" in raw.lower():
        return html_to_text(raw)
    return raw  # plain text


# ══════════════════════════════════════════════════════
# Transcript — Strategy 2 & 3: Motley Fool
# ══════════════════════════════════════════════════════

_FOOL_RE = re.compile(
    r"https://www\.fool\.com/earnings/call-transcripts/"
    r"(\d{4})/(\d{2})/(\d{2})/([\w-]+earnings-call[\w-]*)/"
)

def _find_fool_urls(html: str, ticker: str) -> list[str]:
    matches = _FOOL_RE.findall(html)
    seen: set[str] = set()
    results = []
    for y, mo, d, slug in matches:
        url = f"https://www.fool.com/earnings/call-transcripts/{y}/{mo}/{d}/{slug}/"
        if url not in seen:
            seen.add(url); results.append((y, mo, d, url))
    results.sort(key=lambda x: x[:3], reverse=True)
    tl = ticker.lower()
    urls = [r[3] for r in results]
    relevant = [u for u in urls if tl in u.lower()]
    return relevant or urls[:3]

def _search_fool(ticker: str) -> str | None:
    q   = quote_plus(f"{ticker} earnings call transcript")
    url = f"https://www.fool.com/search/?q={q}&source=eustranscripts"
    _log(f"Searching Motley Fool...")
    try:
        html = web_get(url, referer="https://www.fool.com/")
        time.sleep(WEB_DELAY)
        urls = _find_fool_urls(html, ticker)
        if urls: _log(f"Found: {urls[0]}"); return urls[0]
    except Exception as e:
        _log(f"Fool search error: {e}")
    return None

def _search_ddg(ticker: str) -> str | None:
    q   = quote_plus(f"site:fool.com/earnings/call-transcripts {ticker} earnings call transcript")
    url = f"https://html.duckduckgo.com/html/?q={q}"
    _log(f"DuckDuckGo fallback...")
    try:
        html = web_get(url, referer="https://duckduckgo.com/")
        time.sleep(WEB_DELAY)
        urls = _find_fool_urls(html, ticker)
        if urls: _log(f"Found: {urls[0]}"); return urls[0]
    except Exception as e:
        _log(f"DDG search error: {e}")
    return None

def _parse_fool_slug(slug: str) -> tuple[str,str]:
    m = re.search(r"-q(\d)-(\d{4})-earnings", slug, re.IGNORECASE)
    if m: return m.group(1), m.group(2)
    q = re.search(r"q(\d)", slug, re.IGNORECASE)
    y = re.search(r"(\d{4})", slug)
    return (q.group(1) if q else "?"), (y.group(1) if y else "????")

def _extract_fool_body(html: str) -> str:
    text  = html_to_text(html)
    lines = text.split("\n")
    start = 0
    for i, line in enumerate(lines):
        s = line.strip()
        if len(s) > 80 and any(k in s.lower() for k in ["quarter","revenue","earnings","fiscal","thank you","thanks"]):
            start = i; break
    end = len(lines)
    for i in range(len(lines)-1, start, -1):
        s = lines[i].strip().lower()
        if any(k in s for k in ["related articles","fool.com premium","motley fool","sign up","subscribe","disclosures"]):
            end = i; break
    body = "\n".join(lines[start:end]).strip()
    return re.sub(r"\n{3,}", "\n\n", body)

def _fetch_fool_transcript(url: str) -> tuple[str,str,str,str]:
    """Returns (title, body, quarter, year)."""
    _log(f"Downloading transcript: {url}")
    html = web_get(url, referer="https://www.fool.com/")
    time.sleep(WEB_DELAY)

    title_m = re.search(r"<title>([^<]+)</title>", html, re.IGNORECASE)
    title   = re.sub(r"\s*\|.*$","", title_m.group(1).strip() if title_m else "Earnings Call Transcript")

    body = _extract_fool_body(html)
    if len(body) < 200:
        raise RuntimeError(f"Transcript body too short ({len(body)} chars) — page may require login.")

    slug    = url.rstrip("/").split("/")[-1]
    q, year = _parse_fool_slug(slug)
    return title, body, q, year


# ══════════════════════════════════════════════════════
# Transcript — save or placeholder
# ══════════════════════════════════════════════════════

def _save_transcript(ticker: str, quarter: str, year: str,
                     title: str, source_url: str, body: str) -> Path:
    content = (
        f"---\n"
        f"ticker: {ticker}\n"
        f"source_type: earnings_call_transcript\n"
        f"quarter: Q{quarter} FY{year}\n"
        f"source_url: {source_url}\n"
        f"---\n\n"
        f"# {title}\n\n"
        f"{body}\n"
    )
    out = OUTPUT_DIR / ticker / f"q{quarter}-{year}-call.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(content, encoding="utf-8")
    return out

def _save_placeholder(ticker: str) -> Path:
    """
    Create a placeholder file when transcript cannot be fetched automatically.
    Explains exactly where to get the transcript and how to paste it.
    """
    from datetime import datetime
    year = datetime.now().year

    content = (
        f"---\n"
        f"ticker: {ticker}\n"
        f"source_type: earnings_call_transcript\n"
        f"quarter: PLACEHOLDER — paste transcript below\n"
        f"source_url: (add URL after pasting)\n"
        f"---\n\n"
        f"# {ticker} Earnings Call Transcript — PLACEHOLDER\n\n"
        f"> ⚠️ **Transcript not fetched automatically.**\n"
        f"> Earnings call transcripts are not freely available via API.\n"
        f"> Please paste the transcript manually using one of the sources below.\n\n"
        f"---\n\n"
        f"## How to get the transcript\n\n"
        f"**Option 1 — Motley Fool (free, registration may be required)**\n"
        f"1. Go to: https://www.fool.com/earnings/call-transcripts/\n"
        f"2. Search for: `{ticker} earnings call transcript`\n"
        f"3. Open the latest transcript\n"
        f"4. Copy the full text and paste below\n\n"
        f"**Option 2 — Seeking Alpha (free tier available)**\n"
        f"1. Go to: https://seekingalpha.com/symbol/{ticker}/earnings/transcripts\n"
        f"2. Open the latest transcript\n"
        f"3. Copy and paste below\n\n"
        f"**Option 3 — SEC EDGAR 8-K (earnings press release only, no call)**\n"
        f"1. Go to: https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&type=8-K&dateb=&owner=include&count=10&search_text=&ticker={ticker}\n"
        f"2. Open the latest 8-K → look for Exhibit 99.1 or 99.2\n"
        f"3. Note: 8-K has the earnings release (tables/numbers) but NOT the full call transcript\n\n"
        f"---\n\n"
        f"## Paste transcript here\n\n"
        f"<!-- DELETE everything above this line after pasting, keep the frontmatter -->\n\n"
        f"[PASTE TRANSCRIPT TEXT HERE]\n"
    )

    # Try to find the right quarter from any existing transcript files
    out_dir = OUTPUT_DIR / ticker
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"q?-{year}-call.md"
    # Use a safe filename
    out = out_dir / f"transcript-placeholder.md"
    out.write_text(content, encoding="utf-8")
    return out


def fetch_transcript(ticker: str, subs: dict) -> Path:
    """Try all strategies, fall back to placeholder."""

    # Strategy 1: EDGAR 8-K exhibit
    _log("Strategy 1: EDGAR 8-K transcript exhibit...")
    edgar_url = _find_transcript_in_8k(subs, ticker)
    if edgar_url:
        try:
            body  = _fetch_edgar_transcript(edgar_url)
            # Derive quarter/year from 8-K filing date
            recent = subs["filings"]["recent"]
            forms  = recent["form"]
            fdates = recent["filingDate"]
            from datetime import datetime, timezone, timedelta
            cutoff = datetime.now(timezone.utc) - timedelta(days=180)
            q, year = "?", str(datetime.now().year)
            for i, f in enumerate(forms):
                if f in ("8-K","8-K/A"):
                    fd = datetime.strptime(fdates[i], "%Y-%m-%d").replace(tzinfo=timezone.utc)
                    if fd >= cutoff:
                        # Try to infer quarter from month
                        mo = fd.month
                        q  = str((mo - 1) // 3 + 1)
                        year = str(fd.year)
                        break
            title = f"{ticker} Earnings Call Transcript Q{q} FY{year} (via EDGAR 8-K)"
            out   = _save_transcript(ticker, q, year, title, edgar_url, body)
            _log(f"Saved → {out.relative_to(SCRIPT_DIR.parent)}  ({out.stat().st_size:,} bytes)")
            return out
        except Exception as e:
            _log(f"EDGAR transcript failed: {e}")

    # Strategy 2: Motley Fool direct search
    _log("Strategy 2: Motley Fool search...")
    fool_url = _search_fool(ticker)

    # Strategy 3: DuckDuckGo fallback
    if not fool_url:
        fool_url = _search_ddg(ticker)

    if fool_url:
        try:
            title, body, q, year = _fetch_fool_transcript(fool_url)
            out = _save_transcript(ticker, q, year, title, fool_url, body)
            _log(f"Saved → {out.relative_to(SCRIPT_DIR.parent)}  ({out.stat().st_size:,} bytes)")
            return out
        except Exception as e:
            _log(f"Motley Fool fetch failed: {e}")

    # Strategy 4: Placeholder
    _log("All strategies failed — creating placeholder with manual instructions.")
    out = _save_placeholder(ticker)
    _log(f"Placeholder → {out.relative_to(SCRIPT_DIR.parent)}")
    _log("Open the placeholder and paste transcript from Motley Fool or Seeking Alpha.")
    return out


# ══════════════════════════════════════════════════════
# Per-ticker orchestration
# ══════════════════════════════════════════════════════

def run_ticker(ticker: str, do_10k: bool, do_transcript: bool) -> list[str]:
    global _current_ticker
    _current_ticker = ticker

    errors = []

    try:
        _section(ticker, "CIK lookup")
        cik, _ = get_cik(ticker)
        subs    = get_recent_filings(cik)
    except Exception as e:
        print(f"\n  [ERROR] {ticker}: CIK/filing lookup failed: {e}")
        return [f"{ticker}: CIK lookup failed"]

    if do_10k:
        _section(ticker, "10-K")
        try:
            fetch_10k(ticker, subs)
        except Exception as e:
            _log(f"10-K failed: {e}")
            errors.append(f"{ticker} 10-K: {e}")

    if do_transcript:
        _section(ticker, "Earnings transcript")
        try:
            fetch_transcript(ticker, subs)
        except Exception as e:
            _log(f"Transcript failed: {e}")
            errors.append(f"{ticker} transcript: {e}")

    return errors


# ══════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════

def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__); sys.exit(1)

    flags    = {a for a in args if a.startswith("--")}
    tickers  = [a.upper() for a in args if not a.startswith("--")]

    if not tickers:
        print("Error: no tickers provided."); sys.exit(1)

    do_10k        = "--transcript-only" not in flags
    do_transcript = "--10k-only"        not in flags

    mode = "10-K only" if not do_transcript else ("transcript only" if not do_10k else "10-K + transcript")
    print(f"\nfetch_sources.py  ·  {mode}  ·  tickers: {', '.join(tickers)}")

    all_errors: list[str] = []
    for ticker in tickers:
        errs = run_ticker(ticker, do_10k, do_transcript)
        all_errors.extend(errs)

    print(f"\n{'═' * 52}")
    done = [t for t in tickers if not any(e.startswith(t) for e in all_errors)]
    if done:   print(f"  ✓ Done:   {', '.join(done)}")
    if all_errors:
        print(f"  ✗ Issues:")
        for e in all_errors:
            print(f"    · {e}")
    print()


if __name__ == "__main__":
    main()
