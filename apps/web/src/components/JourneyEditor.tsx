import { useMemo, useState } from 'react'
import type { components } from '../api/schema'
import type { ItineraryEditCommand } from '../api/client'
import { friendlyActivity } from './JourneyMap'
import { useDialogFocus } from '../ui/dialog'

type Snapshot = components['schemas']['TripViewSnapshot']

export function JourneyEditor({ snapshot, busy, onClose, onSave }: {
  snapshot: Snapshot; busy: boolean; onClose: () => void; onSave: (command: ItineraryEditCommand) => Promise<void>
}) {
  const dialogRef = useDialogFocus(onClose)
  const [activities, setActivities] = useState(() => [...snapshot.trip.active_itinerary.activities])
  const [acknowledge, setAcknowledge] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const completed = new Set(snapshot.trip.current_state.completed_activity_ids)
  const activeService = snapshot.trip.current_state.active_service_id
  const removedHard = useMemo(() => snapshot.trip.active_itinerary.activities.some(item => item.hard && !activities.some(next => next.id === item.id)), [activities, snapshot])
  const move = (index: number, delta: number) => setActivities(current => {
    const next = [...current]; const target = index + delta
    if (target < 0 || target >= next.length) return current
    ;[next[index], next[target]] = [next[target], next[index]]
    return next
  })
  const remove = (id: string) => setActivities(current => current.filter(item => item.id !== id))
  const submit = async () => {
    setError(null)
    const ids = new Set(activities.map(item => item.id))
    const constraints = { ...snapshot.trip.constraints,
      required_commitment_ids: snapshot.trip.constraints.required_commitment_ids.filter(id => ids.has(id)) }
    const command: ItineraryEditCommand = {
      expected_trip_version: snapshot.trip.version,
      active_itinerary: { activities, dependencies: snapshot.trip.active_itinerary.dependencies.filter(edge => ids.has(edge.from_id) && ids.has(edge.to_id)) },
      constraints, acknowledge_hard_changes: acknowledge,
      provenance: { id: `prov:user:journey-edit-${snapshot.trip.version + 1}`, kind: 'user_reported', verification: 'unverified',
        observed_at: snapshot.trip.current_state.as_of, retrieved_at: snapshot.trip.current_state.as_of,
        valid_until: null, source_ref: 'user-action:journey-edit' },
    }
    try { await onSave(command) } catch (reason) { setError(reason instanceof Error ? reason.message : 'This edit could not be saved.') }
  }
  return <div className="sheet-backdrop"><section ref={dialogRef} className="sheet edit-sheet" role="dialog" aria-modal="true" aria-labelledby="edit-title">
    <header><div><span className="eyebrow">Remaining journey</span><h2 id="edit-title">Edit journey</h2></div><button data-dialog-initial-focus className="icon-button" aria-label="Close journey editor" onClick={onClose}>×</button></header>
    <p>Fixed service times stay locked. Move or remove future steps, then save the complete journey.</p>
    {error && <div className="inline-error" role="alert">{error}<br /><strong>Your draft is still here.</strong></div>}
    <ol className="edit-list">{activities.map((activity, index) => {
      const historyLocked = completed.has(activity.id) || Boolean(activeService && activity.service_id === activeService)
      const locked = historyLocked || activity.kind === 'fixed_transport'
      const evaluated = snapshot.evaluated_itinerary.find(item => item.activity_id === activity.id)
      return <li key={activity.id}><div><strong>{evaluated ? friendlyActivity(evaluated, snapshot) : 'Journey step'}</strong>
        <span>{historyLocked ? '🔒 Locked · already completed or current' : activity.kind === 'fixed_transport' ? '🔒 Fixed service · use recovery options' : activity.hard ? 'Required plan' : 'Optional'}</span></div>
        <div className="edit-actions"><button disabled={locked || index === 0} aria-label={`Move ${index + 1} up`} onClick={() => move(index, -1)}>↑</button>
          <button disabled={locked || index === activities.length - 1} aria-label={`Move ${index + 1} down`} onClick={() => move(index, 1)}>↓</button>
          <button disabled={locked} onClick={() => remove(activity.id)}>Remove</button></div></li>
    })}</ol>
    {removedHard && <><p className="inline-error" role="status">Acknowledgement is required before removing a required plan.</p><label className="acknowledgement"><input type="checkbox" checked={acknowledge} onChange={event => setAcknowledge(event.target.checked)} /> I understand this changes my required plans</label></>}
    <footer><button className="secondary" onClick={onClose}>Cancel</button><button onClick={submit} disabled={busy || (removedHard && !acknowledge)}>{busy ? 'Saving…' : 'Save and recalculate'}</button></footer>
  </section></div>
}
