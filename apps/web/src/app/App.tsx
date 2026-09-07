import { useState } from 'react'
import type { components } from '../api/schema'
import { api, ApiProblem, type AdoptionResponse, type ItineraryEditCommand, type RankingPreset } from '../api/client'
import { acceptPlannerResponse, replaceSnapshot } from '../state/coherence'
import { consumerCopy } from '../ui/copy'
import { formatINR, formatIST, formatKind, formatMargin } from '../ui/format'
import { JourneyEditor } from '../components/JourneyEditor'
import { JourneyMap, friendlyActivity } from '../components/JourneyMap'
import { RankingControl } from '../components/RankingControl'
import { StatePanel } from '../components/StatePanel'
import { useDialogFocus } from '../ui/dialog'

type Snapshot = components['schemas']['TripViewSnapshot']
type PlannerResult = components['schemas']['PlannerResult']
type Plan = components['schemas']['PlanEvaluation']

const errorMessage = (reason: unknown) => reason instanceof ApiProblem
  ? consumerCopy(reason.problem.error.code, reason.problem.error.message)
  : 'We couldn’t update your journey. Your last good view is still here.'

export function App() {
  const [snapshot, setSnapshot] = useState<Snapshot | null>(null)
  const [planner, setPlanner] = useState<PlannerResult | null>(null)
  const [selectedActivity, setSelectedActivity] = useState<string | null>(null)
  const [selectedPlan, setSelectedPlan] = useState<Plan | null>(null)
  const [ranking, setRanking] = useState<RankingPreset>('cheapest')
  const [sheet, setSheet] = useState<'report' | 'adopt' | 'edit' | null>(null)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [plansStale, setPlansStale] = useState(false)
  const [mapFallback, setMapFallback] = useState(() => new URLSearchParams(window.location.search).get('map') === 'fallback')
  const [acknowledged, setAcknowledged] = useState(false)
  const [adoption, setAdoption] = useState<AdoptionResponse | null>(null)
  const [announcement, setAnnouncement] = useState('')

  const selected = snapshot?.evaluated_itinerary.find(item => item.activity_id === selectedActivity) ?? null
  const locationName = snapshot?.catalog.locations.find(item => item.id === snapshot.trip.current_state.location_id)?.name ?? 'Current journey location'
  const nextTransport = snapshot?.evaluated_itinerary.find(item => item.kind === 'fixed_transport' && !snapshot.trip.current_state.completed_activity_ids.includes(item.activity_id))

  async function run(action: () => Promise<void>) {
    try { setBusy(true); setError(null); await action() } catch (reason) { setError(errorMessage(reason)) } finally { setBusy(false) }
  }
  const loadDemo = async () => run(async () => {
    const response = await api.createDemo()
    let loaded = response.snapshot
    const mode = new URLSearchParams(window.location.search).get('testMode')
    // The browser suite changes real server state through the public mutation
    // commands; normal product sessions never enter these isolated test modes.
    if (mode === 'budget-5000') {
      const provenance = { id: 'prov:test:budget-5000', kind: 'user_reported' as const, verification: 'unverified' as const,
        observed_at: loaded.trip.current_state.as_of, retrieved_at: loaded.trip.current_state.as_of, valid_until: null, source_ref: 'browser-test:budget-5000' }
      const result = await api.replaceConstraints(loaded.trip.id, { expected_trip_version: loaded.trip.version,
        constraints: { ...loaded.trip.constraints, max_cash_required_paise: 500000 }, provenance })
      loaded = result.snapshot
    }
    if (mode === 'needs-input') {
      const provenance = { id: 'prov:test:unsupported-onboard', kind: 'user_reported' as const, verification: 'unverified' as const,
        observed_at: loaded.trip.current_state.as_of, retrieved_at: loaded.trip.current_state.as_of, valid_until: null, source_ref: 'browser-test:unsupported-onboard' }
      const result = await api.replaceCurrentState(loaded.trip.id, { expected_trip_version: loaded.trip.version,
        current_state: { as_of: loaded.trip.current_state.as_of, location_id: null, phase: 'onboard', active_service_id: 'svc:T1:2026-09-26', completed_activity_ids: [], next_recovery_point_id: null, provenance_id: provenance.id }, provenance })
      loaded = result.snapshot
    }
    setSnapshot(loaded); setSelectedActivity(loaded.evaluated_itinerary[0]?.activity_id ?? null)
    setPlanner(null); setAdoption(null); setPlansStale(false); setAnnouncement('Mumbai to Goa demo loaded')
  })
  const reportD1 = async () => snapshot && run(async () => {
    const response = await api.applyD1(snapshot.trip.id, snapshot.trip.version)
    setSnapshot(response.event_result.snapshot); setPlanner(null); setSelectedPlan(null); setPlansStale(false); setSheet(null)
    setAnnouncement('Delay applied. Your connected journey has been updated.')
  })
  const generate = async (preset: RankingPreset = ranking) => snapshot && run(async () => {
    const response = await api.generatePlans(snapshot.trip.id, snapshot.trip.version, snapshot.trip.catalog_version, preset)
    const accepted = acceptPlannerResponse(snapshot, response)
    if (!accepted) { setPlansStale(true); setAnnouncement('Your journey changed. Refresh options.'); return }
    setRanking(preset); setPlanner(accepted); setPlansStale(false); setSelectedPlan(null); setAnnouncement('Recovery options are ready.')
  })
  const adopt = async () => snapshot && selectedPlan && acknowledged && run(async () => {
    const response = await api.adoptPlan(snapshot.trip.id, snapshot.trip.version, selectedPlan.id)
    setSnapshot(response.snapshot); setAdoption(response); setPlanner(null); setSelectedPlan(null); setSheet(null); setAcknowledged(false)
    setAnnouncement('New proposed journey saved. No external booking occurred.')
  })
  const saveEdit = async (command: ItineraryEditCommand) => {
    if (!snapshot) return
    try {
      setBusy(true); setError(null)
      const response = await api.editItinerary(snapshot.trip.id, command)
      const next = replaceSnapshot(snapshot, response.snapshot)
      if (!next) throw new Error('This update belongs to a different journey.')
      setSnapshot(next); setPlansStale(Boolean(planner) && response.changed); setSelectedPlan(null); setSheet(null)
      setAnnouncement(response.changed ? 'Journey updated — find new options' : 'Your journey was already up to date.')
    } catch (reason) { throw new Error(errorMessage(reason)) } finally { setBusy(false) }
  }
  const reset = async () => snapshot && run(async () => {
    const response = await api.reset(snapshot.trip.id, snapshot.trip.version)
    setSnapshot(response.snapshot); setPlanner(null); setSelectedPlan(null); setAdoption(null); setPlansStale(false); setSheet(null)
    setAnnouncement('Scenario reset to the original journey.')
  })

  return <div className="app-shell">
    <header className="app-header"><a className="brand" href="#main" aria-label="ResiliTrip home"><span>R</span> ResiliTrip</a>
      {snapshot && <nav aria-label="Journey actions"><button className="quiet" onClick={() => setSheet('edit')} disabled={!snapshot.available_actions.can_edit_itinerary}>Edit journey</button><button className="quiet" onClick={reset}>Reset scenario</button></nav>}
    </header>
    <div className="truth-strip" role="note"><span aria-hidden="true">◇</span> Synthetic travel scenario · Options are not live or bookable</div>
    <div className="sr-only" role="status" aria-live="polite">{announcement}</div>
    {!snapshot ? <Landing busy={busy} error={error} onStart={loadDemo} /> : <main id="main" className="workspace">
      {error && <StatePanel status="system_error" onAction={() => setError(null)} />}
      {plansStale && <StatePanel status="stale" onAction={() => generate()} />}
      {adoption && <AdoptionSuccess response={adoption} />}
      <section className="workspace-heading"><div><span className="eyebrow">Mumbai → Goa · Saturday, 26 September</span><h1>{adoption ? 'Your proposed journey' : snapshot.overall_status === 'infeasible' ? 'Your arrival plan has changed' : 'Your journey is on track'}</h1>
        <p>One connected view of transport, hotel and your wedding arrival.</p></div><span className={`status-pill ${snapshot.overall_status}`}>{snapshot.overall_status === 'infeasible' ? '⚠ Needs attention' : '✓ Connected journey'}</span></section>
      <div className="workspace-grid">
        <div className="map-column"><JourneyMap snapshot={snapshot} selectedId={selectedActivity} onSelect={setSelectedActivity} preview={selectedPlan} forceFallback={mapFallback} />
          <button className="map-switch" onClick={() => setMapFallback(value => !value)}>{mapFallback ? 'Show corridor map' : 'Use map-free route list'}</button>
          <CurrentStatus location={locationName} snapshot={snapshot} next={nextTransport ? friendlyActivity(nextTransport, snapshot) : 'Journey complete'} onReport={() => { if (nextTransport) setSelectedActivity(nextTransport.activity_id); setSheet('report') }} busy={busy} />
        </div>
        <div className="journey-column"><JourneyTimeline snapshot={snapshot} items={selectedPlan?.activity_sequence ?? snapshot.evaluated_itinerary} selected={selectedActivity} onSelect={setSelectedActivity} preview={Boolean(selectedPlan)} />
          {selected && <ActivityDetail snapshot={snapshot} activity={selected} />}</div>
      </div>
      {snapshot.impacts.length > 0 && <ImpactSummary snapshot={snapshot} onRecover={() => generate()} busy={busy} />}
      {(planner || busy) && <RecoverySection snapshot={snapshot} planner={planner} stale={plansStale} busy={busy} ranking={ranking} onRanking={generate} onPreview={plan => { setSelectedPlan(plan); setSelectedActivity(plan.activity_sequence[0]?.activity_id ?? null) }} />}
      {selectedPlan && !plansStale && <PlanPreview plan={selectedPlan} snapshot={snapshot} onUse={() => setSheet('adopt')} onCompare={() => setSelectedPlan(null)} onEdit={() => setSheet('edit')} />}
      {sheet === 'report' && <ReportSheet selected={selected} snapshot={snapshot} busy={busy} onClose={() => setSheet(null)} onApply={reportD1} />}
      {sheet === 'adopt' && selectedPlan && <AdoptionSheet plan={selectedPlan} checked={acknowledged} busy={busy} onCheck={setAcknowledged} onClose={() => setSheet(null)} onAdopt={adopt} />}
      {sheet === 'edit' && <JourneyEditor snapshot={snapshot} busy={busy} onClose={() => setSheet(null)} onSave={saveEdit} />}
    </main>}
  </div>
}

function Landing({ busy, error, onStart }: { busy: boolean; error: string | null; onStart: () => void }) {
  return <main id="main" className="landing"><section className="hero"><span className="eyebrow">Travel disruption, made understandable</span><h1>Plan for the whole journey</h1><p>See how one delay affects your transfers, hotel and the moment you need to arrive—then compare practical ways forward.</p>
    <button className="primary large" onClick={onStart} disabled={busy}>{busy ? 'Preparing your journey…' : 'Try Mumbai to Goa demo'} <span aria-hidden="true">→</span></button><small>No sign-up. Runs with a local, fictional scenario.</small></section>
    <section className="landing-route" aria-label="Demo journey overview"><div className="route-illustration"><span className="city">Mumbai</span><span className="route-dots">● · · ✈ · · ●</span><span className="city">Goa</span></div><h2>A connected trip, not just a ticket</h2><p>Train, transfers, hotel and wedding—all checked together.</p></section>
    {error && <StatePanel status="system_error" onAction={onStart} />}</main>
}

function CurrentStatus({ location, snapshot, next, onReport, busy }: { location: string; snapshot: Snapshot; next: string; onReport: () => void; busy: boolean }) {
  return <section className="current-card"><div className="current-icon" aria-hidden="true">⌖</div><div><span className="eyebrow">You are here</span><h2>{location}</h2><p>{formatIST(snapshot.trip.current_state.as_of)} · Next: {next}</p></div><button onClick={onReport} disabled={busy || !snapshot.available_actions.can_apply_event}>Report a problem</button></section>
}

function JourneyTimeline({ snapshot, items, selected, onSelect, preview }: { snapshot: Snapshot; items: components['schemas']['EvaluatedActivity'][]; selected: string | null; onSelect: (id: string) => void; preview: boolean }) {
  return <section className="timeline-panel"><header><div><span className="eyebrow">{preview ? 'Plan preview' : 'Your complete route'}</span><h2>{preview ? 'Proposed journey' : 'Journey timeline'}</h2></div>{preview && <span className="preview-chip">Preview</span>}</header><ol className="timeline">{items.map((item, index) => <li key={item.activity_id}><button className={selected === item.activity_id ? 'activity selected' : 'activity'} onClick={() => onSelect(item.activity_id)} aria-pressed={selected === item.activity_id}>
    <span className={`mode-dot ${item.kind}`} aria-hidden="true">{index + 1}</span><span className="activity-copy"><strong>{friendlyActivity(item, snapshot)}</strong><span>{formatIST(item.start_at)}{item.end_at ? ` – ${formatIST(item.end_at)}` : ''}</span></span><span className={`mini-status ${item.status}`}>{item.status === 'infeasible' ? '⚠ Late' : item.status === 'blocked' ? '■ Blocked' : '✓ Checked'}</span></button></li>)}</ol></section>
}

function ActivityDetail({ snapshot, activity }: { snapshot: Snapshot; activity: components['schemas']['EvaluatedActivity'] }) {
  const origin = snapshot.catalog.locations.find(item => item.id === activity.origin_id)?.name
  const destination = snapshot.catalog.locations.find(item => item.id === activity.destination_id)?.name
  return <aside className="detail-card"><span className="eyebrow">Selected step</span><h3>{friendlyActivity(activity, snapshot)}</h3><p>{origin && destination ? `${origin} → ${destination}` : formatKind(activity.kind)}</p><dl><div><dt>Starts</dt><dd>{formatIST(activity.start_at)}</dd></div><div><dt>Ready</dt><dd>{formatIST(activity.ready_at)}</dd></div><div><dt>Status</dt><dd>{activity.status === 'infeasible' ? 'Does not meet the plan' : 'Fits the current plan'}</dd></div></dl></aside>
}

function ImpactSummary({ snapshot, onRecover, busy }: { snapshot: Snapshot; onRecover: () => void; busy: boolean }) {
  const commitment = snapshot.evaluated_itinerary.find(item => item.kind === 'commitment')
  const hotel = snapshot.evaluated_itinerary.find(item => item.kind === 'hotel_checkin')
  const impact = snapshot.impacts.find(item => item.activity_id === commitment?.activity_id)
  return <section className="impact-card"><div className="impact-mark" aria-hidden="true">!</div><div><span className="eyebrow">Connected impact</span><h2>You would reach the wedding at {formatIST(impact?.after_ready_at ?? commitment?.ready_at ?? null)}</h2><p className="danger-copy">{formatMargin(impact?.after_slack_sec ?? commitment?.slack_sec ?? 0)} for your required arrival.</p>
    <div className="impact-facts"><span>⚠ Wedding arrival no longer works</span><span>✓ Hotel check-in is still {hotel?.status === 'infeasible' ? 'affected' : 'valid'}</span></div><details><summary>Why did this change?</summary><p>The reported train delay moves each connected transfer and arrival later. The hotel window remains available, but the wedding cutoff does not.</p></details></div><button className="primary" onClick={onRecover} disabled={busy}>{busy ? 'Checking routes…' : 'Find another way'}</button></section>
}

function RecoverySection({ snapshot, planner, stale, busy, ranking, onRanking, onPreview }: { snapshot: Snapshot; planner: PlannerResult | null; stale: boolean; busy: boolean; ranking: RankingPreset; onRanking: (value: RankingPreset) => void; onPreview: (plan: Plan) => void }) {
  if (busy && !planner) return <section className="recovery"><div className="skeleton" /><div className="skeleton" /></section>
  if (!planner) return null
  if (planner.result_status !== 'complete') return <StatePanel status={planner.result_status} onAction={() => onRanking(ranking)} />
  if (stale) return null
  return <section className="recovery"><header><div><span className="eyebrow">Recovery options</span><h2>Choose a new way forward</h2><p>Compared against your complete journey and arrival requirement.</p></div><RankingControl value={ranking} onChange={onRanking} disabled={busy} /></header>
    <div className="plan-grid">{planner.feasible_plans.map((plan, index) => <PlanCard key={plan.id} plan={plan} snapshot={snapshot} rank={index + 1} onPreview={() => onPreview(plan)} />)}</div>
    <details className="rejected"><summary>Options that don’t meet your plans ({planner.rejected_plans.length})</summary>{planner.rejected_plans.map(plan => <article key={plan.id}><strong>{planTitle(plan, snapshot)}</strong><p>You would reach the wedding at {formatIST(plan.final_required_arrival_at)} — {formatMargin(plan.event_slack_sec)}.</p><span className="status-pill infeasible">Not available to use</span></article>)}</details></section>
}

function planTitle(plan: Plan, snapshot: Snapshot) {
  const services = plan.service_ids.map(id => snapshot.catalog.services.find(service => service.id === id)).filter(Boolean)
  const flight = services.find(service => service?.mode === 'air')
  return flight ? `Fly ${flight.display_code} to Goa` : 'Wait for the delayed train'
}

function PlanCard({ plan, snapshot, rank, onPreview }: { plan: Plan; snapshot: Snapshot; rank: number; onPreview: () => void }) {
  return <article className="plan-card"><div className="plan-rank">{rank === 1 ? 'Recommended' : `Option ${rank}`}</div><h3>{planTitle(plan, snapshot)}</h3><p className="route-summary">Mumbai → Goa → Hotel → Wedding</p><dl className="plan-metrics"><div><dt>Cash still required</dt><dd>{formatINR(plan.cash_required_paise)}</dd></div><div><dt>Wedding arrival</dt><dd>{formatIST(plan.final_required_arrival_at)}</dd></div><div><dt>Arrival margin</dt><dd>{formatMargin(plan.event_slack_sec)}</dd></div><div><dt>Bookings changed</dt><dd>{plan.objective_values.changed_original_booking_count}</dd></div></dl>
    <p className="incremental">{formatINR(plan.incremental_cost_paise)} above your original remaining spend</p><p className="refund">Train refund: {formatINR(plan.potential_refund_paise)} · Check with provider</p><span className="synthetic-chip">◇ Simulated option</span><button className="secondary full" onClick={onPreview}>Preview this plan</button></article>
}

function PlanPreview({ plan, snapshot, onUse, onCompare, onEdit }: { plan: Plan; snapshot: Snapshot; onUse: () => void; onCompare: () => void; onEdit: () => void }) {
  return <section className="preview-panel"><div><span className="preview-chip">Preview</span><h2>{planTitle(plan, snapshot)}</h2><p>Choose before {formatIST(plan.valid_until)} or refresh options.</p></div><div className="preview-actions"><button className="quiet" onClick={onCompare}>Compare again</button><button className="quiet" onClick={onEdit}>Edit remaining journey</button><button onClick={onUse}>Use this plan</button></div></section>
}

function ReportSheet({ selected, snapshot, busy, onClose, onApply }: { selected: components['schemas']['EvaluatedActivity'] | null; snapshot: Snapshot; busy: boolean; onClose: () => void; onApply: () => void }) {
  const dialogRef = useDialogFocus(onClose)
  return <div className="sheet-backdrop"><section ref={dialogRef} className="sheet" role="dialog" aria-modal="true" aria-labelledby="report-title"><header><div><span className="eyebrow">Report a problem</span><h2 id="report-title">What changed?</h2></div><button data-dialog-initial-focus className="icon-button" onClick={onClose} aria-label="Close report problem sheet">×</button></header><div className="selected-service"><strong>{selected ? friendlyActivity(selected, snapshot) : 'Your next train'}</strong><span>Selected journey step</span></div>
    <fieldset className="problem-options"><legend>Choose the issue</legend><label className="selected"><input type="radio" checked readOnly /> It is delayed</label><label><input type="radio" disabled /> It was cancelled</label><label><input type="radio" disabled /> I missed it</label></fieldset><div className="demo-update"><span>Demo update</span><strong>Departure 9:00 AM · Arrival 6:30 PM</strong><p>This updates the effective train time and checks every connected step.</p></div><footer><button className="secondary" onClick={onClose}>Cancel</button><button onClick={onApply} disabled={busy}>{busy ? 'Updating…' : 'Apply delay'}</button></footer></section></div>
}

export function AdoptionSheet({ plan, checked, busy, onCheck, onClose, onAdopt }: { plan: Plan; checked: boolean; busy: boolean; onCheck: (value: boolean) => void; onClose: () => void; onAdopt: () => void }) {
  const dialogRef = useDialogFocus(onClose)
  return <div className="sheet-backdrop"><section ref={dialogRef} className="sheet" role="dialog" aria-modal="true" aria-labelledby="adopt-title"><header><div><span className="eyebrow">Simulation</span><h2 id="adopt-title">Use this as your new plan?</h2></div><button data-dialog-initial-focus className="icon-button" aria-label="Close adoption sheet" onClick={onClose}>×</button></header><p><strong>{formatINR(plan.cash_required_paise)}</strong> cash required · arrive {formatIST(plan.final_required_arrival_at)}</p>
    <label className="acknowledgement"><input type="checkbox" checked={checked} onChange={event => onCheck(event.target.checked)} /> I understand this is a simulated plan. ResiliTrip has not booked, cancelled or paid for anything.</label><footer><button className="secondary" onClick={onClose}>Back</button><button disabled={!checked || busy} onClick={onAdopt}>{busy ? 'Saving…' : 'Use simulated plan'}</button></footer></section></div>
}

function AdoptionSuccess({ response }: { response: AdoptionResponse }) {
  return <section className="adoption-success"><span className="success-icon" aria-hidden="true">✓</span><div><span className="eyebrow">Saved in ResiliTrip</span><h2>New proposed journey saved</h2><p>No external booking was changed. Complete these steps with the relevant providers before relying on this route.</p><ul>{response.provider_actions.map(action => <li key={action.id}><span>○</span><div><strong>{action.title}</strong><small>Not started · {action.reason}</small></div></li>)}</ul></div></section>
}
