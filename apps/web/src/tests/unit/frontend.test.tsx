import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { api, ApiProblem } from '../../api/client'
import { AdoptionSheet } from '../../app/App'
import { JourneyEditor } from '../../components/JourneyEditor'
import { JourneyMap } from '../../components/JourneyMap'
import { RankingControl } from '../../components/RankingControl'
import { StatePanel } from '../../components/StatePanel'
import { acceptPlannerResponse, replaceSnapshot } from '../../state/coherence'
import { consumerCopy } from '../../ui/copy'
import { formatINR, formatIST, formatMargin } from '../../ui/format'
import { makePlan, makeSnapshot } from '../fixtures'

afterEach(() => vi.restoreAllMocks())

describe('generated API client', () => {
  it('sends the typed fixture command and returns a successful payload', async () => {
    const snapshot = makeSnapshot(1)
    const fetchMock = vi.spyOn(globalThis, 'fetch').mockResolvedValue(new Response(JSON.stringify({ trip_id: 'trip:test', trip_version: 1, catalog_version: 'catalog:test', snapshot }), { status: 201, headers: { 'Content-Type': 'application/json' } }))
    const response = await api.createDemo()
    expect(response.snapshot.trip.version).toBe(1)
    expect(JSON.parse(String(fetchMock.mock.calls[0][1]?.body))).toEqual({ source_type: 'fixture', scenario_id: 'mumbai-goa-v2', display_name: 'Asha' })
  })

  it('normalizes a problem response into ApiProblem', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValue(new Response(JSON.stringify({ error: { code: 'STALE_PLAN', message: 'stale', request_id: 'req:test', retryable: true, field_errors: [], current_trip_version: 3, current_catalog_version: 'catalog:test' } }), { status: 409, headers: { 'Content-Type': 'application/json' } }))
    await expect(api.adoptPlan('trip:test', 2, 'plan:test')).rejects.toBeInstanceOf(ApiProblem)
  })
})

describe('snapshot coherence and consumer copy', () => {
  it('rejects a late planner response and preserves the last good snapshot', () => {
    const snapshot = makeSnapshot(3)
    const plan = makePlan()
    const response = { snapshot_version: 2, catalog_version: 'catalog:test', planner_result: { run_id: 'run:test', trip_id: 'trip:test', trip_version: 2, catalog_version: 'catalog:test', ranking_preset: 'cheapest' as const, result_status: 'complete' as const, search_complete: true, interruption_reason: null, scope: { catalog_version: 'catalog:test', replay_as_of: '2026-09-26T05:00:00+05:30', horizon_end: '2026-09-27T05:00:00+05:30', max_catalog_services: 50, max_new_fixed_legs: 2, max_transfer_legs: 8, max_activities: 20 as const }, counts: { states_expanded: 1, complete_paths: 1, duplicate_paths: 0, feasible_total: 1, uncertain_total: 0, rejected_total: 0, frontier_total: 1, displayed_total: 1, pruned_by_reason: {} }, runtime_ms: 0, feasible_plans: [plan], uncertain_plans: [], rejected_plans: [] } }
    expect(acceptPlannerResponse(snapshot, response)).toBeNull()
    expect(replaceSnapshot(snapshot, makeSnapshot(4))?.trip.version).toBe(4)
    expect(consumerCopy('STALE_PLAN')).toContain('older journey')
  })

  it('formats INR, IST and server-provided margins without deriving eligibility', () => {
    expect(formatINR(650000)).toBe('₹6,500')
    expect(formatINR(null)).toBe('Unknown')
    expect(formatIST('2026-09-26T17:20:00+05:30')).toContain('5:20 pm IST')
    expect(formatMargin(-5700)).toBe('95 minutes late')
    expect(formatMargin(0)).toContain('At risk')
  })
})

describe('interactive controls and product states', () => {
  it('uses accessible server ranking values', () => {
    const onChange = vi.fn()
    render(<RankingControl value="cheapest" onChange={onChange} />)
    expect(screen.getByRole('button', { name: 'Lowest cost' }).getAttribute('aria-pressed')).toBe('true')
    fireEvent.click(screen.getByRole('button', { name: 'Earliest arrival' }))
    expect(onChange).toHaveBeenCalledWith('fastest')
  })

  it('renders distinct stale and no-plan states', () => {
    const { rerender } = render(<StatePanel status="stale" />)
    expect(screen.getByRole('heading', { name: 'Your journey has changed' })).toBeTruthy()
    rerender(<StatePanel status="no_feasible_catalog_plan" />)
    expect(screen.getByRole('heading', { name: 'No option fits all your current requirements' })).toBeTruthy()
  })

  it.each([
    ['needs_input', 'We need one more detail'], ['partial_search', 'Only some options were checked'],
    ['offline_map', 'Map unavailable — your journey is still available'], ['system_error', 'We couldn’t update your journey'],
  ] as const)('renders the distinct %s product state', (status, heading) => {
    render(<StatePanel status={status} />)
    expect(screen.getByRole('heading', { name: heading })).toBeTruthy()
  })

  it('keeps adoption disabled until simulation acknowledgement', () => {
    const onCheck = vi.fn()
    const { rerender } = render(<AdoptionSheet plan={makePlan()} checked={false} busy={false} onCheck={onCheck} onClose={() => {}} onAdopt={() => {}} />)
    expect((screen.getByRole('button', { name: 'Use simulated plan' }) as HTMLButtonElement).disabled).toBe(true)
    fireEvent.click(screen.getByRole('checkbox'))
    expect(onCheck).toHaveBeenCalledWith(true)
    rerender(<AdoptionSheet plan={makePlan()} checked busy={false} onCheck={onCheck} onClose={() => {}} onAdopt={() => {}} />)
    expect((screen.getByRole('button', { name: 'Use simulated plan' }) as HTMLButtonElement).disabled).toBe(false)
  })

  it('shows a complete map-independent route fallback', () => {
    render(<JourneyMap snapshot={makeSnapshot()} selectedId={null} onSelect={() => {}} forceFallback />)
    expect(screen.getByText('Map unavailable — your journey is still available')).toBeTruthy()
    expect(screen.getByRole('button', { name: /Train T1/ })).toBeTruthy()
  })
})

describe('journey edit draft', () => {
  it('keeps the edited draft and displays actionable validation failure', async () => {
    const onSave = vi.fn().mockRejectedValue(new Error('This order cannot work because the journey is disconnected.'))
    render(<JourneyEditor snapshot={makeSnapshot()} busy={false} onClose={() => {}} onSave={onSave} />)
    fireEvent.click(screen.getAllByRole('button', { name: 'Remove' })[1])
    fireEvent.click(screen.getByRole('checkbox'))
    fireEvent.click(screen.getByRole('button', { name: 'Save and recalculate' }))
    await waitFor(() => expect(screen.getByRole('alert').textContent).toContain('This order cannot work'))
    expect(screen.getByText('Your draft is still here.')).toBeTruthy()
    expect(screen.getAllByRole('button', { name: 'Remove' })).toHaveLength(1)
  })
})
