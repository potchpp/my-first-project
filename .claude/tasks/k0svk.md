
## Intent
On 2026-10-06 'Amgen' was found in peers.json as a shared LLY/ABBV competitor, but neither cited line nor any LLY/ABBV source names Amgen; the Haiku agents that built the file added names from memory. Other entries may have the same flaw.

## Decisions
Amgen was already removed (2026-10-06). Keep an entry only when the cited line names it; a near-miss citation gets re-sourced, not trusted.

## Pointers
briefs/peers.json (_about says Haiku agents built it from 10-K competition and brief Bear/Kill sections); scripts/holdings_map.py reads it for map chips and graph links; .claude/skills/company-brief/lessons.md.

## Rejected approaches
Trusting the file because it cites line numbers: Amgen had citations too.

## Done-when
Every remaining entry's cited range contains the name (case-insensitive, with variants); a short report lists what was removed; map rebuilt.

## Gotchas
Line ranges like 37-39 must be read whole; check spelling variants (lessons.md #6) before removing. Add a lessons.md entry if more invented names are found.
