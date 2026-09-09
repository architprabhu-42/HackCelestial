# Changes from the Original Mumbai–Goa Demo

## Baseline preserved

The original Mumbai–Goa scenario remains the accepted synthetic, not-bookable
demo. Its fixture values, planner goldens, API behavior, UI, immutable snapshots,
and historic snapshot hashes are retained. The work below is additive; it does not
turn the demo into a live booking or provider-backed product.

## Documentation and delivery structure

- Reorganized and refreshed the product, requirements, domain, architecture,
  API, UX, test-strategy, and compatibility documentation.
- Added the implementation roadmap, current-demo architecture reference, and
  documentation-cleanup handoff material.
- Added repository guidance for Graphify-backed architecture navigation.

## R1 generic-trip foundations

- Added explicit `demo`/`real` trip modes and `draft`/`active` lifecycle state,
  with SQLite migrations that preserve pre-existing demo snapshots and hashes.
- Added evidence facts with provenance, observed/freshness timestamps, coverage
  state, and explicit unknown values.
- Added money primitives for exact, range, and unknown paise amounts, retaining
  separate sunk cost, cash due now, and unreceived refund buckets.
- Added independent generic topology: places, physical segments, transport modes,
  semantic dependency DAGs, and alternative-plan identity.
- Added generic service calendars, exceptions, dated runs, ordered stop calls,
  scheduled/observed timestamps, and overnight journey support.
- Added generic goals, fixed process cutoffs, structural feasibility outcomes, and
  a composed evaluator that keeps structural errors, unknown facts, infeasibility,
  and conditional results distinct.
- Added immutable semantic alternative evaluation snapshots with stable IDs,
  revision rules, referenced inputs, and content hashes.
- Added a separate generic-trip aggregate plus append-only SQLite `generic_*`
  tables. Generic version and semantic-snapshot reads verify hashes before parsing;
  writes use optimistic version checks and atomic rollback on failure.

## Compatibility and verification

- Added focused R1 domain, lifecycle, persistence, and regression tests.
- Regenerated OpenAPI and TypeScript schema only for the earlier API-visible
  lifecycle addition; the generic R1 aggregate remains internal.
- Retained demo regression coverage for its truth label, planner outputs, fixture
  values, and legacy persistence compatibility.

## Graphify knowledge graph

The checked-in `graphify-out/` directory contains the refreshed repository graph:
`graph.json` for graph tooling, `graph.html` for interactive inspection, and
`GRAPH_REPORT.md` for a human-readable overview. It was refreshed after the R1
work using `graphify update .`.
