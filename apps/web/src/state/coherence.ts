import type { components } from '../api/schema'

type Snapshot = components['schemas']['TripViewSnapshot']
type PlannerResponse = components['schemas']['PlannerResponse']

export function acceptPlannerResponse(snapshot: Snapshot, response: PlannerResponse) {
  const result = response.planner_result
  if (response.snapshot_version !== snapshot.trip.version || result.trip_version !== snapshot.trip.version ||
      response.catalog_version !== snapshot.trip.catalog_version || result.catalog_version !== snapshot.trip.catalog_version ||
      result.trip_id !== snapshot.trip.id) return null
  return result
}

export function replaceSnapshot(current: Snapshot | null, next: Snapshot) {
  if (current && current.trip.id !== next.trip.id) return null
  return next
}
