# Blueprint: free "news spike" trigger for the daily /deep check

**Objective.** Add a fourth trigger to the daily check (`scripts/needs_deep.py`): flag a ticker when today's news
volume about the company is far above its own normal. Free only, no account, no key.

**Why not X.** X API has had no free tier for new developers since Feb 2026 (pay-per-use, $0.005 per count request).
The user asked for free only, so the source is **Google News RSS** (`https://news.google.com/rss/search`), queried by
company name. Verified 2026-10-01: returns HTTP 200 with `<item>` entries, no key; each response is **capped at
100 items** (1-day: Rocket Lab 53, Atlassian 10; Nvidia, Apple, Tesla saturate at 100).

**Mode.** Direct: the user works on `main`, commits locally, pushes when asked. No branches or PRs.
**Model tier:** default (Sonnet) for every step. **Status:** reviewed once (adversarial, Opus); all findings applied.

**Invariants (check after every step)**
- `python3 scripts/test_holdings_map.py` passes; the existing `NeedsDeepTests` passes unchanged.
- `grep -c '"portfolio":' index.html graphify-out/holdings-map.html` prints 0 for both.
- `git ls-files portfolio | wc -l` prints 0.
- **Counts only:** no headline, text, or link from the feed is stored, printed, or passed to an agent.
- A news failure never stops the other three triggers, and the daily run stays under about 3 minutes.

**Dependency graph** (serial; each step uses the previous one)
```
Step 1 (names + fetch) ──► Step 2 (history, rule, wire-in) ──► Step 3 (live run + scheduled task)
```

---

## Step 1: Company-name queries and a bounded fetch

**Context brief.** `scripts/needs_deep.py` is the daily check: plain Python, run by the Claude desktop scheduled task
`needs-deep-check` (07:00 Bangkok, Tue–Sat). `main()` builds `tickers = sorted(hm.brief_meta())`, the set of briefs.
Use **that** set; do not read `portfolio/portfolio.json`. `holdings_map.py` has `frontmatter(text, key)` and the
regex `SUFFIX` (company-suffix words). `requests` 2.34 is installed and must be used: `urllib` fails SSL on this Mac.

**Tasks**
1. Add `news_query(ticker)`:
   - Return `NEWS_QUERY[ticker]` if the ticker has an override.
   - Otherwise take the brief's `company:` frontmatter, strip anything in parentheses and the `hm.SUFFIX` words,
     collapse spaces, keep the case, and return `intitle:"<name>"`.
   - Overrides at minimum: RKLB `"Rocket Lab"`, FWONA `"Formula 1" OR "Liberty Media"`, IREN `"IREN"`,
     SPCX `"SpaceX"`, TSM `"TSMC"`, AMD `"AMD"`, LLY `"Eli Lilly"`, KO `"Coca-Cola"`, AAPL `"Apple" iPhone`,
     META `"Meta Platforms" OR Zuckerberg`, GOOG `Alphabet OR Google`, BRKB `"Berkshire Hathaway"`, LOW `"Lowe's"`.
     Each is wrapped in `intitle:(...)`.
2. Add `news_count(query, get=requests.get)`. Use a single window: `q=f'{query} when:1d'`, `hl=en-US`, `gl=US`,
   `ceid=US:en`, a browser `User-Agent`, `timeout=10`. Return the `<item>` count, an int from 0 to 100, or `None` on
   any exception, non-200 or 429. **No window ladder and no scaling:** shorter windows at 20:00 ET sample the quiet
   US evening, and switching windows from day to day makes counts incomparable.
3. Add `fetch_counts(tickers, get=requests.get)`. Sleep 1 s between requests and **stop after 3 consecutive `None`s**,
   so a hung network costs at most about 30 s. Return `{ticker: count}` for non-None results only.

**Verify**
- Unit tests with a stubbed `get`:
  - 37 `<item>`s gives 37.
  - A 429 or an exception gives `None`.
  - Three failures in a row stop the loop; the stub is called 3 times, not N.
- `python3 -c "import sys; sys.path.insert(0,'scripts'); import needs_deep as n, holdings_map as hm; [print(t, n.news_query(t)) for t in sorted(hm.brief_meta())]"`.
  Eyeball every generated query once and add overrides where a name is ambiguous or too long.

**Exit criteria.** Every brief ticker has a sensible query. The fetch is bounded and tested offline.
**Rollback.** Remove the three functions; nothing else uses them.

---

## Step 2: History, spike rule, and the fourth trigger

**Context brief.** Private state lives in `portfolio/` (gitignored), next to the existing
`portfolio/.deep-notified.json`. `flags(monitor, ranges, briefs, today)` returns `(ticker, kind, reason)` per ticker
using if/elif precedence, then sorts by `order = {'crossed': 0, 'due': 1, 'move': 2, 'stale': 3}`.
`unseen()` suppresses flags reported in the last 7 days.

**Tasks**
1. History: `portfolio/news-counts.json` holds `{"2026-10-01": {"RKLB": 53, ...}, ...}` with ints only, no `None`.
   Prune entries older than 60 days.
   - **Guard:** if fewer than half the tickers returned a count, or every count is 0 (likely a feed-format change),
     write nothing for today and compute no spikes.
2. Add `news_spikes(history, today_counts, ratio=3.0, floor=10, min_days=7)`. Return
   `{ticker: (today, median)}` where:
   - "prior days" means only the days on which that ticker has a value, and there are at least `min_days` of them;
   - `today >= floor` and `today >= ratio × median(prior)`;
   - the ticker is **skipped when `median(prior) >= 34`**: under the 100-item cap it cannot show a 3× spike. These
     are mega-caps, which the price-move trigger covers.

   Bootstrap is per ticker through `min_days`; there is no separate warm-up message.
3. Change `flags(...)` to take `news=None`. Add `elif news and t in news:` before the stale branch with kind
   `'news'` and reason `f'news spike ({today} vs usual {median:.0f})'`. Set `order` to
   `{'crossed': 0, 'due': 1, 'move': 2, 'news': 3, 'stale': 4}`.
4. In `main()`, on non-dry runs, run fetch → guard → update history → spikes inside one `try/except` that writes
   one stderr line on failure, then pass `news` to `flags()`. `--dry-run` skips the fetch and the write (no new flag).
5. Docstring: add one line naming the source, saying it stores counts only, and noting that a news flag that clears
   can fire again on a later burst.

**Verify**
- Unit tests (synthetic data, `NeedsDeepTests` style):
  - 7 prior days at 10 with today at 35 is flagged; today at 29 is not.
  - A median of 2 with today at 8 is not flagged (below the floor).
  - 6 prior days is not flagged.
  - A median of 40 is skipped.
  - Days where the ticker is missing don't count toward `min_days`.
  - The guard writes nothing when most fetches failed.
  - A ticker with both a move and a spike reports `'move'`; one with only a spike reports `'news'`.
- `python3 scripts/needs_deep.py --all --dry-run` runs with no network.

**Exit criteria.** Four triggers. A news outage degrades cleanly to three.
**Rollback.** `git checkout scripts/needs_deep.py scripts/test_holdings_map.py`, then delete
`portfolio/news-counts.json`.

---

## Step 3: Live run and scheduled task

**Tasks**
1. Do one real run, `python3 scripts/needs_deep.py`. Check its timing (under 3 min) and that
   `portfolio/news-counts.json` gains today's entry. Stdout is expected to be empty until 7 days of history exist.
2. Trigger the `needs-deep-check` task once (`run_scheduled_task`). Confirm it finishes in a few turns with no
   permission prompts and no republish attempt (`graphify-out/.republish-deferred` handles that). The prompt needs
   no edit, because the reason text is already short.

**Exit criteria.** The morning run includes the news trigger; the first news flags become possible after 7 run days.

---

## Notes

- **Cost:** $0. Google News RSS is unofficial and undocumented, so it can change or rate-limit without notice.
  The bounded fetch and the guard keep that from hurting the other triggers.
- **Privacy:** about 50 company-name queries a day from this Mac show the watch list to Google. Nothing private
  reaches tracked files, the public map, or the notification (ticker plus counts only).
- **Signal quality:** headline volume isn't an event in the business. A spike means "go read what happened", which is
  what the notification asks. It never changes a verdict by itself.
- **Out of scope:** SEC 8-K material-event filings (free, via `fetch_sources.edgar_get`) are a more precise event
  signal. Add them later if news spikes prove noisy.
