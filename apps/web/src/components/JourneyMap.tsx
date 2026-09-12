import { useEffect, useRef, useState } from 'react'
import maplibregl from 'maplibre-gl'
import type { components } from '../api/schema'
import corridor from '../assets/mumbai-goa-corridor.geojson.json'

type Snapshot = components['schemas']['TripViewSnapshot']
type Plan = components['schemas']['PlanEvaluation']
type Activity = components['schemas']['EvaluatedActivity']

const MODE_COLOR: Record<string, string> = { rail: '#6d5bd0', air: '#2d6cdf', road: '#0b8f74' }
const MAP_STYLE = 'https://tiles.openfreemap.org/styles/positron'

type MapStatus = 'loading' | 'ready' | 'error'

export function JourneyMap({ snapshot, selectedId, onSelect, preview, forceFallback = false }: {
  snapshot: Snapshot; selectedId: string | null; onSelect: (id: string) => void; preview?: Plan | null; forceFallback?: boolean
}) {
  const containerRef = useRef<HTMLDivElement>(null)
  const mapRef = useRef<maplibregl.Map | null>(null)
  const markersRef = useRef<maplibregl.Marker[]>([])
  const [status, setStatus] = useState<MapStatus>('loading')

  const previewModes = new Set(preview ? [
    ...preview.service_ids.map(id => snapshot.catalog.services.find(service => service.id === id)?.mode),
    ...(preview.transfer_template_ids.length ? ['road'] : []),
  ] : [])
  const features = corridor.features.filter(feature => !preview || previewModes.has(feature.properties.mode))
  const visibleActivities = preview?.activity_sequence ?? snapshot.evaluated_itinerary

  // Tear down the live map when switching to the list fallback so a fresh
  // map (bound to a new DOM node) is created if the user switches back.
  useEffect(() => {
    if (!forceFallback) return
    markersRef.current.forEach(marker => marker.remove())
    markersRef.current = []
    mapRef.current?.remove()
    mapRef.current = null
    setStatus('loading')
  }, [forceFallback])

  useEffect(() => {
    if (forceFallback || !containerRef.current || mapRef.current) return
    const map = new maplibregl.Map({
      container: containerRef.current, style: MAP_STYLE,
      center: [73.6, 16.9], zoom: 6.2, attributionControl: { compact: true },
    })
    map.addControl(new maplibregl.NavigationControl({ showCompass: false }), 'top-right')
    const loadTimeout = window.setTimeout(() => setStatus('error'), 8000)
    map.on('load', () => { window.clearTimeout(loadTimeout); setStatus('ready') })
    map.on('error', () => { window.clearTimeout(loadTimeout); setStatus('error') })
    mapRef.current = map
    // No cleanup here: React StrictMode's dev-only mount→cleanup→mount cycle
    // destroying and immediately recreating a MapLibre map corrupts its
    // internal request cache and the style fetch hangs forever. Real teardown
    // happens in the forceFallback effect above, which only fires on an
    // actual user-triggered switch to the list view.
  }, [forceFallback])

  useEffect(() => {
    const map = mapRef.current
    if (forceFallback || status !== 'ready' || !map) return
    markersRef.current.forEach(marker => marker.remove())
    markersRef.current = []

    features.forEach((feature, index) => {
      const sourceId = `corridor-${index}`
      const color = MODE_COLOR[feature.properties.mode] ?? '#2557d6'
      const data: GeoJSON.Feature = { type: 'Feature', properties: {}, geometry: feature.geometry as GeoJSON.Geometry }
      if (map.getSource(sourceId)) (map.getSource(sourceId) as maplibregl.GeoJSONSource).setData(data)
      else map.addSource(sourceId, { type: 'geojson', data })
      const layerId = `corridor-line-${index}`
      const paint: maplibregl.LineLayerSpecification['paint'] = preview
        ? { 'line-color': color, 'line-width': 5, 'line-opacity': 0.95 }
        : { 'line-color': color, 'line-width': 3, 'line-opacity': 0.7, 'line-dasharray': [2, 1.6] }
      if (map.getLayer(layerId)) { map.removeLayer(layerId) }
      map.addLayer({ id: layerId, type: 'line', source: sourceId, layout: { 'line-cap': 'round' }, paint })
    })

    const currentLocationId = snapshot.trip.current_state.location_id
    const destinationId = (() => {
      for (let i = snapshot.evaluated_itinerary.length - 1; i >= 0; i--) {
        const item = snapshot.evaluated_itinerary[i]
        if (item.destination_id) return item.destination_id
      }
      return snapshot.evaluated_itinerary.at(-1)?.origin_id ?? null
    })()

    const bounds = new maplibregl.LngLatBounds()
    snapshot.catalog.locations.forEach(location => {
      const lngLat: [number, number] = [location.longitude, location.latitude]
      bounds.extend(lngLat)
      const activity = visibleActivities.find(item => item.origin_id === location.id || item.destination_id === location.id)
      const selected = activity?.activity_id === selectedId
      const isCurrent = location.id === currentLocationId
      const isDestination = !isCurrent && location.id === destinationId
      const el = document.createElement('div')
      const anchor: maplibregl.PositionAnchor = isDestination ? 'bottom' : isCurrent ? 'center' : 'left'
      el.setAttribute('role', 'button')
      el.setAttribute('tabindex', '0')
      el.setAttribute('aria-label', isCurrent ? `${location.name}, your current location` : isDestination ? `${location.name}, destination` : `Select ${location.name}`)
      if (isCurrent) {
        el.className = selected ? 'map-pin map-pin-current selected' : 'map-pin map-pin-current'
        el.innerHTML = '<span class="map-pin-beacon"><span class="map-pin-beacon-ping" aria-hidden="true"></span><span class="map-pin-beacon-dot" aria-hidden="true"></span></span>'
        const label = document.createElement('span'); label.className = 'map-pin-label'; label.textContent = `${location.name} · You are here`
        el.append(label)
      } else if (isDestination) {
        el.className = selected ? 'map-pin map-pin-destination selected' : 'map-pin map-pin-destination'
        const label = document.createElement('span'); label.className = 'map-pin-label'; label.textContent = location.name
        el.innerHTML = '<svg class="map-pin-icon" viewBox="0 0 24 34" width="24" height="34" aria-hidden="true"><path d="M12 0C5.4 0 0 5.4 0 12c0 9 12 22 12 22s12-13 12-22c0-6.6-5.4-12-12-12z" fill="#c0392b" stroke="#fff" stroke-width="1.5"></path><circle cx="12" cy="12" r="4.5" fill="#fff"></circle></svg>'
        el.append(label)
      } else {
        el.className = selected ? 'map-pin selected' : 'map-pin'
        const dot = document.createElement('span'); dot.className = 'map-pin-dot'
        const label = document.createElement('span'); label.className = 'map-pin-label'; label.textContent = location.name
        el.append(dot, label)
      }
      if (activity) {
        el.addEventListener('click', () => onSelect(activity.activity_id))
        el.addEventListener('keydown', event => { if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); onSelect(activity.activity_id) } })
      }
      const marker = new maplibregl.Marker({ element: el, anchor }).setLngLat(lngLat).addTo(map)
      markersRef.current.push(marker)
    })

    if (!bounds.isEmpty()) map.fitBounds(bounds, { padding: 56, duration: 0 })
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [forceFallback, status, snapshot, preview, selectedId])

  if (forceFallback) return <section className="map-fallback" aria-label="Route list map fallback">
    <strong>Map unavailable — your journey is still available</strong>
    <ol>{snapshot.evaluated_itinerary.map(item => <li key={item.activity_id}><button onClick={() => onSelect(item.activity_id)}>{friendlyActivity(item, snapshot)}</button></li>)}</ol>
  </section>

  return <section className="journey-map" aria-label={preview ? 'Plan route preview map' : 'Journey corridor map'}>
    <div className="map-badge">{preview ? 'Preview · Not live' : 'Route preview · Not live'}</div>
    <div ref={containerRef} className="map-canvas" />
    {status !== 'ready' && <MapPlaceholder status={status} snapshot={snapshot} onSelect={onSelect} activities={visibleActivities} />}
  </section>
}

function MapPlaceholder({ status, snapshot, onSelect, activities }: {
  status: MapStatus; snapshot: Snapshot; onSelect: (id: string) => void; activities: Activity[]
}) {
  const copy = status === 'error'
    ? { heading: "We couldn't load the live map", body: 'Your journey is still fully available below.' }
    : { heading: 'Loading live map…', body: 'Fetching map tiles.' }
  return <div className="map-placeholder">
    <strong>{copy.heading}</strong><p>{copy.body}</p>
    <ol>{activities.map(item => <li key={item.activity_id}><button onClick={() => onSelect(item.activity_id)}>{friendlyActivity(item, snapshot)}</button></li>)}</ol>
  </div>
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
