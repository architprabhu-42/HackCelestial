# Graph Report - resilitrip  (2026-09-09)

## Corpus Check
- 138 files · ~177,221 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 974 nodes · 2567 edges · 73 communities (41 shown, 21 thin omitted)
- Extraction: 87% EXTRACTED · 13% INFERRED · 0% AMBIGUOUS · INFERRED: 325 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `26cfc64c`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- routers/contracts.py
- App.tsx
- models.py
- ContractModel
- test_r1_generic_topology.py
- plan_recovery
- helpers.ts
- EvidenceValue
- package.json
- compilerOptions
- ResiliTrip README
- compilerOptions
- devDependencies
- schema.d.ts
- scripts
- ResiliTrip — Domain Model and India Travel Glossary
- tsconfig.json
- Graphify skill
- api/__init__.py
- routers/__init__.py
- infrastructure/__init__.py
- resilitrip/__init__.py
- tools/__init__.py
- repository agent instructions
- Baseline impact interface snapshot
- Baseline workspace interface snapshot
- Recovery comparison interface snapshot
- Journey editor acknowledgement snapshot
- Offline map fallback interface snapshot
- 6. Entity definitions
- Gate A0 compatibility record
- resilitrip-api
- graphify reference: extra exports and benchmark
- 4. Essential distinctions
- 7. State vocabularies
- setup.ts
- TripRepository
- dependencies
- graphify reference: query, path, explain
- repositories.py
- 9. Time model
- engines
- graphify reference: add a URL and watch a folder
- graphify reference: commit hook and native CLAUDE.md integration
- graphify reference: incremental update and cluster-only
- 11. Financial model
- 12. Constraint model
- 5. Aggregate roots and versioning
- test_r1_generic_trip_persistence.py
- graphify reference: GitHub clone and cross-repo merge
- graphify reference: transcribe video and audio
- 8. State transitions
- README.md
- model_validator
- Path
- CurrentState
- ServiceCatalog
- DomainValidationError
- health.py
- Changes from the Original Mumbai–Goa Demo
- field_validator
- baseline_snapshot

## God Nodes (most connected - your core abstractions)
1. `ContractModel` - 99 edges
2. `plan_recovery()` - 45 edges
3. `create_initial_trip()` - 43 edges
4. `TripAggregate` - 34 edges
5. `apply_timing_event()` - 33 edges
6. `composition_input()` - 32 edges
7. `TripRepository` - 30 edges
8. `generic_input()` - 30 edges
9. `load_fixture()` - 29 edges
10. `connect()` - 27 edges

## Surprising Connections (you probably didn't know these)
- `ResiliTrip README` --references--> `reference scenario and fixture specification`  [EXTRACTED]
  README.md → docs/04_Reference_Scenario_and_Fixture_Specification.md
- `ResiliTrip README` --references--> `test strategy and golden validation specification`  [EXTRACTED]
  README.md → docs/09_Test_Strategy_and_Golden_Validation_Specification.md
- `ResiliTrip README` --references--> `current demo architecture`  [EXTRACTED]
  README.md → docs/CURRENT_DEMO_ARCHITECTURE.md
- `ResiliTrip README` --references--> `ResiliTrip demo runbook`  [EXTRACTED]
  README.md → docs/DEMO_RUNBOOK.md
- `GenericTripAggregate` --uses--> `GenericCompositionInput`  [INFERRED]
  apps/api/resilitrip/domain/generic_trip.py → apps/api/resilitrip/domain/composed_evaluation.py

## Import Cycles
- None detected.

## Communities (73 total, 21 thin omitted)

### Community 0 - "routers/contracts.py"
Cohesion: 0.16
Nodes (33): ApiProblem, adopt_plan(), apply_event_route(), create_trip(), _db(), generate_plans(), get_plan(), get_trip() (+25 more)

### Community 1 - "App.tsx"
Cohesion: 0.05
Nodes (61): AdoptionResponse, api, ApiProblem, ConstraintsReplaceCommand, CurrentStateReplaceCommand, EventResponse, ItineraryEditCommand, MutationResponse (+53 more)

### Community 2 - "models.py"
Cohesion: 0.05
Nodes (90): evaluate_baseline(), Baseline itinerary projection only; recovery planning is intentionally absent., classify_slack(), hotel_start_is_valid(), meets_cutoff(), money_within_limits(), plan_is_valid(), datetime (+82 more)

### Community 3 - "ContractModel"
Cohesion: 0.15
Nodes (25): AdoptionCommand, AdoptionRecord, AdoptionResponse, ApiErrorCode, CurrentStateReplaceCommand, EventResponse, EventResult, FixtureTripCreate (+17 more)

### Community 4 - "test_r1_generic_topology.py"
Cohesion: 0.17
Nodes (18): AlternativePlanReference, DependencyStrength, DependencyType, PhysicalRouteSegment, model_validator, StrEnum, Generic, provider-independent trip topology primitives. This module…, One ordered physical movement, without asserting a service or timetable. (+10 more)

### Community 5 - "plan_recovery"
Cohesion: 0.08
Nodes (62): create_initial_trip(), Gate A1 creation of a version-one trip and its baseline projection., snapshot_for_trip(), apply_timing_event(), calculate_impacts(), evaluate_trip(), Pure timing-event application and deterministic impact diffing., Create an isolated immutable service-state branch for fixture perturbation… (+54 more)

### Community 6 - "helpers.ts"
Cohesion: 0.45
Nodes (5): applyD1(), generatePlans(), loadDemo(), previewF3(), @playwright/test

### Community 8 - "package.json"
Cohesion: 0.11
Nodes (16): name, private, type, version, @axe-core/playwright, jsdom, maplibre-gl, openapi-typescript (+8 more)

### Community 9 - "compilerOptions"
Cohesion: 0.11
Nodes (17): compilerOptions, allowJs, allowSyntheticDefaultImports, esModuleInterop, isolatedModules, jsx, lib, module (+9 more)

### Community 10 - "ResiliTrip README"
Cohesion: 0.16
Nodes (22): Product Decision and Scope, Source feasibility gate, Product Requirements, reference scenario and fixture specification, algorithm and recovery planning specification, Backend domain authority, Technical Architecture, Persisted planning jobs (+14 more)

### Community 11 - "compilerOptions"
Cohesion: 0.14
Nodes (13): compilerOptions, allowImportingTsExtensions, lib, module, moduleDetection, moduleResolution, noEmit, skipLibCheck (+5 more)

### Community 12 - "devDependencies"
Cohesion: 0.15
Nodes (13): devDependencies, @axe-core/playwright, jsdom, openapi-typescript, @playwright/test, @testing-library/react, @types/node, @types/react (+5 more)

### Community 13 - "schema.d.ts"
Cohesion: 0.33
Nodes (5): components, $defs, operations, paths, webhooks

### Community 14 - "scripts"
Cohesion: 0.33
Nodes (6): scripts, build, dev, test, test:e2e, test:watch

### Community 15 - "ResiliTrip — Domain Model and India Travel Glossary"
Cohesion: 0.11
Nodes (17): 10. Location and continuity model, 13. Event and immutability rules, 14. Provenance and uncertainty rules, 15. Canonical reason codes, 16. Identifier conventions, 17. Compact record example, 18. India travel glossary, 19. Cross-entity invariants (+9 more)

### Community 17 - "Graphify skill"
Cohesion: 0.67
Nodes (3): Graphify semantic extraction specification, Graphify skill, persistent knowledge graph

### Community 29 - "6. Entity definitions"
Cohesion: 0.11
Nodes (18): 6. Entity definitions, DM-01 — TravelerProfile, DM-02 — CurrentState, DM-03 — Location, DM-04 — ServiceInstance, DM-05 — TransferTemplate, DM-06 — Activity, DM-07 — Dependency (+10 more)

### Community 44 - "graphify reference: extra exports and benchmark"
Cohesion: 0.22
Nodes (8): graphify reference: extra exports and benchmark, Step 6b - Wiki (only if --wiki flag), Step 7 - Neo4j export (only if --neo4j or --neo4j-push flag), Step 7a - FalkorDB export (only if --falkordb or --falkordb-push flag), Step 7b - SVG export (only if --svg flag), Step 7c - GraphML export (only if --graphml flag), Step 7d - MCP server (only if --mcp flag), Step 8 - Token reduction benchmark (only if total_words > 5000)

### Community 45 - "4. Essential distinctions"
Cohesion: 0.29
Nodes (7): 4.1 Trip versus itinerary, 4.2 Service instance versus activity, 4.3 Transfer template versus transfer activity, 4.4 Booking versus physical movement, 4.5 Dependency graph versus search graph, 4.6 Scheduled, effective and observed time, 4. Essential distinctions

### Community 46 - "7. State vocabularies"
Cohesion: 0.29
Nodes (7): 7.1 Current traveler phase, 7.2 Service status, 7.3 Feasibility status, 7.4 Planner result status, 7.5 Booking knowledge state, 7.6 Source display status, 7. State vocabularies

### Community 48 - "TripRepository"
Cohesion: 0.05
Nodes (76): api_problem_handler(), internal_error_handler(), problem_body(), Request, validation_handler(), default_settings(), Configuration for the local-only P0 application., Settings intentionally limited to the Gate A0 infrastructure needs. (+68 more)

### Community 49 - "dependencies"
Cohesion: 0.40
Nodes (5): dependencies, maplibre-gl, react, react-dom, @xyflow/react

### Community 50 - "graphify reference: query, path, explain"
Cohesion: 0.33
Nodes (5): For /graphify explain, For /graphify path, graphify reference: query, path, explain, Step 0 — Constrained query expansion (REQUIRED before traversal), Step 1 — Traversal

### Community 51 - "repositories.py"
Cohesion: 0.07
Nodes (29): GenericTripAggregate, field_validator, model_validator, Isolated aggregate for persisted generic R1 trips. This model intentionally…, A versioned generic trip and its immutable semantic evaluation history., TimingReplayEvent, TripLifecycle, TripMode (+21 more)

### Community 52 - "9. Time model"
Cohesion: 0.40
Nodes (5): 9.1 Representation, 9.2 Boundaries, 9.3 Activity readiness, 9.4 Replay time, 9. Time model

### Community 53 - "engines"
Cohesion: 0.67
Nodes (3): engines, node, npm

### Community 54 - "graphify reference: add a URL and watch a folder"
Cohesion: 0.50
Nodes (3): For /graphify add, For --watch, graphify reference: add a URL and watch a folder

### Community 55 - "graphify reference: commit hook and native CLAUDE.md integration"
Cohesion: 0.50
Nodes (3): For git commit hook, For native CLAUDE.md integration, graphify reference: commit hook and native CLAUDE.md integration

### Community 56 - "graphify reference: incremental update and cluster-only"
Cohesion: 0.50
Nodes (3): For --cluster-only, For --update (incremental re-extraction), graphify reference: incremental update and cluster-only

### Community 57 - "11. Financial model"
Cohesion: 0.50
Nodes (4): 11.1 Terms, 11.2 Hero financial baseline, 11.3 Invariants, 11. Financial model

### Community 58 - "12. Constraint model"
Cohesion: 0.50
Nodes (4): 12.1 Hard constraints, 12.2 Ranking preferences, 12.3 Constraint-check truth values, 12. Constraint model

### Community 59 - "5. Aggregate roots and versioning"
Cohesion: 0.50
Nodes (4): 5.1 Trip, 5.2 Service catalog, 5.3 Plan, 5. Aggregate roots and versioning

### Community 60 - "test_r1_generic_trip_persistence.py"
Cohesion: 0.05
Nodes (121): compose_evaluation(), ComposedMoney, ComposedOutcome, CompositionReason, CompositionReasonCode, EvidenceReference, GenericCompositionInput, GenericCompositionResult (+113 more)

### Community 63 - "8. State transitions"
Cohesion: 0.67
Nodes (3): 8.1 Trip and plan lifecycle, 8.2 Event disposition, 8. State transitions

### Community 65 - "model_validator"
Cohesion: 0.14
Nodes (4): Location, PolicyRecord, model_validator, ServiceDefinition

### Community 68 - "CurrentState"
Cohesion: 0.26
Nodes (13): ConstraintsReplaceCommand, Frozen-prefix validation for the future-itinerary replacement contract., validate_itinerary_replacement(), CurrentState, TravelerPhase, Validate a standalone replacement itinerary before it can become active., validate_dependency_dag(), replacement() (+5 more)

### Community 69 - "ServiceCatalog"
Cohesion: 0.32
Nodes (13): ItineraryEditCommand, ManualTripCreate, Booking, Constraints, ItineraryDefinition, MoneyItem, ProvenanceRecord, ServiceCatalog (+5 more)

### Community 71 - "DomainValidationError"
Cohesion: 0.29
Nodes (9): ExecutableScenarioFixture, DomainValidationError, ValueError, Validate cross references, collection uniqueness, and the itinerary DAG., Normalized domain validation failure with a stable code and path., validate_fixture(), load_mutated(), parametrize (+1 more)

### Community 72 - "health.py"
Cohesion: 0.39
Nodes (7): LiveHealthResponse, ReadyHealthResponse, liveness(), get, Request, Health contract endpoints., readiness()

### Community 73 - "Changes from the Original Mumbai–Goa Demo"
Cohesion: 0.29
Nodes (6): Baseline preserved, Changes from the Original Mumbai–Goa Demo, Compatibility and verification, Documentation and delivery structure, Graphify knowledge graph, R1 generic-trip foundations

### Community 75 - "baseline_snapshot"
Cohesion: 0.60
Nodes (3): baseline_snapshot(), test_t02_connected_journey_projection_matches_dependency_chain(), test_t03_baseline_snapshot_matches_document_04()

## Knowledge Gaps
- **198 isolated node(s):** `paths`, `webhooks`, `components`, `$defs`, `operations` (+193 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 346 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **21 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `ContractModel` connect `ContractModel` to `model_validator`, `models.py`, `CurrentState`, `ServiceCatalog`, `plan_recovery`, `DomainValidationError`, `health.py`, `test_r1_generic_topology.py`, `field_validator`, `repositories.py`, `test_r1_generic_trip_persistence.py`?**
  _High betweenness centrality (0.126) - this node is a cross-community bridge._
- **Why does `TripAggregate` connect `plan_recovery` to `routers/contracts.py`, `model_validator`, `models.py`, `ContractModel`, `field_validator`, `TripRepository`, `repositories.py`?**
  _High betweenness centrality (0.030) - this node is a cross-community bridge._
- **Why does `create_initial_trip()` connect `plan_recovery` to `routers/contracts.py`, `models.py`, `DomainValidationError`, `baseline_snapshot`, `TripRepository`, `repositories.py`?**
  _High betweenness centrality (0.028) - this node is a cross-community bridge._
- **Are the 13 inferred relationships involving `plan_recovery()` (e.g. with `DomainReasonCode` and `FeasibilityStatus`) actually correct?**
  _`plan_recovery()` has 13 INFERRED edges - model-reasoned connections that need verification._
- **Are the 15 inferred relationships involving `create_initial_trip()` (e.g. with `ExecutableScenarioFixture` and `ServiceStatus`) actually correct?**
  _`create_initial_trip()` has 15 INFERRED edges - model-reasoned connections that need verification._
- **Are the 18 inferred relationships involving `TripAggregate` (e.g. with `create_trip()` and `snapshot_for_trip()`) actually correct?**
  _`TripAggregate` has 18 INFERRED edges - model-reasoned connections that need verification._
- **Are the 10 inferred relationships involving `apply_timing_event()` (e.g. with `ServiceStatus` and `TimingReplayEvent`) actually correct?**
  _`apply_timing_event()` has 10 INFERRED edges - model-reasoned connections that need verification._