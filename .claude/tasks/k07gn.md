
## Intent
The Shared competitors panel is thin for consumer names, so overlaps between consumer holdings are invisible on the map.

## Decisions
Only competitors named in our own sources count; same rule as the peers check.

## Pointers
briefs/peers.json; consumer briefs (shared_driver consumer-spend); sources/<T>/10-k competition sections.

## Rejected approaches
Adding well-known rivals from general knowledge: that is the Amgen error.

## Done-when
New entries each cite a line containing the name; map shows the new chips; tests pass.

## Gotchas
Do this after the peers check so the file's rule is settled first.
