export function DependencyDiagram() {
  return (
    <svg
      className="dependency-diagram"
      viewBox="0 0 720 200"
      role="img"
      aria-label="Diagram: the train is delayed, the transfer is recalculated, the hotel window still holds, and the wedding arrival no longer works"
    >
      <defs>
        <marker id="dg-arrow" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="6.5" markerHeight="6.5" orient="auto-start-reverse">
          <path d="M0,0 L10,5 L0,10 z" className="dg-arrowhead" />
        </marker>
        <marker id="dg-arrow-accent" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="6.5" markerHeight="6.5" orient="auto-start-reverse">
          <path d="M0,0 L10,5 L0,10 z" className="dg-arrowhead-accent" />
        </marker>
      </defs>

      <line x1="150" y1="98" x2="196" y2="98" className="dg-edge-accent" markerEnd="url(#dg-arrow-accent)" />
      <line x1="340" y1="98" x2="386" y2="98" className="dg-edge" markerEnd="url(#dg-arrow)" />
      <line x1="530" y1="98" x2="576" y2="98" className="dg-edge" markerEnd="url(#dg-arrow)" />

      <text x="173" y="80" textAnchor="middle" className="dg-tag dg-tag-accent">+2h 30m</text>

      <g>
        <rect x="10" y="66" width="140" height="64" rx="12" className="dg-node dg-node-accent" />
        <text x="80" y="92" textAnchor="middle" className="dg-node-title">Train · T1</text>
        <text x="80" y="110" textAnchor="middle" className="dg-node-sub">Mumbai → Goa</text>
      </g>

      <g>
        <rect x="200" y="66" width="140" height="64" rx="12" className="dg-node" />
        <text x="270" y="92" textAnchor="middle" className="dg-node-title">Transfer</text>
        <text x="270" y="110" textAnchor="middle" className="dg-node-sub">Station → hotel</text>
      </g>

      <g>
        <rect x="390" y="66" width="140" height="64" rx="12" className="dg-node" />
        <text x="460" y="92" textAnchor="middle" className="dg-node-title">Hotel</text>
        <text x="460" y="110" textAnchor="middle" className="dg-node-sub">Check-in window</text>
      </g>

      <g>
        <rect x="580" y="66" width="140" height="64" rx="12" className="dg-node dg-node-accent" />
        <text x="650" y="92" textAnchor="middle" className="dg-node-title">Wedding</text>
        <text x="650" y="110" textAnchor="middle" className="dg-node-sub">Required arrival</text>
      </g>

      <text x="270" y="152" textAnchor="middle" className="dg-tag">Recalculated</text>
      <text x="460" y="152" textAnchor="middle" className="dg-tag">Still valid</text>
      <text x="650" y="152" textAnchor="middle" className="dg-tag dg-tag-accent">Arrives too late</text>
    </svg>
  )
}
