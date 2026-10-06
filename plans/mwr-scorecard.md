# Beat-the-S&P scorecard: MWR against the same money in the index

## Goal

Answer "am I beating the S&P 500 with my actual money?" honestly, and feed each number into the decision it serves.
Choices made 2026-10-03: headline window **rolling 2 years**; **trade-around check** per holding; **invested book only**
(cash and total assets are out of scope).

## Why the current comparison goes

The map compares a simple return on capital (profit ÷ start value + new money) with the S&P's point-to-point change.
Money added late counts as full capital but had little time to earn, so the book looks far behind when it is roughly
level. The simple return stays in `perf.py` as data, but the map stops comparing it with the index.

## Metrics

| Metric | Definition | Decision it serves |
|---|---|---|
| **Book MWR** | XIRR of the book's cash flows in the window: start value in, net buys in, sells out, end value out. Annualised. | Context |
| **Same-money S&P** | The same dated cash flows put into `^SP500TR`; XIRR of that shadow. | Context |
| **Gap** (headline) | Book MWR − same-money S&P, pts/yr. Rolling 2y = the score; 1y = early warning; since start = context. | Is picking worth it (yearly review) |
| **TWR** | Already in `perf.py`. Shown for 1y and 2y only, annualised. Since-start TWR is dropped (small early book inflates it). | Picks vs timing diagnostic |
| **Money timing** | MWR − annualised TWR. For this book it mostly measures when money arrived (≈70% in the last 18 months), not trade quality. | Context only |
| **Add record** (trade audit) | Each add's stock vs the S&P over the next 63 trading days; per stock: adds judged, how many beat the index. | Do my adds help? Where does averaging in fail? |
| **Per-holding gap** | Each holding's MWR vs its own cash flows put into the S&P, over the window it was held. | Tie-breaker at the cap; prompts a thesis re-check |
| **Gap attribution** | Each holding's excess dollars vs its shadow, as % of the book's value. Includes names sold during the window. Additive, so drivers sum their holdings. | "Which stocks caused this?" at the 2y horizon |

## Guardrails

- Holdings held under 1 year: "too early to judge", no gap shown.
- Positions under 0.5% of total assets are grouped as "small positions".
- Performance never triggers an exit; exits stay on kill conditions. Wording is evidence, never an instruction.
- XIRR that does not converge shows "—", never a guessed number.

## Changes

1. **`scripts/perf.py`**: `xirr()`, a same-money shadow, and per-window book fields (`mwr`, `shadow_mwr`, `gap_pp`,
   `twr_ann`, `timing_pp`); per-position fields for the 2y window (`mwr`, `shadow_mwr`, `gap_pp`, `timing_pp`,
   `excess_usd` → shown as % only, `held_days`). Appends one row per run to `portfolio/kpi-history.jsonl` (private) so
   the map can show the change since the last review (~120 days ago).
2. **`scripts/test_perf.py`**: a lump sum that tracks the index has gap ≈ 0; a buy before a rise has positive
   trade-around value; one known XIRR case; holding excess sums to the book excess.
3. **Spec** `docs/superpowers/specs/2026-09-18-portfolio-apr-core-design.md`: record that MWR vs same-money S&P replaces
   APR as the KPI, and why (the earlier decision dropped XIRR and the shadow).
4. **`scripts/holdings_map.py`**: pass the new fields into the private view (percentages only). Driver figure = sum of its
   holdings' excess, as % of the driver's current value.
5. **Map (private page only)**:
   - Top card: 2y gap as the big number; since-start and 1y smaller; change since the last review.
   - Gap attribution: the biggest contributors for and against.
   - Holding panel: "with your money vs S&P" gap and the add record.
   - "Needs a look" adds only overlaps: behind the index for 1y+ **and** (kill condition on watch or review, or "Ahead
     of itself"); or 4+ adds with under 25% beating the index (from the trade audit).
   - Driver period switch becomes the 2y gap per driver; 1-day and 5-day moves move lower on the page; the simple-return
     comparison is removed.
6. **Ask Claude and `/council`**: the evidence pack gains the holding's gap and add record.

## Verification

- Tests pass; book MWR and same-money S&P match the throwaway check of 2026-10-03 (scratchpad `mwr.py`; figures stay out of tracked files).
- Holding excess sums to the book excess within rounding.
- `index.html` (public) still carries no portfolio data.

## Out of scope

Cash and total-asset returns; a 5-year window (not enough history yet).
