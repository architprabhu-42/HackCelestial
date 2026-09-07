import type { components } from '../api/schema'
import corridor from '../assets/mumbai-goa-corridor.geojson.json'

type Snapshot = components['schemas']['TripViewSnapshot']
type Plan = components['schemas']['PlanEvaluation']

const project = ([lon, lat]: number[]) => ({ x: 55 + (lon - 72.7) * 225, y: 330 - (lat - 15.1) * 68 })

export function JourneyMap({ snapshot, selectedId, onSelect, preview, forceFallback = false }: {
  snapshot: Snapshot; selectedId: string | null; onSelect: (id: string) => void; preview?: Plan | null; forceFallback?: boolean
}) {
  if (forceFallback) return <section className="map-fallback" aria-label="Route list map fallback">
    <strong>Map unavailable — your journey is still available</strong>
    <ol>{snapshot.evaluated_itinerary.map(item => <li key={item.activity_id}><button onClick={() => onSelect(item.activity_id)}>{friendlyActivity(item, snapshot)}</button></li>)}</ol>
  </section>
  const previewModes = new Set(preview ? [
    ...preview.service_ids.map(id => snapshot.catalog.services.find(service => service.id === id)?.mode),
    ...(preview.transfer_template_ids.length ? ['road'] : []),
  ] : [])
  const features = corridor.features.filter(feature => !preview || previewModes.has(feature.properties.mode))
  const visibleActivities = preview?.activity_sequence ?? snapshot.evaluated_itinerary
  return <section className="journey-map" aria-label={preview ? 'Plan route preview map' : 'Journey corridor map'}>
    <div className="map-badge">{preview ? 'Preview · Not live' : 'Route preview · Not live'}</div>
    <svg viewBox="0 0 360 360" aria-label="Local map of the Mumbai to Goa journey corridor">
      <path className="coast" d="M45 18 C105 78 85 145 155 207 C190 240 210 292 273 346" />
      {features.map((feature, index) => {
        const points = feature.geometry.coordinates.map(project).map(point => `${point.x},${point.y}`).join(' ')
        return <polyline key={index} points={points} className={`route-line ${feature.properties.mode} ${preview ? 'preview' : ''}`} />
      })}
      {snapshot.catalog.locations.map(location => {
        const point = project([location.longitude, location.latitude])
        const activity = visibleActivities.find(item => item.origin_id === location.id || item.destination_id === location.id)
        return <g key={location.id} className={activity?.activity_id === selectedId ? 'marker selected' : 'marker'}
          role="button" tabIndex={0} aria-label={`Select ${location.name}`}
          onClick={() => activity && onSelect(activity.activity_id)}
          onKeyDown={event => { if (activity && (event.key === 'Enter' || event.key === ' ')) onSelect(activity.activity_id) }}>
          <circle cx={point.x} cy={point.y} r="7" /><text x={point.x + 10} y={point.y + 4}>{location.name}</text>
        </g>
      })}
    </svg>
  </section>
}

export function friendlyActivity(item: components['schemas']['EvaluatedActivity'], snapshot: Snapshot) {
  const service = snapshot.catalog.services.find(value => value.id === item.service_id)
  if (service) {
    const destination = snapshot.catalog.locations.find(value => value.id === service.destination_id)?.name
    return `${service.mode === 'air' ? 'Flight' : service.mode === 'rail' ? 'Train' : 'Service'} ${service.display_code} to ${destination ?? 'next stop'}`
  }
  const destination = snapshot.catalog.locations.find(value => value.id === item.destination_id)?.name
  if (item.kind === 'flexible_transfer') return `Cab to ${destination ?? 'next stop'}`
  if (item.kind === 'hotel_checkin') return 'Hotel check-in'
  if (item.kind === 'commitment') return 'Wedding'
  return 'Arrival and exit time'
}
