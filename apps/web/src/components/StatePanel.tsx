import type { components } from '../api/schema'

type Status = components['schemas']['PlannerResultStatus'] | 'stale' | 'offline_map' | 'system_error'

const states: Record<Status, { title: string; body: string; action: string }> = {
  complete: { title: 'Choose a new way forward', body: 'These options meet your current journey requirements.', action: 'Preview a plan' },
  no_feasible_catalog_plan: { title: 'No option fits all your current requirements', body: 'Try editing your budget or remaining journey.', action: 'Edit journey' },
  needs_input: { title: 'We need one more detail', body: 'Add the missing information before choosing an option.', action: 'Review details' },
  partial_search: { title: 'Only some options were checked', body: 'No global cheapest or fastest claim is available yet.', action: 'Retry options' },
  error: { title: 'We couldn’t check recovery options', body: 'Your last good journey is still shown.', action: 'Try again' },
  stale: { title: 'Your journey has changed', body: 'These options are based on an older journey.', action: 'Refresh options' },
  offline_map: { title: 'Map unavailable — your journey is still available', body: 'Use the complete route list below.', action: 'View route list' },
  system_error: { title: 'We couldn’t update your journey', body: 'Your last good journey has been preserved.', action: 'Try again' },
}

export function StatePanel({ status, onAction }: { status: Status; onAction?: () => void }) {
  const state = states[status]
  return <section className={`state-panel state-${status}`} aria-live="polite">
    <span className="status-symbol" aria-hidden="true">{status === 'complete' ? '✓' : '!'}</span>
    <div><h2>{state.title}</h2><p>{state.body}</p></div>
    {onAction && <button className="secondary" onClick={onAction}>{state.action}</button>}
  </section>
}
