# Graph Report - resilitrip  (2026-09-09)

## Corpus Check
- 138 files · ~177,221 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 973 nodes · 2591 edges · 76 communities (46 shown, 19 thin omitted)
- Extraction: 88% EXTRACTED · 12% INFERRED · 0% AMBIGUOUS · INFERRED: 298 edges (avg confidence: 0.95)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `e8098298`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- routers/contracts.py
- App.tsx
- models.py
- ContractModel
- repositories.py
- create_initial_trip
- helpers.ts
- test_r1_goal_evaluation.py
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
- test_r1_generic_trip_persistence.py
- Gate A0 compatibility record
- resilitrip-api
- graphify reference: extra exports and benchmark
- 4. Essential distinctions
- 7. State vocabularies
- setup.ts
- load_fixture
- dependencies
- graphify reference: query, path, explain
- GenericTripAggregate
- 9. Time model
- engines
- graphify reference: add a URL and watch a folder
- graphify reference: commit hook and native CLAUDE.md integration
- graphify reference: incremental update and cluster-only
- 11. Financial model
- 12. Constraint model
- 5. Aggregate roots and versioning
- test_r1_composed_evaluation.py
- graphify reference: GitHub clone and cross-repo merge
- graphify reference: transcribe video and audio
- 8. State transitions
- README.md
- model_validator
- connect
- TripLifecycle
- CurrentState
- ServiceCatalog
- semantic_snapshots.py
- DomainValidationError
- health.py
- Changes from the Original Mumbai–Goa Demo
- field_validator
- baseline_snapshot

## God Nodes (most connected - your core abstractions)
1. `ContractModel` - 99 edges
2. `create_initial_trip()` - 52 edges
3. `plan_recovery()` - 52 edges
4. `apply_timing_event()` - 40 edges
5. `TripAggregate` - 34 edges
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
- `ManualTripCreate` --uses--> `CurrentState`  [INFERRED]
  apps/api/resilitrip/api/contracts.py → apps/api/resilitrip/domain/models.py

## Import Cycles
- None detected.

## Communities (76 total, 19 thin omitted)

### Community 0 - "routers/contracts.py"
Cohesion: 0.14
Nodes (35): ApiProblem, adopt_plan(), apply_event_route(), create_trip(), _db(), generate_plans(), get_plan(), get_trip() (+27 more)

### Community 1 - "App.tsx"
Cohesion: 0.05
Nodes (61): AdoptionResponse, api, ApiProblem, ConstraintsReplaceCommand, CurrentStateReplaceCommand, EventResponse, ItineraryEditCommand, MutationResponse (+53 more)

### Community 2 - "models.py"
Cohesion: 0.05
Nodes (90): evaluate_baseline(), Baseline itinerary projection only; recovery planning is intentionally absent., classify_slack(), hotel_start_is_valid(), meets_cutoff(), money_within_limits(), plan_is_valid(), datetime (+82 more)

### Community 3 - "ContractModel"
Cohesion: 0.16
Nodes (24): AdoptionCommand, AdoptionRecord, AdoptionResponse, ApiErrorCode, EventResponse, EventResult, FixtureTripCreate, MutationResponse (+16 more)

### Community 4 - "repositories.py"
Cohesion: 0.27
Nodes (5): canonical_json(), content_hash(), generic_snapshot_hash(), Canonical, hash-checked SQLite repositories for Gate A3., snapshot_hash()

### Community 5 - "create_initial_trip"
Cohesion: 0.09
Nodes (63): create_initial_trip(), Gate A1 creation of a version-one trip and its baseline projection., snapshot_for_trip(), apply_timing_event(), calculate_impacts(), evaluate_trip(), Pure timing-event application and deterministic impact diffing., Create an isolated immutable service-state branch for fixture perturbation… (+55 more)

### Community 6 - "helpers.ts"
Cohesion: 0.36
Nodes (6): applyD1(), generatePlans(), loadDemo(), previewF3(), @axe-core/playwright, @playwright/test

### Community 7 - "test_r1_goal_evaluation.py"
Cohesion: 0.17
Nodes (24): evaluate_structurally(), EvaluationReasonCode, FactKnowledge, GoalFact, GoalRequirementStrength, ProcessCutoffRule, datetime, model_validator (+16 more)

### Community 8 - "package.json"
Cohesion: 0.12
Nodes (15): name, private, type, version, jsdom, maplibre-gl, openapi-typescript, react-dom (+7 more)

### Community 9 - "compilerOptions"
Cohesion: 0.11
Nodes (17): compilerOptions, allowJs, allowSyntheticDefaultImports, esModuleInterop, isolatedModules, jsx, lib, module (+9 more)

### Community 10 - "ResiliTrip README"
Cohesion: 0.15
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
Cohesion: 0.12
Nodes (17): 10. Location and continuity model, 13. Event and immutability rules, 14. Provenance and uncertainty rules, 15. Canonical reason codes, 16. Identifier conventions, 17. Compact record example, 18. India travel glossary, 19. Cross-entity invariants (+9 more)

### Community 17 - "Graphify skill"
Cohesion: 0.67
Nodes (3): Graphify semantic extraction specification, Graphify skill, persistent knowledge graph

### Community 29 - "6. Entity definitions"
Cohesion: 0.11
Nodes (18): 6. Entity definitions, DM-01 — TravelerProfile, DM-02 — CurrentState, DM-03 — Location, DM-04 — ServiceInstance, DM-05 — TransferTemplate, DM-06 — Activity, DM-07 — Dependency (+10 more)

### Community 30 - "test_r1_generic_trip_persistence.py"
Cohesion: 0.31
Nodes (13): append_snapshot(), EvaluationSnapshotHistory, Return a new frozen history, preserving every prior immutable snapshot., An append-only in-memory history; prior frozen snapshots are never rewritten., aggregate(), at(), datetime, Integration coverage for the isolated append-only generic R1 namespace. (+5 more)

### Community 44 - "graphify reference: extra exports and benchmark"
Cohesion: 0.22
Nodes (8): graphify reference: extra exports and benchmark, Step 6b - Wiki (only if --wiki flag), Step 7 - Neo4j export (only if --neo4j or --neo4j-push flag), Step 7a - FalkorDB export (only if --falkordb or --falkordb-push flag), Step 7b - SVG export (only if --svg flag), Step 7c - GraphML export (only if --graphml flag), Step 7d - MCP server (only if --mcp flag), Step 8 - Token reduction benchmark (only if total_words > 5000)

### Community 45 - "4. Essential distinctions"
Cohesion: 0.29
Nodes (7): 4.1 Trip versus itinerary, 4.2 Service instance versus activity, 4.3 Transfer template versus transfer activity, 4.4 Booking versus physical movement, 4.5 Dependency graph versus search graph, 4.6 Scheduled, effective and observed time, 4. Essential distinctions

### Community 46 - "7. State vocabularies"
Cohesion: 0.29
Nodes (7): 7.1 Current traveler phase, 7.2 Service status, 7.3 Feasibility status, 7.4 Planner result status, 7.5 Booking knowledge state, 7.6 Source display status, 7. State vocabularies

### Community 48 - "load_fixture"
Cohesion: 0.08
Nodes (52): api_problem_handler(), internal_error_handler(), problem_body(), Request, validation_handler(), default_settings(), Configuration for the local-only P0 application., Settings intentionally limited to the Gate A0 infrastructure needs. (+44 more)

### Community 49 - "dependencies"
Cohesion: 0.40
Nodes (5): dependencies, maplibre-gl, react, react-dom, @xyflow/react

### Community 50 - "graphify reference: query, path, explain"
Cohesion: 0.33
Nodes (5): For /graphify explain, For /graphify path, graphify reference: query, path, explain, Step 0 — Constrained query expansion (REQUIRED before traversal), Step 1 — Traversal

### Community 51 - "GenericTripAggregate"
Cohesion: 0.18
Nodes (6): GenericTripAggregate, field_validator, model_validator, A versioned generic trip and its immutable semantic evaluation history., GenericTripRepository, Append-only, hash-checked persistence for the isolated R1 aggregate.

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

### Community 60 - "test_r1_composed_evaluation.py"
Cohesion: 0.06
Nodes (101): compose_evaluation(), ComposedMoney, ComposedOutcome, CompositionReason, CompositionReasonCode, EvidenceReference, GenericCompositionInput, StrEnum (+93 more)

### Community 63 - "8. State transitions"
Cohesion: 0.67
Nodes (3): 8.1 Trip and plan lifecycle, 8.2 Event disposition, 8. State transitions

### Community 65 - "model_validator"
Cohesion: 0.14
Nodes (4): Location, PolicyRecord, model_validator, ServiceDefinition

### Community 66 - "connect"
Cohesion: 0.15
Nodes (23): Connection, seed_catalog(), connect(), _initial_schema(), initialize(), Connection, Path, _r1_generic_trip_namespace() (+15 more)

### Community 67 - "TripLifecycle"
Cohesion: 0.18
Nodes (7): Isolated aggregate for persisted generic R1 trips. This model intentionally…, TripLifecycle, TripMode, _checked(), parametrize, test_r1_demo_trip_defaults_to_active_lifecycle(), test_r1_rejects_invalid_mode_lifecycle_or_truth_label_combinations()

### Community 68 - "CurrentState"
Cohesion: 0.25
Nodes (14): ConstraintsReplaceCommand, Frozen-prefix validation for the future-itinerary replacement contract., validate_itinerary_replacement(), CurrentState, ItineraryDefinition, TravelerPhase, Validate a standalone replacement itinerary before it can become active., validate_dependency_dag() (+6 more)

### Community 69 - "ServiceCatalog"
Cohesion: 0.26
Nodes (13): CurrentStateReplaceCommand, ItineraryEditCommand, ManualTripCreate, Booking, Constraints, MoneyItem, ProvenanceRecord, ServiceCatalog (+5 more)

### Community 70 - "semantic_snapshots.py"
Cohesion: 0.27
Nodes (10): GenericCompositionResult, create_evaluation_snapshot(), ImmutableEvaluationSnapshot, datetime, model_validator, Immutable, semantic alternative-plan evaluation snapshots for generic R1 work., Stable semantic identity and its revision; intentionally no rank or score., Create a content-hashed snapshot from a deterministic composed evaluation. (+2 more)

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
- **198 isolated node(s):** `resilitrip-api`, `name`, `version`, `private`, `type` (+193 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 345 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **19 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `ContractModel` connect `ContractModel` to `model_validator`, `models.py`, `TripLifecycle`, `CurrentState`, `ServiceCatalog`, `semantic_snapshots.py`, `test_r1_goal_evaluation.py`, `health.py`, `create_initial_trip`, `field_validator`, `DomainValidationError`, `GenericTripAggregate`, `test_r1_composed_evaluation.py`, `test_r1_generic_trip_persistence.py`?**
  _High betweenness centrality (0.102) - this node is a cross-community bridge._
- **Why does `create_initial_trip()` connect `create_initial_trip` to `routers/contracts.py`, `connect`, `models.py`, `TripLifecycle`, `DomainValidationError`, `test_r1_goal_evaluation.py`, `baseline_snapshot`, `load_fixture`, `test_r1_composed_evaluation.py`, `test_r1_generic_trip_persistence.py`?**
  _High betweenness centrality (0.046) - this node is a cross-community bridge._
- **Why does `plan_recovery()` connect `create_initial_trip` to `routers/contracts.py`, `models.py`, `test_r1_goal_evaluation.py`, `test_r1_composed_evaluation.py`, `test_r1_generic_trip_persistence.py`?**
  _High betweenness centrality (0.039) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `create_initial_trip()` (e.g. with `ExecutableScenarioFixture` and `ServiceStatus`) actually correct?**
  _`create_initial_trip()` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Are the 6 inferred relationships involving `plan_recovery()` (e.g. with `DomainReasonCode` and `FeasibilityStatus`) actually correct?**
  _`plan_recovery()` has 6 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `apply_timing_event()` (e.g. with `ServiceStatus` and `TimingReplayEvent`) actually correct?**
  _`apply_timing_event()` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Are the 18 inferred relationships involving `TripAggregate` (e.g. with `create_trip()` and `snapshot_for_trip()`) actually correct?**
  _`TripAggregate` has 18 INFERRED edges - model-reasoned connections that need verification._