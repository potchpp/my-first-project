#!/usr/bin/env python3
"""Find companies named across holdings' research that have no brief of their own.

Reads the graphify knowledge graph plus a cached entity-type classification and
reports non-held companies ranked by how many different holdings mention them.
Never reads portfolio/ — holdings are inferred from briefs/ filenames.
"""
import json, re, sys, collections, pathlib, argparse

ROOT = pathlib.Path(__file__).resolve().parent.parent
GRAPH = ROOT / "graphify-out" / "graph.json"
TYPES = ROOT / "data" / "entity-types.json"
BRIEFS = ROOT / "briefs"


# Name variants that refer to a company we already hold but don't normalize to it.
ALIASES = {
    "tsmc": "taiwansemiconductormanufacturing",
    "google": "alphabet",
    "googl": "alphabet",
    "metaplatforms": "meta",
    "sandisk": "sndk",
    "berkshirehathaway": "brkb",
}


def norm(s):
    s = re.sub(r"\s*\(.*?\)", "", s or "")
    s = re.sub(r"[^a-z0-9]", "", s.lower())
    s = re.sub(r"^the", "", s)
    s = re.sub(r"(inc|corp|corporation|company|co|ltd|limited|holdings?|group|plc|nv|sa|ag|as)$", "", s)
    return ALIASES.get(s, s)


def held_keys():
    """Tickers and company names we already research, from briefs/ only."""
    keys = set()
    for p in BRIEFS.glob("*.md"):
        keys.add(norm(p.stem))
        txt = p.read_text(encoding="utf-8", errors="ignore")
        for pat in (r"^company:\s*(.+)$", r"^#\s*[A-Z\.\-]+\s*[—\-–]\s*(.+)$"):
            m = re.search(pat, txt, re.M)
            if m:
                keys.add(norm(m.group(1)))
    keys.discard("")
    return keys


def owner(source_file):
    """Which ticker's research a node came from."""
    sf = str(source_file or "").replace("\\", "/")
    m = re.match(r"briefs/([A-Za-z0-9\.\-]+)\.md", sf) or re.match(r"sources/([A-Za-z0-9\.\-]+)/", sf)
    return m.group(1).upper().replace("-", "") if m else None


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--min-mentions", type=int, default=1, help="minimum distinct holdings naming it")
    ap.add_argument("--include-private", action="store_true", help="also show private/unlisted companies")
    ap.add_argument("--all-kinds", action="store_true", help="ignore the company filter")
    args = ap.parse_args(argv)

    for f in (GRAPH, TYPES):
        if not f.exists():
            print(f"error: missing {f.relative_to(ROOT)}", file=sys.stderr)
            return 1

    types = {norm(e["label"]): e for e in json.loads(TYPES.read_text(encoding="utf-8"))}
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    held = held_keys()
    # Native tickers make ownership exact: AWS carries AMZN, SpaceX carries SPCX.
    held_tickers = {re.sub(r"[^A-Z0-9]", "", p.stem.upper()) for p in BRIEFS.glob("*.md")}

    mentions = collections.defaultdict(set)
    display = {}
    for n in graph.get("nodes", []):
        o = owner(n.get("source_file"))
        label = (n.get("label") or "").strip()
        if not o or not label:
            continue
        k = norm(label)
        if not k or k in held:
            continue
        # Prefer the entity_type the extractor put on the node; fall back to the
        # cached classification for nodes extracted before typing existed.
        if n.get("entity_type"):
            ent = {"kind": n["entity_type"], "label": label,
                   "ticker": n.get("ticker"), "private": bool(n.get("private"))}
        else:
            c = types.get(k)
            if c is None:
                continue
            ent = {"kind": c.get("kind"), "label": c.get("label", label),
                   "ticker": c.get("ticker"), "private": bool(c.get("private"))}
        tk = re.sub(r"[^A-Z0-9]", "", (ent["ticker"] or "").upper().split(".")[0])
        if tk and tk in held_tickers:
            continue
        if not args.all_kinds and ent["kind"] != "company":
            continue
        if ent["private"] and not args.include_private:
            continue
        mentions[k].add(o)
        # Keep whichever record carries a ticker.
        if k not in display or (ent["ticker"] and not display[k].get("ticker")):
            display[k] = ent

    rows = [(len(v), display[k].get("ticker") or "—", display[k]["label"], sorted(v))
            for k, v in mentions.items() if len(v) >= args.min_mentions]
    rows.sort(key=lambda r: (-r[0], r[1]))

    if not rows:
        print("No undercover companies found at this threshold.")
        return 0

    print(f"{'#':>3}  {'TICKER':<10} {'COMPANY':<38} NAMED IN THE RESEARCH OF")
    print("-" * 100)
    for cnt, tic, label, owners in rows:
        print(f"{cnt:>3}  {tic:<10} {label[:38]:<38} {', '.join(owners)}")
    note = "including private/unlisted" if args.include_private else "private/unlisted hidden (use --include-private)"
    print(f"\n{len(rows)} candidates, {note}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
