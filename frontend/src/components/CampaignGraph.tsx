import { useCallback, useRef } from 'react'
import ForceGraph2D from 'react-force-graph-2d'
import type { GraphNode, GraphLink } from '../types'

interface Props {
  nodes: GraphNode[]
  links: GraphLink[]
}

const NODE_COLORS: Record<string, string> = {
  report: '#0FA3A3',
  domain: '#F28C28',
  phone: '#D64545',
  upi: '#a855f7',
  sender: '#3b82f6',
}

const NODE_SIZES: Record<string, number> = {
  report: 6,
  domain: 10,
  phone: 10,
  upi: 10,
  sender: 8,
}

function getRiskColor(node: GraphNode): string {
  if (node.type === 'report') {
    if (node.label_risk === 'High Risk') return '#D64545'
    if (node.label_risk === 'Suspicious') return '#F28C28'
    return '#0FA3A3'
  }
  return NODE_COLORS[node.type] || '#0FA3A3'
}

export default function CampaignGraph({ nodes, links }: Props) {
  const fgRef = useRef<any>(null)

  const handleNodeClick = useCallback((node: GraphNode) => {
    if (fgRef.current) {
      fgRef.current.centerAt(node.x, node.y, 600)
      fgRef.current.zoom(3, 600)
    }
  }, [])

  const drawNode = useCallback((node: GraphNode, ctx: CanvasRenderingContext2D, globalScale: number) => {
    const size = NODE_SIZES[node.type] || 6
    const color = getRiskColor(node)

    ctx.beginPath()
    ctx.arc(node.x!, node.y!, size, 0, 2 * Math.PI)
    ctx.fillStyle = color
    ctx.fill()

    // Glow effect for high-risk reports
    if (node.type === 'report' && node.label_risk === 'High Risk') {
      ctx.beginPath()
      ctx.arc(node.x!, node.y!, size + 3, 0, 2 * Math.PI)
      ctx.strokeStyle = `${color}44`
      ctx.lineWidth = 2
      ctx.stroke()
    }

    // Label
    if (globalScale > 1.5) {
      ctx.font = `${10 / globalScale}px Inter, sans-serif`
      ctx.fillStyle = 'rgba(255,255,255,0.8)'
      ctx.textAlign = 'center'
      ctx.textBaseline = 'top'
      ctx.fillText(node.label.slice(0, 20), node.x!, node.y! + size + 2)
    }
  }, [])

  if (nodes.length === 0) {
    return (
      <div className="flex items-center justify-center h-64 text-white/40">
        No graph data available
      </div>
    )
  }

  return (
    <div className="w-full rounded-xl overflow-hidden bg-navy/50 border border-white/10">
      <ForceGraph2D
        ref={fgRef}
        graphData={{ nodes: nodes as any[], links: links as any[] }}
        width={undefined}
        height={420}
        backgroundColor="#0B1B2B"
        nodeCanvasObject={drawNode as any}
        nodePointerAreaPaint={(node: any, color, ctx) => {
          const size = NODE_SIZES[node.type] || 6
          ctx.fillStyle = color
          ctx.beginPath()
          ctx.arc(node.x, node.y, size + 2, 0, 2 * Math.PI)
          ctx.fill()
        }}
        linkColor={() => 'rgba(255,255,255,0.15)'}
        linkWidth={1.5}
        linkDirectionalParticles={2}
        linkDirectionalParticleSpeed={0.004}
        linkDirectionalParticleColor={() => '#F28C28'}
        onNodeClick={handleNodeClick as any}
        cooldownTicks={80}
        d3AlphaDecay={0.02}
        d3VelocityDecay={0.3}
        nodeLabel={(node: any) => `${node.type.toUpperCase()}: ${node.label}`}
      />
      {/* Legend */}
      <div className="flex flex-wrap gap-4 p-3 border-t border-white/10">
        {Object.entries(NODE_COLORS).map(([type, color]) => (
          <div key={type} className="flex items-center gap-1.5 text-xs text-white/60">
            <div className="w-3 h-3 rounded-full" style={{ backgroundColor: color }} />
            <span className="capitalize">{type}</span>
          </div>
        ))}
        <div className="flex items-center gap-1.5 text-xs text-white/60">
          <div className="w-3 h-3 rounded-full bg-alert-red" />
          <span>High Risk Report</span>
        </div>
      </div>
    </div>
  )
}
