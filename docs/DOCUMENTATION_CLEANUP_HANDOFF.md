# Documentation cleanup — model handoff

Updated: 2026-09-09. This is execution context for the completed documentation task,
not the product roadmap or a claim that future features have shipped.

## Request and authority

The user approved **Save the roadmap and consolidate project documentation** and
then requested this separate handoff so Sol or Terra can continue safely. We are
now in Default mode: editing is authorized. Product implementation starts later.
Do not install plugins, change application behavior, migrate databases, update
dependencies, or implement roadmap features as part of this task.

The approved cleanup is:

1. Save the complete previously agreed phased product roadmap in
   `docs/IMPLEMENTATION_PLAN.md` (planned, not implemented).
2. Consolidate the nine numbered specifications. Retain and streamline **03, 04,
   05, 07, 09** as current-implementation references. Before deleting **01, 02,
   06, 08**, preserve their useful unique content in the onboarding guide,
   retained references, demo runbook, or roadmap, and repair references.
3. Update README, AI_CONTEXT and AGENTS authority rules to distinguish the current
   synthetic demo from the adopted future direction. Mark gate-a0 as historical.
4. Remove the obsolete `.codex/hooks.json.graphify-bak`, preserving active hooks,
   skills and configuration. Remove only inspected disposable generated output;
   ignore future output appropriately. Preserve unidentified files and local data.
5. Refresh Graphify documentation semantics and shared artifacts, then verify
   links, coverage and the focused diff. An AST-only update is not a doc refresh.

The user chose **consolidate useful details**, not wholesale deletion or archiving
all specifications. Original proposal on the Desktop must remain untouched:
`C:\Users\Archit\OneDrive\Desktop\ResiliTrip_Full_Proposed_Solution.md`.

## Progress at this checkpoint

- Planning and read-only inventory completed; user approved implementation.
- Read root AGENTS, README, AI_CONTEXT, DEMO_RUNBOOK and Graphify instructions.
- Roadmap, current-demo architecture reference, README/onboarding updates and
  retained-reference authority notes were written. Documents 01, 02, 06 and 08
  were subsequently restored as roadmap-aligned future specifications; they replace
  the old demo-only scope, architecture and UX authority.
- The obsolete Graphify hook backup and verified contract/test/cache output were
  removed. `.debug-api/case/a3.db` remains because it is an untracked local
  database whose disposal was not proven.
- No application tests have been run in this execution turn. Earlier planning
  recorded 54 backend and 13 frontend unit tests passing; do not present those as
  a fresh full-suite result.
- No commit has been made in this execution turn.

## Repository baseline and safety

Repository: `C:\Users\Archit\OneDrive\Desktop\resilitrip`, Windows PowerShell.
Application code was unchanged from `58be065` during the planning inspection.
Later commits added Graphify/onboarding: `a3f1414`, `14363f2`, `e809829`.
Recheck status before working; user changes always take precedence.

Initial untracked output included `.contract-check-tmp/`, `.debug-api/`,
`apps/web/test-results/`, `graphify-out/cache/`, numerous `.pytest-tmp-*` and
`.test-tmp-*` directories, and `tmp7ypf3zfw/`. Some directories are unreadable in
the sandbox. Do not delete based on names alone or request broad deletion rights.

Inspected immediate contents:

- `.contract-check-tmp/`: generated `openapi.json` and `schema.d.ts`.
- `apps/web/test-results/`: `.last-run.json`.
- `graphify-out/cache/`: `last_query_stamp`.
- `.debug-api/`: a `case` subdirectory, contents not yet inspected.
- Hook backup contains an older PreToolUse Graphify hook command. Confirm active
  configuration independently; never delete `.codex/hooks.json`.

Use `apply_patch` for file edits. Before recursive cleanup, resolve every exact
target and verify it remains under the repository; use PowerShell end-to-end.
Preserve source, tests, fixtures, goldens, lockfiles, SQLite databases, and the
shared graph JSON/report/HTML. Do not sweep `tmp*` or remove a workspace root.
Protected `.codex`/`.agents`/`.git` writes may require tool escalation.

## Product roadmap to save in full

Goal: a local, general-purpose, unfamiliar-trip planning and disruption-recovery
application, free-only data/services, no deadline. Keep React/TypeScript, FastAPI,
Python and SQLite; retain the fictional Mumbai–Goa demo as a clearly separate mode.
Success is create → validate → save/reopen → disrupt → recover → preview/select →
reopen for a non-demo trip, honestly handling unavailable/unknown provider facts.

### Ordered phases and exit gates

- **Foundation:** adopt proposal/roadmap authority; preserve current acceptance
  baseline; record architecture decisions and source capabilities; establish full
  test baseline and migration/rollback policy; reconcile environment-setting
  mismatches during later implementation, not this cleanup.
- **R0 source feasibility:** test Google Maps Demo Key with the actual account,
  without billing, for places, maps, routes and transit across ten geographic
  cases. Verify quotas, dates, coverage, attribution and retention restrictions.
  Delhi GTFS is regional only, subject to verified terms/date validity. Mappls is
  a replacement only if Google fails and its free feasibility is verified. Choose
  one working stack, not parallel stacks. No assumed free national train/bus/flight
  inventory. Coverage: supported/not covered/temporarily unavailable/unknown/manual.
  Source-independent work may continue if blocked; source gate stays incomplete.
- **R1 generic domain:** separate real/demo and draft/active; separate transport
  graph, physical route, semantic dependency DAG and alternative plans. Model
  service patterns/calendars/exceptions/runs/ordered stop calls, scheduled versus
  observed times, full dates and overnight trips, goals, process cutoffs, evidence
  and freshness. Money is exact/range/unknown in paise with party/scope; separate
  sunk costs, spend now and unreceived refunds. Seat availability and accessibility
  must not be assumed. One shared evaluator separates structural errors, unknown
  facts and known infeasibility; required process time is distinct from slack;
  known lower-bound violations remain infeasible. Delays must not incorrectly move
  fixed cutoffs. Versioned SQLite migrations preserve old hashes/history through a
  legacy reader and explicit conversion; old demo data must never become real data.
- **R2 trip creation:** saved trips and separate demo entry; Travel/Stay/Activity/
  Deadline/Free-time inputs; train/flight/bus/local/car/walk and manual ferry;
  place search, pin, coordinates and manual input; dates, party, budget, activity
  flags. Draft save/reopen, non-mutating validation, separate draft from active.
  Regenerate sequential connections while preserving hard dependencies and past
  prefix; explicit acknowledgement of hard implications; reject stale UI responses.
- **R3 recovery:** external provider adapters fetch before pure-domain evaluation;
  normalize walk/transit chains, vehicle assumptions and deduplicate runs/hubs.
  Recover from current position/time, including onboard future stops or flight
  landing; missing facts require input. Disruption updates use idempotent absolute
  facts. Bounded priority-label search supports waits, services, transfers and
  activity edits; progressive widening with explicit time/expansion/quota limits.
  Dominance only for comparable states; rank comparable cost, goals, changes,
  retention and buffer before pruning; preserve preset winners and unknown groups.
  Stable semantic IDs and revisions. Persist queued/running/completed/partial/
  failed/cancelled jobs with worker, polling, cancellation and restart handling.
- **R4 presentation:** real map subject to source terms, general SVG/list fallback;
  synchronized map/timeline/cards, shared prefix and up to four visible branches
  with a complete list; show costs, goals, slack and evidence; generic labels,
  explicit dates and estimated-progress disclosure. Preview is non-mutating;
  selection needs appropriate acknowledgement. Mobile, keyboard and reduced-motion
  support; never claim booking execution.
- **R5 safety and persistence:** server wall clock for real trips, separate demo
  clock; revalidate selected evidence/expiry/version without HTTP inside SQLite
  write transactions, then atomically recheck version and commit. Idempotent
  adoption handles retries/races. Infeasible drafts may be saved but not recommended;
  conditional options require acknowledgement of unresolved facts. Provider
  failures are bounded; enforce retention in persistence, logs and exports.
  Offline mode never substitutes synthetic facts. Versioned local export/import
  omits restricted data; protect server keys and restrict any browser keys.
- **R6 release:** unfamiliar-trip end-to-end acceptance plus retained demo;
  backup/restore; measure local-core and provider latency separately; five-person
  comprehension check, honest pitch and 1080p backup demonstration; refresh both
  AST and documentation graph semantics.

### Interfaces and verification to retain

Keep `/api/v1` and evolve contracts with the local frontend/backend together.
Extend trip creation and reads; add trip listing, draft save and non-mutating
validation; itinerary adoption applies an acknowledged draft. Add place/service
search, transfer estimates and source capabilities. Extend events/constraints/
state, asynchronous planning job creation/read/cancel, preview/adoption revision,
expiry and idempotency; import/export and evidence retrieval. Preserve error
envelope, version checks and demo reset. Regenerate OpenAPI/types/examples per
implementation slice, not during this documentation task.

Test mapping from supplied proposal: R0 RTEST-25–28/32; R1 02/05/08–20/22;
R2 01/03–07/10; R3 08–09/14–16/21–26/31/36; R4 35 plus walkthrough;
R5 27–34/38; R6 performance/usability/demo. RTEST-37 public hosting is deferred.
Retain controlled fixtures separately from actual provider records, renamed IDs,
overnight/multi-day, non-wedding goals, zero budget, missing fares, village routes,
repeated hubs, hills and islands. Each later slice needs behavior/contract tests,
documentation/evidence and graph updates; full release gates before completion.

Out of scope: payments, booking/cancellation execution, PNR/refunds, live ML/weather/
chat, public hosting, national self-hosted transit data. No additional plugins
are required to start. Free-provider access remains a feasibility gate, not a promise.

## Existing-code findings that must not be disguised by doc cleanup

Current application is a synthetic Mumbai–Goa demo, not the roadmap implementation.
Planning found hardcoded fixture IDs/money and wedding labels; recovery uses the
original itinerary and does not fully support onboard recovery; unknown values
can be coerced to zero; current schema uses demo mode and a small transport set.
SQLite uses direct sqlite3 and initialization, not a completed migration system.
Current map is a schematic SVG, not an integrated live-map provider. Graphify is a
navigation aid, not proof of full context or correctness. Check code before making
precise assertions: preserved design specifications may describe intended behavior
that current code has not fully achieved.

## Graphify continuation

Repo skill: `.codex/skills/graphify/SKILL.md`; read fully before graph actions, plus
required `references/update.md` and `references/extraction-spec.md`. Initial read
was truncated around the middle; middle sections were subsequently read, but a
resuming agent should ensure it has read the complete instructions itself.
Skill explicitly requires semantic extraction subagents for documentation, which
is an exception to the general no-proactive-delegation rule. Announce skill use.
No API key is required: host-agent semantic extraction is available. Do not install
or invoke a paid backend merely to refresh documentation.

Installed CLI: `C:\Users\Archit\.local\bin\graphify.exe`.
Tool interpreter (may require escalation to execute):
`C:\Users\Archit\AppData\Local\Packages\OpenAI.Codex_2p2nqsd0c76g0\LocalCache\Roaming\uv\tools\graphifyy\Scripts\python.exe`.
Version observed previously: graphifyy 0.9.56 with MCP extras.
MCP registration was inspected earlier; protocol handshake was not verified.
Native post-commit hook updates are AST-only and can leave tracked graph changes.

Use documentation-aware incremental detection/extraction and `build_merge` with
the repository root. Prune genuinely deleted sources; replacement semantics handle
changed sources. Preserve unaffected API/TypeScript graph coverage and directional
edge metadata. Validate every extraction chunk; no filename-only placeholders,
invented edges or fabricated token counts. Tool usage counts may be unavailable;
record that honestly. Regenerate JSON/report/HTML consistently, and stamp only
successfully extracted semantic sources. Existing graph coverage is imperfect;
do not claim a whole-repository semantic audit from this scoped refresh.

## Next steps

1. If resuming, treat this cleanup as complete and begin product implementation
   only when the user requests it.
2. Before any new implementation slice, read `IMPLEMENTATION_PLAN.md`, establish
   a fresh test baseline, and retain the synthetic demo as a distinct mode.
3. Graphify was refreshed with semantic documentation extraction. Its undirected
   integrity diagnostic reported no missing endpoints but normal relation collapse;
   do not mistake it for a formal proof of completeness. The refreshed semantic
   batches produced no hyperedges, so the prior hyperedge metadata was intentionally
   pruned rather than retained with deleted-document references.
