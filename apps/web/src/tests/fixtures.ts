import type { components } from '../api/schema'

type Snapshot = components['schemas']['TripViewSnapshot']
type Plan = components['schemas']['PlanEvaluation']

const provenance = { id: 'prov:test', kind: 'synthetic' as const, verification: 'fixture' as const, observed_at: '2026-09-26T05:00:00+05:30', retrieved_at: '2026-09-26T05:00:00+05:30', valid_until: null, source_ref: 'test' }
const activities = [
  { id: 'act:train', kind: 'fixed_transport' as const, hard: true, booking_id: null, provenance_id: 'prov:test', service_id: 'svc:train', transfer_template_id: null, location_id: null, duration_sec: null, earliest_start: null, latest_start: null, start_at: null, readiness_allowance_sec: null, derived_from_service_id: null },
  { id: 'act:wedding', kind: 'commitment' as const, hard: true, booking_id: null, provenance_id: 'prov:test', service_id: null, transfer_template_id: null, location_id: 'place:wedding', duration_sec: null, earliest_start: null, latest_start: null, start_at: '2026-09-26T20:00:00+05:30', readiness_allowance_sec: 2700, derived_from_service_id: null },
]
const dependencies = [{ id: 'dep:one', from_id: 'act:train', to_id: 'act:wedding', buffer_sec: 0, reason: 'connected' }]

export function makeSnapshot(version = 2): Snapshot {
  return {
    trip: { schema_version: 'resilitrip-api-1.0', id: 'trip:test', version, scenario_id: 'mumbai-goa-v2', mode: 'demo', lifecycle: 'active', display_timezone: 'Asia/Kolkata', currency: 'INR', truth_label: 'SYNTHETIC SCENARIO — NOT BOOKABLE', traveler: { party_size: 1, display_name: 'Asha', accessibility_required: false }, catalog_version: 'catalog:test', decision_allowance_sec: 900,
      current_state: { as_of: '2026-09-26T05:00:00+05:30', location_id: 'rail:mumbai', phase: 'at_location', active_service_id: null, completed_activity_ids: [], next_recovery_point_id: null, provenance_id: 'prov:test' },
      constraints: { party_size: 1, max_cash_required_paise: 1000000, max_incremental_cost_paise: 900000, allowed_modes: ['rail','air','road_transfer'], required_commitment_ids: ['act:wedding'], accessibility_required: false, ranking_preset: 'cheapest', max_new_fixed_legs: 2, max_transfer_legs: 8, horizon_end: '2026-09-27T05:00:00+05:30', risk_threshold_sec: 1800 },
      original_itinerary: { activities, dependencies }, active_itinerary: { activities, dependencies }, bookings: [], baseline_money_items: [], baseline_remaining_spend_paise: 130000,
      effective_services: [{ service_id: 'svc:train', effective_departure: '2026-09-26T06:00:00+05:30', effective_arrival: '2026-09-26T15:30:00+05:30', status: 'scheduled', last_event_id: null, provenance_id: 'prov:test' }], provenance: [provenance], constraints_provenance_id: 'prov:test', adopted_plan_id: null, last_mutation_kind: 'event' },
    catalog: { schema_version: 'resilitrip-api-1.0', catalog_version: 'catalog:test', scenario_id: 'mumbai-goa-v2', display_timezone: 'Asia/Kolkata', currency: 'INR',
      locations: [{ id: 'rail:mumbai', name: 'Mumbai CSMT', kind: 'rail_station', code: 'CSMT', terminal: null, latitude: 18.94, longitude: 72.835, provenance_id: 'prov:test', field_provenance: [] }, { id: 'place:wedding', name: 'Goa wedding venue', kind: 'venue', code: null, terminal: null, latitude: 15.54, longitude: 73.95, provenance_id: 'prov:test', field_provenance: [] }],
      services: [{ id: 'svc:train', display_code: 'T1', mode: 'rail', origin_id: 'rail:mumbai', destination_id: 'place:wedding', scheduled_departure: '2026-09-26T06:00:00+05:30', scheduled_arrival: '2026-09-26T15:30:00+05:30', service_date: '2026-09-26', origin_allowance_sec: 0, exit_allowance_sec: 0, capacity: 1, price_paise: 130000, price_state: 'paid', policy_id: 'policy:test', provenance_id: 'prov:test', field_provenance: [] }], transfer_templates: [], policies: [], provenance: [provenance] },
    evaluated_itinerary: [{ activity_id: 'act:train', kind: 'fixed_transport', origin_id: 'rail:mumbai', destination_id: 'place:wedding', service_id: 'svc:train', transfer_template_id: null, start_at: '2026-09-26T06:00:00+05:30', end_at: '2026-09-26T15:30:00+05:30', ready_at: '2026-09-26T15:30:00+05:30', cutoff_at: null, slack_sec: null, status: 'feasible', reason_codes: [], provenance_ids: ['prov:test'] }, { activity_id: 'act:wedding', kind: 'commitment', origin_id: 'place:wedding', destination_id: 'place:wedding', service_id: null, transfer_template_id: null, start_at: '2026-09-26T17:50:00+05:30', end_at: '2026-09-26T17:50:00+05:30', ready_at: '2026-09-26T17:50:00+05:30', cutoff_at: '2026-09-26T19:15:00+05:30', slack_sec: 5100, status: 'feasible', reason_codes: [], provenance_ids: ['prov:test'] }],
    overall_status: 'feasible', impacts: [], provenance: [provenance], available_actions: { can_apply_event: true, can_edit_constraints: true, can_edit_current_state: true, can_edit_itinerary: true, can_generate_plans: true, can_adopt_plan: false, can_reset: true },
  }
}

export function makePlan(): Plan {
  const snapshot = makeSnapshot()
  return { id: 'plan:test', trip_id: snapshot.trip.id, trip_version: 2, catalog_version: snapshot.trip.catalog_version, run_id: 'run:test', lifecycle_status: 'preview', evaluation_status: 'feasible', valid_until: '2026-09-26T05:15:00+05:30', sequence_ids: ['svc:train'], sequence_signature: 'a'.repeat(64), proposed_itinerary: snapshot.trip.active_itinerary, activity_sequence: snapshot.evaluated_itinerary, service_ids: ['svc:train'], transfer_template_ids: [], money_items: [], cash_required_paise: 650000, incremental_cost_paise: 520000, potential_refund_paise: null, final_required_arrival_at: '2026-09-26T17:20:00+05:30', event_slack_sec: 6900, changed_original_booking_ids: [], constraint_checks: [], provenance_ids: ['prov:test'], objective_values: { cash_required_paise: 650000, final_required_arrival_at: '2026-09-26T17:20:00+05:30', changed_original_booking_count: 2 }, frontier_member: true, display_rank: 1, ranking_reason_code: 'LOWEST_CASH_ON_FRONTIER', simulated: true, bookable: false, reason_codes: ['HARD_CONSTRAINTS_PASS'] }
}
