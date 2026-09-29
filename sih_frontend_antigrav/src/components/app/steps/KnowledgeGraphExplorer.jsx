// winning_features.md item 10 — "include a visual graph explorer" for
// POST /api/knowledge-graph's {nodes, edges} (engines/knowledge_graph.py).
// The backend returns no layout/coordinates (by design — see that
// endpoint's docstring), so this computes a simple deterministic layered
// layout client-side: one column per node `kind`, in a fixed left-to-right
// order matching the plan's own worked example (Product -> Ingredient ->
// Biological Resource -> TK/Classification/ABS -> IP Type/Authority ->
// Jurisdiction). No charting library — plain inline SVG, consistent with
// this app's existing bundle-size discipline.

const COLUMN_ORDER = [
  'Product',
  'Ingredient',
  'BiologicalResource',
  'Classification',
  'TKFinding',
  'ABSObligation',
  'LicensingRoute',
  'ComplianceStep',
  'IPType',
  'Authority',
  'Jurisdiction',
];

const NODE_WIDTH = 168;
const NODE_HEIGHT = 40;
const COLUMN_GAP = 60;
const ROW_GAP = 14;
const PADDING = 20;

const KIND_COLOR = {
  Product: 'var(--text-gold)',
  Jurisdiction: 'var(--text-gold)',
  TKFinding: 'var(--risk-medium)',
  ABSObligation: 'var(--risk-medium)',
  IPType: 'var(--risk-low)',
};

function layout(nodes, edges) {
  const kinds = [...new Set(nodes.map((n) => n.kind))];
  // Known kinds in COLUMN_ORDER first (in that order), then any unknown
  // kind appended before Jurisdiction so nothing silently vanishes if
  // the backend ever adds a new node kind.
  const known = COLUMN_ORDER.filter((k) => kinds.includes(k));
  const unknown = kinds.filter((k) => !COLUMN_ORDER.includes(k));
  const jurisdictionIndex = known.indexOf('Jurisdiction');
  const columns = jurisdictionIndex === -1
    ? [...known, ...unknown]
    : [...known.slice(0, jurisdictionIndex), ...unknown, ...known.slice(jurisdictionIndex)];

  const columnIndex = new Map(columns.map((k, i) => [k, i]));
  const columnCounts = new Map();
  const positioned = new Map();

  for (const node of nodes) {
    const col = columnIndex.get(node.kind) ?? columns.length;
    const row = columnCounts.get(col) || 0;
    columnCounts.set(col, row + 1);
    positioned.set(node.id, {
      ...node,
      x: PADDING + col * (NODE_WIDTH + COLUMN_GAP),
      y: PADDING + row * (NODE_HEIGHT + ROW_GAP),
    });
  }

  const maxRows = Math.max(1, ...[...columnCounts.values()]);
  const width = PADDING * 2 + columns.length * NODE_WIDTH + (columns.length - 1) * COLUMN_GAP;
  const height = PADDING * 2 + maxRows * NODE_HEIGHT + (maxRows - 1) * ROW_GAP;

  const positionedEdges = edges
    .map((e) => ({ ...e, source: positioned.get(e.source), target: positioned.get(e.target) }))
    .filter((e) => e.source && e.target);

  return { positionedNodes: [...positioned.values()], positionedEdges, width, height };
}

export default function KnowledgeGraphExplorer({ graph }) {
  if (!graph || !graph.nodes?.length) return null;

  const { positionedNodes, positionedEdges, width, height } = layout(graph.nodes, graph.edges || []);

  return (
    <div className="kg-explorer">
      <svg width={width} height={height} viewBox={`0 0 ${width} ${height}`} role="img" aria-label="Knowledge graph">
        <defs>
          <marker id="kg-arrow" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <path d="M0,0 L8,4 L0,8 Z" fill="var(--app-text-muted)" />
          </marker>
        </defs>

        {positionedEdges.map((e, i) => {
          const x1 = e.source.x + NODE_WIDTH;
          const y1 = e.source.y + NODE_HEIGHT / 2;
          const x2 = e.target.x;
          const y2 = e.target.y + NODE_HEIGHT / 2;
          const midX = (x1 + x2) / 2;
          return (
            <path
              key={i}
              d={`M ${x1} ${y1} C ${midX} ${y1}, ${midX} ${y2}, ${x2} ${y2}`}
              fill="none"
              stroke="var(--app-border)"
              strokeWidth="1.5"
              markerEnd="url(#kg-arrow)"
            />
          );
        })}

        {positionedNodes.map((n) => (
          <g key={n.id} transform={`translate(${n.x}, ${n.y})`}>
            <rect
              width={NODE_WIDTH}
              height={NODE_HEIGHT}
              rx="8"
              fill="var(--app-bg-elevated)"
              stroke={KIND_COLOR[n.kind] || 'var(--app-border)'}
              strokeWidth="1.3"
            />
            <title>{`${n.kind}: ${n.label}`}</title>
            <foreignObject width={NODE_WIDTH} height={NODE_HEIGHT}>
              <div className="kg-explorer__node-label">{n.label}</div>
            </foreignObject>
          </g>
        ))}
      </svg>
    </div>
  );
}
