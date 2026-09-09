# Graph Report - resilitrip  (2026-09-09)

## Corpus Check
- 119 files · ~187,525 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 657 nodes · 1656 edges · 42 communities (22 shown, 9 thin omitted)
- Extraction: 89% EXTRACTED · 11% INFERRED · 0% AMBIGUOUS · INFERRED: 184 edges (avg confidence: 0.95)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `a3f14148`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- ContractModel
- load_fixture
- App.tsx
- routers/contracts.py
- models.py
- plan_recovery
- constraints.py
- recovery.py
- compilerOptions
- helpers.ts
- package.json
- compilerOptions
- devDependencies
- ResiliTrip Repository Context
- DomainValidationError
- Graphify Pipeline
- scripts
- schema.d.ts
- setup.ts
- dependencies
- @vitejs/plugin-react
- Typed API Boundary
- engines
- tsconfig.json
- api/__init__.py
- routers/__init__.py
- infrastructure/__init__.py
- resilitrip/__init__.py
- tools/__init__.py
- resilitrip-api
- ResiliTrip AI Context

## God Nodes (most connected - your core abstractions)
1. `ContractModel` - 58 edges
2. `plan_recovery()` - 38 edges
3. `TripAggregate` - 33 edges
4. `create_initial_trip()` - 32 edges
5. `load_fixture()` - 29 edges
6. `create_app()` - 27 edges
7. `apply_timing_event()` - 26 edges
8. `TripRepository` - 26 edges
9. `evaluate_itinerary()` - 21 edges
10. `ServiceCatalog` - 20 edges

## Surprising Connections (you probably didn't know these)
- `ResiliTrip Repository Context` --references--> `baseline impact chromium win32`  [EXTRACTED]
  README.md → apps/web/e2e/hero.spec.ts-snapshots/baseline-impact-chromium-win32.png
- `ResiliTrip Repository Context` --references--> `baseline workspace chromium win32`  [EXTRACTED]
  README.md → apps/web/e2e/hero.spec.ts-snapshots/baseline-workspace-chromium-win32.png
- `ResiliTrip Repository Context` --references--> `recovery comparison chromium win32`  [EXTRACTED]
  README.md → apps/web/e2e/hero.spec.ts-snapshots/recovery-comparison-chromium-win32.png
- `ResiliTrip Repository Context` --references--> `journey editor warning chromium win32`  [EXTRACTED]
  README.md → apps/web/e2e/itinerary-edit.spec.ts-snapshots/journey-editor-warning-chromium-win32.png
- `ResiliTrip Repository Context` --references--> `offline map fallback chromium win32`  [EXTRACTED]
  README.md → apps/web/e2e/offline.spec.ts-snapshots/offline-map-fallback-chromium-win32.png

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Persistent Graph Knowledge Workflow** — _codex_skills_graphify_skill_graphify_pipeline, agents_graphify_repository_workflow, _codex_skills_graphify_references_update_incremental_reextraction [EXTRACTED 1.00]
- **Hero Fixture Planner Validation Flow** — docs_04_reference_scenario_and_fixture_specification_canonical_fixture, docs_05_algorithm_and_recovery_planning_specification_bounded_recovery_planner, data_golden_readme_planner_golden_outputs [EXTRACTED 1.00]
- **ResiliTrip Delivery Contract** — docs_01_product_decision_and_scope_lock_product_scope_lock, docs_02_product_requirements_document_product_requirements, docs_06_technical_architecture_specification_local_first_architecture [EXTRACTED 1.00]

## Communities (42 total, 9 thin omitted)

### Community 0 - "ContractModel"
Cohesion: 0.06
Nodes (62): AdoptionCommand, AdoptionRecord, AdoptionResponse, ApiErrorCode, ConstraintsReplaceCommand, CurrentStateReplaceCommand, EventResponse, EventResult (+54 more)

### Community 1 - "load_fixture"
Cohesion: 0.07
Nodes (62): api_problem_handler(), internal_error_handler(), problem_body(), Request, validation_handler(), default_settings(), Configuration for the local-only P0 application., Settings intentionally limited to the Gate A0 infrastructure needs. (+54 more)

### Community 2 - "App.tsx"
Cohesion: 0.05
Nodes (61): AdoptionResponse, api, ApiProblem, ConstraintsReplaceCommand, CurrentStateReplaceCommand, EventResponse, ItineraryEditCommand, MutationResponse (+53 more)

### Community 3 - "routers/contracts.py"
Cohesion: 0.09
Nodes (43): ApiProblem, adopt_plan(), apply_event_route(), create_trip(), _db(), generate_plans(), get_plan(), get_trip() (+35 more)

### Community 4 - "models.py"
Cohesion: 0.07
Nodes (60): _check(), evaluate_itinerary(), datetime, EvidenceValue, Shared deterministic selected-itinerary evaluator for impact and later planning., Evaluate a complete DAG without mutating catalog, trip, or effective state., _seconds(), _timestamp() (+52 more)

### Community 5 - "plan_recovery"
Cohesion: 0.11
Nodes (52): create_initial_trip(), apply_cancellation_event(), apply_timing_event(), calculate_impacts(), evaluate_trip(), Pure timing-event application and deterministic impact diffing., Create an isolated immutable service-state branch for fixture perturbation…, replace_service_state() (+44 more)

### Community 6 - "constraints.py"
Cohesion: 0.22
Nodes (18): classify_slack(), hotel_start_is_valid(), meets_cutoff(), money_within_limits(), plan_is_valid(), datetime, Exact, side-effect-free A1 constraint boundary rules., Classify slack: zero remains feasible but at risk; threshold itself is safe. (+10 more)

### Community 7 - "recovery.py"
Cohesion: 0.22
Nodes (17): ActivityDefinition, ActivityKind, Dependency, build_catalog_indexes(), _candidate_id(), CatalogIndexes, derive_recovery_frontier(), enumerate_atomic_candidates() (+9 more)

### Community 8 - "compilerOptions"
Cohesion: 0.11
Nodes (17): compilerOptions, allowJs, allowSyntheticDefaultImports, esModuleInterop, isolatedModules, jsx, lib, module (+9 more)

### Community 9 - "helpers.ts"
Cohesion: 0.40
Nodes (5): applyD1(), generatePlans(), loadDemo(), previewF3(), @playwright/test

### Community 10 - "package.json"
Cohesion: 0.13
Nodes (14): name, private, type, version, @axe-core/playwright, jsdom, maplibre-gl, openapi-typescript (+6 more)

### Community 11 - "compilerOptions"
Cohesion: 0.14
Nodes (13): compilerOptions, allowImportingTsExtensions, lib, module, moduleDetection, moduleResolution, noEmit, skipLibCheck (+5 more)

### Community 12 - "devDependencies"
Cohesion: 0.15
Nodes (13): devDependencies, @axe-core/playwright, jsdom, openapi-typescript, @playwright/test, @testing-library/react, @types/node, @types/react (+5 more)

### Community 13 - "ResiliTrip Repository Context"
Cohesion: 0.11
Nodes (23): baseline impact chromium win32, baseline workspace chromium win32, recovery comparison chromium win32, journey editor warning chromium win32, offline map fallback chromium win32, Containerized Local Runtime, Planner Golden Outputs, Mumbai Goa Hero Recovery Scenario (+15 more)

### Community 14 - "DomainValidationError"
Cohesion: 0.15
Nodes (16): baseline_snapshot(), Gate A1 creation of a version-one trip and its baseline projection., evaluate_baseline(), Baseline itinerary projection only; recovery planning is intentionally absent., EvaluatedActivity, ExecutableScenarioFixture, DomainValidationError, ValueError (+8 more)

### Community 15 - "Graphify Pipeline"
Cohesion: 0.22
Nodes (10): Graphify Watch Mode, Graphify Optional Exports, Semantic Extraction Schema, Cross Repository Graph Merge, Post Commit Graph Update Hook, Graph Query Navigation, Media Transcription, Incremental Re-extraction (+2 more)

### Community 16 - "scripts"
Cohesion: 0.33
Nodes (6): scripts, build, dev, test, test:e2e, test:watch

### Community 17 - "schema.d.ts"
Cohesion: 0.33
Nodes (5): components, $defs, operations, paths, webhooks

### Community 19 - "dependencies"
Cohesion: 0.40
Nodes (5): dependencies, maplibre-gl, react, react-dom, @xyflow/react

### Community 21 - "Typed API Boundary"
Cohesion: 0.67
Nodes (3): Web Application Mount, Typed API Boundary, Versioned Trip Snapshot

### Community 22 - "engines"
Cohesion: 0.67
Nodes (3): engines, node, npm

### Community 41 - "ResiliTrip AI Context"
Cohesion: 0.25
Nodes (7): Architecture, Change safety, Core invariants, Graph MCP, Local workflow, ResiliTrip AI Context, Start here

## Knowledge Gaps
- **121 isolated node(s):** `resilitrip-api`, `name`, `version`, `private`, `type` (+116 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 225 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **9 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `ContractModel` connect `ContractModel` to `routers/contracts.py`, `models.py`, `plan_recovery`, `constraints.py`, `recovery.py`, `DomainValidationError`?**
  _High betweenness centrality (0.040) - this node is a cross-community bridge._
- **Why does `TripAggregate` connect `routers/contracts.py` to `ContractModel`, `models.py`, `plan_recovery`, `recovery.py`, `DomainValidationError`?**
  _High betweenness centrality (0.037) - this node is a cross-community bridge._
- **Why does `load_fixture()` connect `load_fixture` to `routers/contracts.py`, `plan_recovery`, `DomainValidationError`?**
  _High betweenness centrality (0.031) - this node is a cross-community bridge._
- **Are the 6 inferred relationships involving `plan_recovery()` (e.g. with `DomainReasonCode` and `FeasibilityStatus`) actually correct?**
  _`plan_recovery()` has 6 INFERRED edges - model-reasoned connections that need verification._
- **Are the 18 inferred relationships involving `TripAggregate` (e.g. with `create_trip()` and `snapshot_for_trip()`) actually correct?**
  _`TripAggregate` has 18 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `create_initial_trip()` (e.g. with `ExecutableScenarioFixture` and `ServiceStatus`) actually correct?**
  _`create_initial_trip()` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `load_fixture()` (e.g. with `ExecutableScenarioFixture` and `DomainValidationError`) actually correct?**
  _`load_fixture()` has 2 INFERRED edges - model-reasoned connections that need verification._