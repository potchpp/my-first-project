# Tasks: my-first-project
<!-- Task board manifest v1. Status tokens: [backlog] [todo] [doing] [done] [forbidden]. -->
<!-- "blocked" is DERIVED — never a manual status. Two kinds: deps not all [done], OR a -->
<!-- "blocker: <reason>" line on a [todo] (external wait); set/clear it with -->
<!-- status block <id> "<reason>" / status unblock <id> -- never hand-edit the line. -->
<!-- [backlog] = not ready yet; excluded from run planning. Promote with: status todo <id> -->
<!-- [forbidden] = too dangerous to ever run — permanent tombstone. Add 'reason: <why>'. -->
<!--   Never archived. Flip back to todo only if mis-classified. -->
<!--   Set with: status forbidden <id>  -->
<!--   Format: "## T<NN> [forbidden] <title>" + "reason: <why it must never run>" -->
<!-- Task header format is parsed: "## T<NN> [status] <free-text title>". Keep the id+status shape. -->
<!-- Recurring chores (separate class, NOT in run/todo) use ids R<NN> + [recurring]; surface only when due. -->
<!--   ## R01 [recurring] <title>  /  every: 7d  /  last-done: YYYY-MM-DD  /  do: ...   (reset with: status did R01) -->
<!-- board-format: 1 -->

## k4fdk [todo] Align policy.json driver cap with the AI-chain budget
created: 2026-10-06
deps: -
exec: agent
model: sonnet
effort: M
do: Update portfolio/policy.json so the AI-capex chain uses the chain budget decided on 2026-10-05 instead of the old per-driver cap, and make the map and trading desk read it.
done-when: holdings_map.py and the trading-desk skill show the AI chain against the new budget, and tests pass.

## k8fex [todo] Add TSMC as supplier in the NVDA, AMD and AVGO briefs
created: 2026-10-06
deps: -
exec: agent
model: sonnet
effort: M
do: Run a partial /deep-style edit on briefs/NVDA.md, AMD.md and AVGO.md to name TSMC as the foundry they depend on, linked as [[TSM]], with the fact gate on the changed lines and the ledger.
done-when: Each of the three briefs links [[TSM]] with a source line from its own 10-K, both fact-gate reviewers pass, and verdict_ledger.py records each.

## k0svk [todo] Verify every peers.json citation names the company
created: 2026-10-06
deps: -
exec: agent
model: sonnet
effort: M
do: For each competitor and risk entry in briefs/peers.json, open the cited file:line and confirm the company or risk is named there; remove or re-source any that are not.
done-when: A script or check lists every entry with its cited line containing the name, and every unsupported entry is removed or re-cited.

## k07gn [todo] Fill in consumer competitors in peers.json
created: 2026-10-06
deps: k0svk
exec: agent
model: sonnet
effort: S
do: Add sourced competitors for the consumer holdings in briefs/peers.json, each citing a 10-K competition line or brief line that names the competitor.
done-when: Consumer holdings that share a named competitor appear as chips on the map, each entry citing a line that names it.

## k58w2 [todo] Full brief on ETN (energy scout Tier 2)
created: 2026-10-06
deps: -
exec: agent
model: sonnet
effort: L
do: Ask the user before running /deep ETN; if approved, run it and add ETN to monitor.json.
done-when: briefs/ETN.md exists with a verdict and falsifier, fact gate passed, ledger logged, monitor.json entry added.
