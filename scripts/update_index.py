#!/usr/bin/env python3
"""
update_index.py — regenerates briefs/index.json from all briefs/*.md files.

Called by Claude Code PostToolUse hook (stdin = hook JSON), or directly:
  python3 scripts/update_index.py
  python3 scripts/update_index.py briefs/AAPL.md   ← also accepts file arg (ignored, scans all)
"""

import sys
import re
import json
import os
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
BRIEFS_DIR   = PROJECT_ROOT / "briefs"
INDEX_JSON   = BRIEFS_DIR / "index.json"


# ─── Parse one brief ─────────────────────────────────────────────────────────

def parse_brief(md_path: Path) -> dict:
    content = md_path.read_text(encoding="utf-8")

    # # AAPL — Apple Inc.
    m = re.match(r"^# ([A-Z0-9]+)\s*[—–\-]+\s*(.+)$", content, re.MULTILINE)
    if not m:
        raise ValueError(f"Cannot parse heading in {md_path}")
    ticker       = m.group(1).strip()
    company_name = m.group(2).strip()

    # *Brief generated: 2026-06-07 | ...*
    dm   = re.search(r"Brief generated:\s*(\d{4}-\d{2}-\d{2})", content)
    date = dm.group(1) if dm else "unknown"

    # First paragraph after snapshot heading
    preview = ""
    for pat in [
        r"## What the company does\s*\n+([\s\S]+?)(?=\n---|\n##)",
        r"## 1\. Company snapshot[^\n]*\n+([\s\S]+?)(?=\n---|\n##)",
        r"## Company snapshot[^\n]*\n+([\s\S]+?)(?=\n---|\n##)",
    ]:
        pm = re.search(pat, content)
        if pm:
            text = pm.group(1).strip()
            text = re.sub(r"\*+", "", text)
            text = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", text)
            text = re.sub(r"\s+", " ", text).strip()
            if len(text) > 220:
                cut = text[:220].rfind(".")
                text = text[: cut + 1] if cut > 120 else text[:220] + "..."
            preview = text
            break

    # has_source: sources/<TICKER>/ exists and has at least one file
    sources_dir = PROJECT_ROOT / "sources" / ticker
    has_source = sources_dir.is_dir() and any(sources_dir.iterdir())

    # stale: brief date > 90 days ago
    stale = False
    if date != "unknown":
        from datetime import datetime, timezone
        try:
            brief_date = datetime.strptime(date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
            days_old = (datetime.now(timezone.utc) - brief_date).days
            stale = days_old > 120
        except ValueError:
            pass

    return {"ticker": ticker, "name": company_name, "date": date,
            "preview": preview, "has_source": has_source, "stale": stale}


# ─── Rebuild index.json ───────────────────────────────────────────────────────

def rebuild_index() -> list[str]:
    """Scan all briefs/*.md and write briefs/index.json. Returns list of changed tickers (empty = no change)."""
    old_entries = {}
    if INDEX_JSON.exists():
        try:
            for e in json.loads(INDEX_JSON.read_text(encoding="utf-8")):
                old_entries[e["ticker"]] = e
        except Exception:
            pass

    entries = []
    for md_path in sorted(BRIEFS_DIR.glob("*.md")):
        try:
            entries.append(parse_brief(md_path))
        except Exception as e:
            print(f"  skip {md_path.name}: {e}", file=sys.stderr)

    new_json = json.dumps(entries, ensure_ascii=False, indent=2)
    if INDEX_JSON.exists() and INDEX_JSON.read_text(encoding="utf-8") == new_json:
        return []

    # Find which tickers actually changed
    new_map = {e["ticker"]: e for e in entries}
    changed = [t for t, v in new_map.items() if old_entries.get(t) != v]
    changed += [t for t in old_entries if t not in new_map]  # deleted

    INDEX_JSON.write_text(new_json, encoding="utf-8")
    return changed or [e["ticker"] for e in entries]  # fallback: list all


# ─── Git ─────────────────────────────────────────────────────────────────────

def git_push(changed_tickers: list[str]):
    os.chdir(PROJECT_ROOT)
    subprocess.run(["git", "add", "briefs/"], check=True)
    label = ", ".join(changed_tickers) if changed_tickers else "briefs"
    result = subprocess.run(
        ["git", "commit", "-m", f"Auto-update: {label} → index.json"],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        if "nothing to commit" in result.stdout + result.stderr:
            return
        raise RuntimeError(result.stderr)
    subprocess.run(["git", "push", "origin", "main"], check=True)


# ─── Main ────────────────────────────────────────────────────────────────────

def main():
    try:
        changed = rebuild_index()
        if changed:
            git_push(changed)
            label = ", ".join(changed)
            print(json.dumps({
                "systemMessage": f"✓ {label} → index.json updated → pushed to Vercel"
            }))
        # no change = silent exit
    except Exception as e:
        print(f"update_index error: {e}", file=sys.stderr)
        sys.exit(0)


if __name__ == "__main__":
    main()
