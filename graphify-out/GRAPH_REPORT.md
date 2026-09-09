# Graph Report - resilitrip  (2026-09-09)

## Corpus Check
- 125 files · ~187,031 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 649 nodes · 1648 edges · 41 communities (21 shown, 9 thin omitted)
- Extraction: 89% EXTRACTED · 11% INFERRED · 0% AMBIGUOUS · INFERRED: 184 edges (avg confidence: 0.95)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- api/contracts Module
- Live Health Response Module
- client Module
- Api Problem Module
- evaluation Module
- create initial trip() Module
- constraints Module
- Activity Definition Module
- tsconfig.app Module
- accessibility.spec Module
- package Module
- tsconfig.node Module
- dev Dependencies Module
- Containerized Local Runtime Module
- baseline impact chromium win32 Module
- Graphify Watch Mode Module
- scripts Module
- schema.d Module
- setup Module
- dependencies Module
- vite.config Module
- Web Application Mount Module
- engines Module
- tsconfig Module
- api/ init Module
- routers/ init Module
- infrastructure/ init Module
- resilitrip/ init Module
- tools/ init Module
- resilitrip api Module

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

## Communities (41 total, 9 thin omitted)

### Community 0 - "api/contracts Module"
Cohesion: 0.05
Nodes (71): AdoptionCommand, AdoptionRecord, AdoptionResponse, ApiErrorCode, ConstraintsReplaceCommand, CurrentStateReplaceCommand, EventResponse, EventResult (+63 more)

### Community 1 - "Live Health Response Module"
Cohesion: 0.06
Nodes (68): LiveHealthResponse, ReadyHealthResponse, api_problem_handler(), internal_error_handler(), problem_body(), Request, validation_handler(), liveness() (+60 more)

### Community 2 - "client Module"
Cohesion: 0.05
Nodes (61): AdoptionResponse, api, ApiProblem, ConstraintsReplaceCommand, CurrentStateReplaceCommand, EventResponse, ItineraryEditCommand, MutationResponse (+53 more)

### Community 3 - "Api Problem Module"
Cohesion: 0.09
Nodes (43): ApiProblem, adopt_plan(), apply_event_route(), create_trip(), _db(), generate_plans(), get_plan(), get_trip() (+35 more)

### Community 4 - "evaluation Module"
Cohesion: 0.07
Nodes (59): _check(), evaluate_itinerary(), datetime, EvidenceValue, Shared deterministic selected-itinerary evaluator for impact and later planning., Evaluate a complete DAG without mutating catalog, trip, or effective state., _seconds(), _timestamp() (+51 more)

### Community 5 - "create initial trip() Module"
Cohesion: 0.10
Nodes (53): create_initial_trip(), apply_cancellation_event(), apply_timing_event(), calculate_impacts(), evaluate_trip(), Pure timing-event application and deterministic impact diffing., Create an isolated immutable service-state branch for fixture perturbation…, replace_service_state() (+45 more)

### Community 6 - "constraints Module"
Cohesion: 0.22
Nodes (19): classify_slack(), hotel_start_is_valid(), meets_cutoff(), money_within_limits(), plan_is_valid(), datetime, Exact, side-effect-free A1 constraint boundary rules., Classify slack: zero remains feasible but at risk; threshold itself is safe. (+11 more)

### Community 7 - "Activity Definition Module"
Cohesion: 0.22
Nodes (17): ActivityDefinition, ActivityKind, Dependency, build_catalog_indexes(), _candidate_id(), CatalogIndexes, derive_recovery_frontier(), enumerate_atomic_candidates() (+9 more)

### Community 8 - "tsconfig.app Module"
Cohesion: 0.11
Nodes (17): compilerOptions, allowJs, allowSyntheticDefaultImports, esModuleInterop, isolatedModules, jsx, lib, module (+9 more)

### Community 9 - "accessibility.spec Module"
Cohesion: 0.40
Nodes (5): applyD1(), generatePlans(), loadDemo(), previewF3(), @playwright/test

### Community 10 - "package Module"
Cohesion: 0.13
Nodes (14): name, private, type, version, @axe-core/playwright, jsdom, maplibre-gl, openapi-typescript (+6 more)

### Community 11 - "tsconfig.node Module"
Cohesion: 0.14
Nodes (13): compilerOptions, allowImportingTsExtensions, lib, module, moduleDetection, moduleResolution, noEmit, skipLibCheck (+5 more)

### Community 12 - "dev Dependencies Module"
Cohesion: 0.15
Nodes (13): devDependencies, @axe-core/playwright, jsdom, openapi-typescript, @playwright/test, @testing-library/react, @types/node, @types/react (+5 more)

### Community 13 - "Containerized Local Runtime Module"
Cohesion: 0.27
Nodes (12): Containerized Local Runtime, Planner Golden Outputs, Mumbai Goa Hero Recovery Scenario, Product Scope Lock, Shared Constraint Evaluator Principle, Product Requirements, Travel Recovery Domain Model, Canonical Mumbai Goa Fixture (+4 more)

### Community 14 - "baseline impact chromium win32 Module"
Cohesion: 0.18
Nodes (11): baseline impact chromium win32, baseline workspace chromium win32, recovery comparison chromium win32, journey editor warning chromium win32, offline map fallback chromium win32, 07 API and Data Contract Specification, 08 UX Interaction and Demo Specification, 09 Test Strategy and Golden Validation Specification (+3 more)

### Community 15 - "Graphify Watch Mode Module"
Cohesion: 0.22
Nodes (10): Graphify Watch Mode, Graphify Optional Exports, Semantic Extraction Schema, Cross Repository Graph Merge, Post Commit Graph Update Hook, Graph Query Navigation, Media Transcription, Incremental Re-extraction (+2 more)

### Community 16 - "scripts Module"
Cohesion: 0.33
Nodes (6): scripts, build, dev, test, test:e2e, test:watch

### Community 17 - "schema.d Module"
Cohesion: 0.33
Nodes (5): components, $defs, operations, paths, webhooks

### Community 19 - "dependencies Module"
Cohesion: 0.40
Nodes (5): dependencies, maplibre-gl, react, react-dom, @xyflow/react

### Community 21 - "Web Application Mount Module"
Cohesion: 0.67
Nodes (3): Web Application Mount, Typed API Boundary, Versioned Trip Snapshot

### Community 22 - "engines Module"
Cohesion: 0.67
Nodes (3): engines, node, npm

## Knowledge Gaps
- **116 isolated node(s):** `resilitrip-api`, `name`, `version`, `private`, `type` (+111 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 219 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **9 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `ContractModel` connect `api/contracts Module` to `Live Health Response Module`, `Api Problem Module`, `evaluation Module`, `create initial trip() Module`, `constraints Module`, `Activity Definition Module`?**
  _High betweenness centrality (0.041) - this node is a cross-community bridge._
- **Why does `TripAggregate` connect `Api Problem Module` to `api/contracts Module`, `evaluation Module`, `create initial trip() Module`, `Activity Definition Module`?**
  _High betweenness centrality (0.038) - this node is a cross-community bridge._
- **Why does `load_fixture()` connect `Live Health Response Module` to `api/contracts Module`, `Api Problem Module`, `create initial trip() Module`?**
  _High betweenness centrality (0.032) - this node is a cross-community bridge._
- **Are the 6 inferred relationships involving `plan_recovery()` (e.g. with `DomainReasonCode` and `FeasibilityStatus`) actually correct?**
  _`plan_recovery()` has 6 INFERRED edges - model-reasoned connections that need verification._
- **Are the 18 inferred relationships involving `TripAggregate` (e.g. with `create_trip()` and `snapshot_for_trip()`) actually correct?**
  _`TripAggregate` has 18 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `create_initial_trip()` (e.g. with `ExecutableScenarioFixture` and `ServiceStatus`) actually correct?**
  _`create_initial_trip()` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `load_fixture()` (e.g. with `ExecutableScenarioFixture` and `DomainValidationError`) actually correct?**
  _`load_fixture()` has 2 INFERRED edges - model-reasoned connections that need verification._