#!/usr/bin/env python3
"""
fetch_10k.py — Downloads the latest 10-K from SEC EDGAR for a given ticker,
               extracts Item 1 (Business), Item 1A (Risk Factors), and
               Item 7 (MD&A), and saves to sources/<TICKER>/10-k-fy<YEAR>.md

Usage:
    python fetch_10k.py AAPL
    python fetch_10k.py NVDA TSLA          # multiple tickers

Requirements: Python 3.10+ stdlib only (no pip install needed)
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
from html.parser import HTMLParser

# macOS Python often ships without root certs configured — use unverified context
_SSL = ssl._create_unverified_context()

# ── Config ─────────────────────────────────────────────────────────────────
USER_AGENT    = "stock-research-tool potchpurana@gmail.com"
REQUEST_DELAY = 0.5          # seconds between EDGAR requests (rate-limit courtesy)
MAX_PER_ITEM  = 60_000       # character cap per item section
SCRIPT_DIR    = Path(__file__).parent
OUTPUT_DIR    = SCRIPT_DIR.parent / "sources"


# ── HTTP ───────────────────────────────────────────────────────────────────

def edgar_get(url: str, as_text: bool = False) -> bytes | str:
    """GET from EDGAR with required User-Agent; handles gzip transparently."""
    req = Request(url, headers={
        "User-Agent": USER_AGENT,
        "Accept-Encoding": "gzip, deflate",
    })
    try:
        with urlopen(req, timeout=30, context=_SSL) as resp:
            raw = resp.read()
            if resp.info().get("Content-Encoding") == "gzip" or raw[:2] == b"\x1f\x8b":
                raw = gzip.decompress(raw)
    except HTTPError as e:
        raise RuntimeError(f"HTTP {e.code}: {url}") from e
    except URLError as e:
        raise RuntimeError(f"Network error: {url} — {e.reason}") from e

    if not as_text:
        return raw
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return raw.decode("latin-1", errors="replace")


# ── EDGAR lookups ──────────────────────────────────────────────────────────

def get_cik(ticker: str) -> str:
    """Return zero-padded 10-digit CIK string for ticker, or raise."""
    _log("Looking up CIK...")
    data = json.loads(edgar_get("https://www.sec.gov/files/company_tickers.json"))
    time.sleep(REQUEST_DELAY)

    for entry in data.values():
        if entry["ticker"] == ticker.upper():
            cik = str(entry["cik_str"]).zfill(10)
            _log(f"CIK {cik}  ({entry['title']})")
            return cik

    raise RuntimeError(f"Ticker '{ticker}' not found in EDGAR. Check spelling.")


def get_latest_10k(cik: str) -> dict:
    """Return metadata for the most recent 10-K filing."""
    _log("Fetching filing history...")
    url = f"https://data.sec.gov/submissions/CIK{cik}.json"
    subs = json.loads(edgar_get(url))
    time.sleep(REQUEST_DELAY)

    company_name = subs.get("name", "Unknown Company")
    recent       = subs["filings"]["recent"]
    forms        = recent["form"]
    accessions   = recent["accessionNumber"]
    filing_dates = recent["filingDate"]
    report_dates = recent.get("reportDate", [""] * len(forms))
    primary_docs = recent.get("primaryDocument", [""] * len(forms))

    for i, form in enumerate(forms):
        if form == "10-K":
            acc         = accessions[i]
            acc_nodash  = acc.replace("-", "")
            report_date = report_dates[i] or filing_dates[i]
            fiscal_year = report_date[:4]          # YYYY from report period end
            _log(f"Latest 10-K filed {filing_dates[i]} (period {report_date})")
            return {
                "company_name": company_name,
                "accession":     acc,
                "acc_nodash":    acc_nodash,
                "primary_doc":   primary_docs[i],
                "filing_date":   filing_dates[i],
                "fiscal_year":   fiscal_year,
                "cik_int":       int(cik),
            }

    raise RuntimeError(f"No 10-K found for CIK {cik}.")


def resolve_doc_url(info: dict) -> str:
    """Return the URL of the main 10-K HTML document."""
    cik   = info["cik_int"]
    nd    = info["acc_nodash"]
    pdoc  = info["primary_doc"]

    if pdoc:
        url = f"https://www.sec.gov/Archives/edgar/data/{cik}/{nd}/{pdoc}"
        _log(f"Primary document: {pdoc}")
        return url

    # Fall back: parse filing index HTML to find first .htm link
    _log("Parsing filing index to find document URL...")
    index_url = f"https://www.sec.gov/Archives/edgar/data/{cik}/{nd}/{nd}-index.htm"
    index_html = edgar_get(index_url, as_text=True)
    time.sleep(REQUEST_DELAY)

    hrefs = re.findall(
        rf'href="(/Archives/edgar/data/{cik}/{nd}/[^"]+\.htm)"',
        index_html,
        re.IGNORECASE,
    )
    hrefs = [h for h in hrefs if "index" not in Path(h).name.lower()]
    if hrefs:
        return "https://www.sec.gov" + hrefs[0]

    raise RuntimeError("Cannot find 10-K HTML document in filing index.")


# ── HTML → plain text ──────────────────────────────────────────────────────

class _StripHTML(HTMLParser):
    """Converts HTML to plain text preserving block-level line breaks."""

    _SKIP  = {"script", "style", "head", "noscript", "meta", "link"}
    _BLOCK = {
        "p", "div", "section", "article", "header", "footer",
        "h1", "h2", "h3", "h4", "h5", "h6",
        "tr", "li", "blockquote", "table",
    }

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self._depth = 0       # depth inside skip-tags

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
    p = _StripHTML()
    p.feed(html)
    return p.result()


# ── Item extraction ─────────────────────────────────────────────────────────

# Each pattern anchors to a newline so it won't match mid-sentence
_PATTERNS = {
    "item1":      r"\n[ \t]*item\s+1[\.\s]+business[^\n]*\n",
    "item1a":     r"\n[ \t]*item\s+1a[\.\s]+risk\s+factors[^\n]*\n",
    "item1b":     r"\n[ \t]*item\s+1b[\.\s]+",
    "item2":      r"\n[ \t]*item\s+2[\.\s]+",
    "item7":      r"\n[ \t]*item\s+7[\.\s]+management",
    "item7a":     r"\n[ \t]*item\s+7a[\.\s]+",
    "item8":      r"\n[ \t]*item\s+8[\.\s]+",
    "signatures": r"\n[ \t]*signatures\b",
}


def _all_positions(text: str, key: str) -> list[int]:
    return [m.start() for m in re.finditer(_PATTERNS[key], text, re.IGNORECASE)]


def _last(positions: list[int]) -> int | None:
    """Last occurrence = body (not Table of Contents)."""
    return positions[-1] if positions else None


def extract_items(text: str) -> dict[str, str]:
    """
    Find and extract Item 1, Item 1A, Item 7 from plain-text 10-K.
    Uses the LAST occurrence of each heading to skip the Table of Contents.
    """
    pos = {k: _all_positions(text, k) for k in _PATTERNS}

    start1  = _last(pos["item1"])
    start1a = _last(pos["item1a"])
    start7  = _last(pos["item7"])

    missing = [name for name, start in [("Item 1", start1), ("Item 1A", start1a), ("Item 7", start7)] if start is None]
    if missing:
        raise RuntimeError(f"Could not find section(s) in document: {', '.join(missing)}")

    # Item 1 ends at Item 1A
    end1 = start1a

    # Item 1A ends at Item 1B or Item 2 (whichever comes first after Item 1A)
    after_1a = sorted(p for k in ("item1b", "item2") for p in pos[k] if p > start1a)
    end1a = after_1a[0] if after_1a else start7

    # Item 7 ends at Item 7A, Item 8, or Signatures
    after_7 = sorted(p for k in ("item7a", "item8", "signatures") for p in pos[k] if p > start7)
    end7 = after_7[0] if after_7 else start7 + MAX_PER_ITEM

    def clip(s: str) -> str:
        s = s.strip()
        if len(s) > MAX_PER_ITEM:
            s = s[:MAX_PER_ITEM] + f"\n\n[... truncated at {MAX_PER_ITEM:,} chars — see source URL for full text ...]"
        return s

    return {
        "item1":  clip(text[start1:end1]),
        "item1a": clip(text[start1a:end1a]),
        "item7":  clip(text[start7:end7]),
    }


# ── Output ─────────────────────────────────────────────────────────────────

def build_md(ticker: str, info: dict, items: dict, doc_url: str) -> str:
    fy   = f"FY{info['fiscal_year']}"
    name = info["company_name"]
    return f"""---
ticker: {ticker.upper()}
source_type: 10k_excerpt
fiscal_year: {fy}
filing_date: {info["filing_date"]}
source_url: {doc_url}
sections: Item 1 (Business), Item 1A (Risk Factors excerpt), Item 7 (MD&A excerpt)
---

# {name} 10-K {fy} (excerpt)

{items["item1"]}

{items["item1a"]}

{items["item7"]}
"""


def save(ticker: str, fiscal_year: str, content: str) -> Path:
    out_dir = OUTPUT_DIR / ticker.upper()
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"10-k-fy{fiscal_year}.md"
    path.write_text(content, encoding="utf-8")
    return path


# ── Logging helper ─────────────────────────────────────────────────────────

_current_ticker = ""

def _log(msg: str):
    print(f"  [{_current_ticker}] {msg}")


# ── Per-ticker pipeline ────────────────────────────────────────────────────

def fetch_one(ticker: str) -> None:
    global _current_ticker
    _current_ticker = ticker.upper()

    print(f"\n{'─' * 50}")
    print(f"  Ticker: {_current_ticker}")
    print(f"{'─' * 50}")

    cik      = get_cik(ticker)
    info     = get_latest_10k(cik)
    doc_url  = resolve_doc_url(info)

    _log(f"Downloading document ({doc_url.split('/')[-1]})...")
    html = edgar_get(doc_url, as_text=True)
    time.sleep(REQUEST_DELAY)

    _log(f"Parsing HTML ({len(html):,} chars)...")
    text = html_to_text(html)
    _log(f"Plain text: {len(text):,} chars")

    _log("Extracting Item 1, 1A, 7...")
    items = extract_items(text)
    _log(f"Item 1:  {len(items['item1']):,} chars")
    _log(f"Item 1A: {len(items['item1a']):,} chars")
    _log(f"Item 7:  {len(items['item7']):,} chars")

    content = build_md(_current_ticker, info, items, doc_url)
    path    = save(_current_ticker, info["fiscal_year"], content)

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
        print(f"  Done: {', '.join(done)}")
    if errors:
        print(f"  Failed: {', '.join(errors)}")


if __name__ == "__main__":
    main()
