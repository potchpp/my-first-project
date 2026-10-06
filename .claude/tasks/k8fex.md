
## Intent
The graph shows TSMC supplying NVDA, AAPL, AMD and AVGO (hand-checked edge corrections, 2026-10-06), but the NVDA, AMD and AVGO briefs never mention TSMC, so the supplier risk is missing from their Bear and kill sections.

## Decisions
Partial edit only: add the dependency to Fundamentals/Bear (and a kill condition only if the 10-K sizes the damage); do not re-run the full brief pipeline.

## Pointers
briefs/TSM.md; sources/NVDA, sources/AMD, sources/AVGO 10-Ks (search 'Taiwan Semiconductor' and 'TSMC'); scripts/holdings_map.py CORRECTIONS list; .claude/skills/company-brief/SKILL.md step 7b and 10b.

## Rejected approaches
Adding the link only in graph.json: the brief is the source of truth and graphify re-extracts from it.

## Done-when
Three briefs updated with sourced TSMC lines, fact gate PASS, ledger accept/watch, graph rebuilt.

## Gotchas
Search name variants (Taiwan Semiconductor Manufacturing, TSMC, foundry partner) before calling it absent (lessons.md #6). Do not loosen any kill condition while editing.
