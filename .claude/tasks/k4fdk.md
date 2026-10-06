
## Intent
The 2026-10-05 AI-capex council replaced the per-driver tag cap with a chain budget as a share of total assets, but portfolio/policy.json still holds the old cap, so the map and /trade still flag a breach that no longer applies.

## Decisions
The chain budget and the reason (loss the user accepts if the chain halves) are recorded in portfolio/decisions.md, entry 2026-10-05. The tier rule (proven / behind / too early) and the bubble alarm are NOT settled yet; only the budget is.

## Pointers
portfolio/policy.json (private, gitignored); portfolio/decisions.md 2026-10-05; scripts/holdings_map.py (driver cap use); .claude/skills/trading-desk/SKILL.md step 4; journal doc BOOK checkpoint 'Settle the AI tier rule and the bubble alarm' due 2026-10-31.

## Rejected approaches
Raising the 10% tag cap for every driver: the council kept caps per driver and gave only the AI chain its own budget.

## Done-when
Map's AI-chain bar and /trade's cap check use the chain budget; other drivers keep the old cap; tests pass.

## Gotchas
portfolio/ is private: never copy its numbers into tracked files or this board. The chain is the hyperscaler CHAINS set in holdings_map.py, not the ai-capex tag alone.
