import type { components } from './schema'

type TripCreated = components['schemas']['TripCreatedResponse']
type EventResponse = components['schemas']['EventResponse']
type PlannerResponse = components['schemas']['PlannerResponse']
type AdoptionResponse = components['schemas']['AdoptionResponse']
type MutationResponse = components['schemas']['MutationResponse']
type ProblemResponse = components['schemas']['ProblemResponse']
type RankingPreset = components['schemas']['RankingPreset']
type ItineraryEditCommand = components['schemas']['ItineraryEditCommand']
type ConstraintsReplaceCommand = components['schemas']['ConstraintsReplaceCommand']
type CurrentStateReplaceCommand = components['schemas']['CurrentStateReplaceCommand']

export class ApiProblem extends Error {
  constructor(public readonly problem: ProblemResponse, public readonly status: number) {
    super(problem.error.message)
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(path, {
    ...init,
    headers: init?.body ? { 'Content-Type': 'application/json', ...init.headers } : init?.headers,
  })
  const payload: unknown = await response.json()
  if (!response.ok) throw new ApiProblem(payload as ProblemResponse, response.status)
  return payload as T
}

function plannerTestControl(): HeadersInit | undefined {
  const mode = new URLSearchParams(window.location.search).get('testMode')
  if (mode === 'partial') return { 'X-ResiliTrip-Test-Control': 'partial_search' }
  if (mode === 'planner-error') return { 'X-ResiliTrip-Test-Control': 'planner_error' }
  return undefined
}

export const api = {
  createDemo: () => request<TripCreated>('/api/v1/trips', {
    method: 'POST', body: JSON.stringify({ source_type: 'fixture', scenario_id: 'mumbai-goa-v2', display_name: 'Asha' }),
  }),
  applyD1: (tripId: string, version: number) => request<EventResponse>(`/api/v1/trips/${encodeURIComponent(tripId)}/events`, {
    method: 'POST', body: JSON.stringify({
      event_id: 'event:D1', source_id: 'replay:mumbai-goa-v2', source_sequence: 1,
      expected_trip_version: version, type: 'SERVICE_TIMING_UPDATED', service_id: 'svc:T1:2026-09-26',
      observed_at: '2026-09-26T05:00:00+05:30', effective_at: '2026-09-26T05:00:00+05:30',
      new_departure_at: '2026-09-26T09:00:00+05:30', new_arrival_at: '2026-09-26T18:30:00+05:30',
      provenance: { id: 'prov:replay:D1', kind: 'synthetic', verification: 'fixture',
        observed_at: '2026-09-26T05:00:00+05:30', retrieved_at: '2026-09-26T05:00:00+05:30',
        valid_until: null, source_ref: 'replay:mumbai-goa-v2' },
    }),
  }),
  generatePlans: (tripId: string, version: number, catalogVersion: string, ranking: RankingPreset) =>
    request<PlannerResponse>(`/api/v1/trips/${encodeURIComponent(tripId)}/plans`, {
      method: 'POST', headers: plannerTestControl(), body: JSON.stringify({ expected_trip_version: version, expected_catalog_version: catalogVersion, ranking_preset: ranking }),
    }),
  adoptPlan: (tripId: string, version: number, planId: string) =>
    request<AdoptionResponse>(`/api/v1/trips/${encodeURIComponent(tripId)}/adoptions`, {
      method: 'POST', body: JSON.stringify({ expected_trip_version: version, plan_id: planId, acknowledge_simulation: true }),
    }),
  editItinerary: (tripId: string, command: ItineraryEditCommand) =>
    request<MutationResponse>(`/api/v1/trips/${encodeURIComponent(tripId)}/itinerary`, { method: 'PUT', body: JSON.stringify(command) }),
  replaceConstraints: (tripId: string, command: ConstraintsReplaceCommand) =>
    request<MutationResponse>(`/api/v1/trips/${encodeURIComponent(tripId)}/constraints`, { method: 'PUT', body: JSON.stringify(command) }),
  replaceCurrentState: (tripId: string, command: CurrentStateReplaceCommand) =>
    request<MutationResponse>(`/api/v1/trips/${encodeURIComponent(tripId)}/current-state`, { method: 'PUT', body: JSON.stringify(command) }),
  reset: (tripId: string, version: number) => request<MutationResponse>(`/api/v1/trips/${encodeURIComponent(tripId)}/reset`, {
    method: 'POST', body: JSON.stringify({ expected_trip_version: version, scenario_id: 'mumbai-goa-v2' }),
  }),
}

export type { AdoptionResponse, ItineraryEditCommand, MutationResponse, PlannerResponse, ProblemResponse, RankingPreset, TripCreated }
