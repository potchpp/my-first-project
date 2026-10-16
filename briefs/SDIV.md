---
ticker: SDIV
company: Global X SuperDividend ETF
updated: 2026-10-17
type: stock-brief
shared_driver: high-yield-income
---

# SDIV — Global X SuperDividend ETF
**Date:** 2026-10-17 | *First brief. SDIV is an ETF: no 10-K, no earnings call (fetch_sources.py found no company CIK). Web sources only; pipeline adapted to a fund. NAV $23.71, price $23.67 (issuer, 2026-10-15).*

**Source docs:** [[sources/SDIV/fund-facts]]

---

## Fund snapshot

SDIV holds about 106 stocks (issuer, 2026-10-15) picked by the Solactive Global SuperDividend Index: the 100 highest-yielding global equities that pass a dividend-stability screen, equal weighted. Net expense ratio 0.58%, net assets $1.17B on 49,309,412 shares, monthly distributions (issuer page, 2026-10-15). Mix (issuer, 2026-09-30): Financials 32.02%, Energy 16.89%, Real Estate 15.78%; countries (issuer, undated): US 32.30%, Brazil 17.23%, Norway 6.07%. Largest holding 1.80%, top-10 weights listed sum to about 16.2% with one weight not shown (issuer, 2026-10-15; my sum). Yield: 30-day SEC 9.77%, trailing-12-month 9.81%, issuer says the trailing-12-month yield and the 8.94% distribution rate are estimated to include return of capital. It is a cash-flow product built on a screen, not a company with a franchise.

## Fund structure signal *(fund structure agent)*
- **Concentration is by theme, not by name:** Financials + Energy + Real Estate = 64.7% (issuer, 2026-09-30, my sum). No holding above 1.80%. Equal weighting means a payout cut in one name costs little, but the index picks yield, and a high yield is often a fallen price.
- **Index has been patched:** 2021-04-16 weighting change for quarterly dividend-cut reviews and a 2024-07-22 move to target share counts *(Solactive notices via search snippet, 2024 notice URL 404: both unverified)*.
- **AUM:** $1.17B (2026-10-15) vs $1.33B (ETF Central, 2026-03-10), about -12% in seven months; no closure notice found. Turnover not confirmed (sources conflict). Premium/discount -0.181% (2026-10-15).

## Income quality *(income quality agent)*
- **The monthly payout has been cut, repeatedly.** Ladder from stockanalysis.com ex-dates: $0.30 (Feb-Aug 2022) → $0.255 → $0.23 (Apr 2023) → $0.21 (Aug 2023) → $0.19 (Apr 2024) → ~$0.19-0.20 through 2025 → $0.18 from 2026-05-05. That is **-40% from $0.30, and -54% from the $0.395 paid 2021-12-30** *(single source for the ladder: unverified; 24/7 Wall St, 2026-08-25, confirms a 2026 trim)*. The most recent cut was -5%. Ex-date sums per share: $3.405 (2022), $2.645 (2023), $2.336 (2024), $2.305 (2025) (agent arithmetic).
- **Part of the payout is return of capital.** Global X Form 19a, 2026-08-05: 29.69% of the August distribution and 26.09% year-to-date was ROC; May 2026 showed 56.77%, June 5.42% *(19(a) notices are estimates, not tax figures; the .docx was read by one agent only: unverified)*. Older notices ranged from about 14% to 82% (single months and fiscal-year-to-date figures; fund-facts.md). Full-year 1099 splits were not found.
- **NAV history:** current NAV $23.71 (issuer, 2026-10-15). Launch NAV and year-end NAVs could not be sourced, so "NAV has not grown" rests only on the issuer's 5y/10y price returns of +0.16% / -0.83% (unverified basis).

## Latest earnings
Not applicable: a fund has no earnings. Latest fund-level data is the 2026-09-30 return table below and the August 2026 19(a) notice above.

## Bull / Bear

**Bull** *(bull_researcher)*
- The cut ladder is slowing: steps of -15%, -10%, -9%, -10%, then -5% (May 2026); 2025 payout was about 1% below 2024 on ex-date sums *(income quality)*. ROC share swings month to month (56.77% May, 5.42% June), so one month overstates the problem.
- Structure is spread out and rule-based: 106 holdings, 1.80% largest, 0.58% fee, discount -0.181%, and a 3-year NAV return of +13.29% (issuer, 2026-09-30) *(fund structure; income quality)*.
- It does a different job from the benchmark: cash flow from a value-tilted, non-US-heavy basket. Break-even vs the S&P 500 5-year return needs NAV up about +4.0% a year on a 9.81% yield *(valuation)*. Weakest points, by the bull's own admission: every point mitigates rather than rebuts the 5y/10y gap, and the issuer figures behind the 1y/3y reading have an unlabeled basis.

**Bear** *(bear_researcher)*
- Income is shrinking and partly funded by return of capital: $0.30 → $0.18, six or more cuts, a May 2026 cut still in the record, ROC 26.09% YTD. The 9.8% yield is quoted on a NAV whose 5y price return is +0.16% (issuer, 2026-09-30).
- The return gap to the benchmark is large (below), and the yield is picked by a ranking: a top-100 yield screen with only an "at least stable" forecast filter tends to select names whose price has fallen. 64.7% sits in three cyclical sectors, 17.23% in Brazil *(country table undated)*.
- AUM -12% since March, 1-month outflow -$122.27M (ETFdb, 2026-10-14; cause unknown), and a "yield trap" read from 24/7 Wall St (2026-09-18). Weakest point, by the bear's own admission: the payout has sat near $0.18-0.20 since April 2024.

## Valuation
**Lens:** total return vs price return vs S&P 500 total return over 3/5/10 years, then what the 9.8% yield implies about sustainability. P/E and EV multiples are not meaningful for a fund.

| NAV total return, annualized, 2026-09-30 | 3y | 5y | 10y |
|---|---|---|---|
| SDIV (issuer; basis not labeled on page, small 5y/10y values imply annualized) | +13.29% | +0.20% | -0.74% |
| SDIV market price | +13.17% | +0.16% | -0.83% |
| S&P 500 total return (SSGA SPY page, same date) | 22.89% | 13.79% | 15.33% |

$100 over 5 years becomes about $101 vs $191, and over 10 years about $93 vs $416 (my arithmetic on those figures). The S&P figures are close to a second source for 5 years (NerdWallet, Oct 2026: 13.30-13.31%) but a 10-year cross-check conflicts (S&P Global: 13.44% to 2026-09-16; FinanceCharts VOO 15.54%, date unclear): **S&P 10-year figure unverified within about 2 points.**

**Data conflict resolved (2026-10-17):** the price only looks flat because SDIV did a **1-for-3 reverse split on 2022-12-20** (Global X announcement 2022-11-18; MIAX corporate-action alert). In pre-split terms the price kept falling, so the issuer's ~0% 5-year and −0.7% 10-year NAV returns are consistent with the payout history. The gap to the S&P 500 (13.6 / 16.1 points a year on issuer figures) stands.

**What the yield implies:** $0.18 × 12 = $2.16, 9.1% of NAV (my arithmetic); with 26.09% ROC YTD, about 2.4% of NAV a year is being handed back as capital. To match the S&P 500's 13.79% over time, SDIV needs NAV to change about +4.0% a year (13.79 - 9.81, my arithmetic); to match 15.33%, about +5.5%. Its 5-year price return was +0.16%.

**Verdict: Ahead of itself.** The 9.8% yield is partly return of capital and the payout has been cut from $0.30 to $0.18; the 5y/10y total return trails the S&P 500 by a wide margin. The one counter-signal is the 3-year return (+13.29%, still 9.6 points a year behind the S&P).

**Falsifying number** (Ahead of itself is disproved by a number coming in ABOVE the bar): SDIV 1-year NAV total return (issuer fact sheet, as of 2027-09-30) **above 13.8%** (the S&P 500's 5-year annualized figure, 13.79%, at 2026-09-30). Current value: 7.51% (1y, 2026-09-30). Deadline: 2027-09-30 reading. *The issuer's 5y/10y figures are consistent with the price history once the 2022-12-20 1-for-3 reverse split is accounted for.*

## Addressable market
Not applicable to a fund. The substitute question is capacity: the yield-ranked pool of global stocks is large, but AUM fell about 12% in seven months, so closure risk matters only if AUM drops far below today's $1.17B (see Kill conditions).

## Variant perception
- *Thesis metric:* 12-month distributions per share plus change in NAV (ROC-adjusted total return), against the S&P 500 total return. Today: 12 × $0.18 = $2.16 on NAV $23.71, with 26.09% of YTD distributions ROC.
- *Where we differ from consensus:* nothing. The cautious read (yield trap, serial cuts, ROC) is what the 24/7 Wall St and Morningstar commentary already says. No expectation gap to earn.
- *Honest fit check:* this investor holds platform and infrastructure companies for 3+ years, wants a kill condition before every purchase, and measures against the S&P 500 total return. SDIV does not fit that style: it is an equal-weighted yield screen with no thesis about an industry shift, and on the issuer's numbers it has trailed the benchmark over 5 and 10 years. What it can be for is income and non-US, value-tilted diversification, with Brazil, Norway and the UK in the mix. If the job is income, the test is the payout and the ROC share. If the job is beating the S&P 500, the numbers above say it has not.

## Kill conditions
Event-based; for a fund they are about the payout, NAV, the index and survival.
1. **Monthly distribution cut to $0.153 or lower** (15% below $0.18) within any 12 months. [bounded ~15%] — the income this fund exists to pay.
2. **Full-year return-of-capital share above 50%** on the final 1099 characterization, or on 19(a) YTD for two consecutive notices. [bounded ~25%] — the payout is then mostly the investor's own money. *(Threshold is judgment; no full-year split found yet.)*
3. **NAV down 20% or more within 12 months** (from $23.71 to $18.97 or below, month-end). [bounded ~20%]
4. **Index methodology change** that removes the dividend-stability screen or equal weighting. [open-ended] — the product would no longer be the one analyzed.
5. **Net assets below $300M** (about 74% under $1.17B). [open-ended] — closure or merger risk and forced selling.

Primary kill condition (strongest bear point with no bull counter): #1, the payout, because the bull case only slows the cut ladder and does not rule out the next step.

## What to ask
1. What job is SDIV doing in the book, income or diversification, and could that job be done with a lower-cost holding that does not carry return of capital? If the answer is "beat the S&P 500", what number would show it has?
2. Are the payout ladder figures split-adjusted? Pre- and post-2022-12-20 amounts differ by 3x; check stockanalysis.com's ladder against the issuer's distribution history before quoting cut sizes.
3. What was the 2025 and 2026 full-year 1099 return-of-capital share, and which annual-report page shows the fiscal-year end? (We inferred Oct 31 from the Dec 2024 and Mar 2025 19(a) notices; unverified.)

---
*Fact gate: about 37 claims checked per reviewer, 6 fixed (top-10 sum, ROC scope, ROC range, return reconstruction 9-15%, launch NAV removed, turnover removed), about 12 left as WEB/single-source (unverified), 2 rounds. Round 2: both reviewers failed only on the turnover line, which was then deleted (not re-run: deletion only).*
