import React, { useEffect, useRef, useState } from 'react'
import dynamic from 'next/dynamic'
import { useAuth } from '@/context/AuthContext'

// Dynamic import to avoid SSR issues with canvas
const ForceGraph2D = dynamic(() => import('react-force-graph-2d'), {
  ssr: false,
  loading: () => <div style={{ padding: 20, color: 'var(--text-muted)' }}>Loading Graph Engine...</div>
})

interface GraphData {
  nodes: any[]
  links: any[]
}

export default function KnowledgeGraph() {
  const { user } = useAuth()
  const [data, setData] = useState<GraphData>({ nodes: [], links: [] })
  const fgRef = useRef<any>()
  const [fullscreen, setFullscreen] = useState(false)
  const [selectedNode, setSelectedNode] = useState<any | null>(null)

  useEffect(() => {
    if (!user) return
    const token = window.localStorage.getItem('PLATFORM_API_KEY')
    
    fetch(`/api/lifecore/graph?user_id=${user.id}`, {
      headers: token ? { 'Authorization': `Bearer ${token}` } : {}
    })
      .then(res => res.json())
      .then(json => {
        if (json.nodes) setData(json)
      })
      .catch(err => console.error("Graph fetch error:", err))
  }, [user])

  const outerStyle: React.CSSProperties = fullscreen
    ? {
        position: 'fixed',
        inset: 0,
        zIndex: 1000,
        background: 'rgba(3, 7, 18, 0.96)',
        padding: '24px',
      }
    : {
        height: '100%',
        minHeight: '320px',
        width: '100%',
        overflow: 'hidden',
      }

  const innerStyle: React.CSSProperties = fullscreen
    ? {
        height: '100%',
        width: '100%',
        borderRadius: 'var(--radius-lg)',
        border: '1px solid var(--border-light)',
        background: 'var(--bg-dark)',
        position: 'relative',
      }
    : {
        height: '100%',
        width: '100%',
        position: 'relative',
      }

  return (
    <div style={outerStyle}>
      <div style={innerStyle}>
        <div
          style={{
            position: 'absolute',
            top: 8,
            right: 8,
            zIndex: 10,
            display: 'flex',
            gap: 8,
          }}
        >
          {fullscreen && (
            <span
              style={{
                fontSize: 12,
                color: 'var(--text-muted)',
                marginRight: 8,
                alignSelf: 'center',
              }}
            >
              Fullscreen graph view
            </span>
          )}
          <button
            type="button"
            onClick={() => setFullscreen(f => !f)}
            className="btn secondary"
            style={{ padding: '4px 10px', fontSize: 11 }}
          >
            {fullscreen ? 'Exit Fullscreen' : 'Fullscreen'}
          </button>
        </div>
      {data.nodes.length === 0 ? (
        <div style={{ 
          height: '100%', 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'center',
          flexDirection: 'column',
          color: 'var(--text-muted)'
        }}>
          <p>No graph data available.</p>
          <small>Ensure Neo4j is running and data is synced.</small>
        </div>
      ) : (
        <ForceGraph2D
          ref={fgRef}
          graphData={data}
          nodeLabel="label"
          nodeAutoColorBy="group"
          nodeVal={val => (val as any).val}
          linkColor={() => 'rgba(148, 163, 184, 0.2)'}
          linkWidth={0.5}
          linkDirectionalArrowLength={2}
          linkDirectionalArrowRelPos={1}
          linkDirectionalParticles={fullscreen ? 1 : 0}
          linkDirectionalParticleWidth={1.5}
          d3Force="charge"
          d3ForceStrength={-120}
          d3ForceLinkDistance={50}
          backgroundColor="rgba(0,0,0,0)"
          onNodeClick={node => {
            // Center on click with safety check
            if (fgRef.current) {
              // Check if methods exist (dynamic ref forwarding can vary)
              if (typeof fgRef.current.centerAt === 'function') {
                fgRef.current.centerAt(node.x, node.y, 1000)
              }
              if (typeof fgRef.current.zoom === 'function') {
                fgRef.current.zoom(8, 2000)
              }
            }
            setSelectedNode(node)
          }}
          d3VelocityDecay={0.4}
          d3AlphaDecay={0.01}
          cooldownTicks={100}
          onEngineStop={() => {
            if (fgRef.current && typeof fgRef.current.zoomToFit === 'function') {
              fgRef.current.zoomToFit(400, 20)
            }
          }}
          nodeCanvasObject={(node, ctx, globalScale) => {
            const n: any = node
            const label: string = n.label || ''
            const group: string = n.group
            const color = n.color || getNodeColor(group)
            
            // Highlight selected
            const isSelected = selectedNode && selectedNode.id === n.id
            const isImportant = group === 'Condition' || group === 'Patient'

            // Dynamic radius: Condition/Patient bigger, others smaller
            let baseR = 3
            if (group === 'Patient') baseR = 8
            else if (group === 'Condition') baseR = 6
            else if (group === 'Event') baseR = 2.5
            else if (group === 'Document') baseR = 2
            
            const radius = isSelected ? baseR * 1.5 : baseR

            // Draw circle
            ctx.beginPath()
            ctx.arc(n.x || 0, n.y || 0, radius, 0, 2 * Math.PI, false)
            ctx.fillStyle = isSelected ? '#ffffff' : color
            ctx.fill()
            
            // Stroke for selected or patient
            if (isSelected || group === 'Patient') {
               ctx.lineWidth = 1.5 / globalScale
               ctx.strokeStyle = isSelected ? color : '#ffffff'
               ctx.stroke()
            }

            // Text Rendering Logic:
            // 1. If selected -> show label
            // 2. If zoomed in heavily (scale > 3.5) -> show all
            // 3. If moderate zoom (scale > 1.2) -> show only Conditions/Patient
            // 4. Otherwise hide text to reduce clutter
            const showText = isSelected || (globalScale > 3.5) || (isImportant && globalScale > 1.2)

            if (showText) {
              const MAX_LABEL_LEN = isSelected ? 40 : 20
              let printLabel = label
              if (printLabel.length > MAX_LABEL_LEN) {
                  printLabel = printLabel.slice(0, MAX_LABEL_LEN) + '…'
              }
              
              const fontSize = (isSelected ? 14 : 10) / globalScale
              ctx.font = `${isSelected ? 'bold ' : ''}${fontSize}px Roboto, Sans-Serif`
              
              // Text Background for readability
              const textWidth = ctx.measureText(printLabel).width
              const bkgPad = 2 / globalScale
              ctx.fillStyle = 'rgba(0, 0, 0, 0.7)'
              ctx.fillRect(
                (n.x || 0) - textWidth / 2 - bkgPad, 
                (n.y || 0) + radius + (2 / globalScale) - bkgPad, 
                textWidth + bkgPad * 2, 
                fontSize + bkgPad * 2
              )

              ctx.textAlign = 'center'
              ctx.textBaseline = 'top'
              ctx.fillStyle = isSelected ? '#ffffff' : '#e2e8f0'
              ctx.fillText(printLabel, n.x || 0, (n.y || 0) + radius + (2 / globalScale))
            }
          }}
        />
      )}
      {selectedNode && (
        <div
          style={{
            position: 'absolute',
            left: 16,
            bottom: 16,
            maxWidth: fullscreen ? 320 : 260,
            maxHeight: '60%',
            overflowY: 'auto',
            padding: '14px 16px',
            borderRadius: 16,
            background: 'rgba(9, 14, 26, 0.95)',
            backdropFilter: 'blur(10px)',
            border: '1px solid var(--border-light)',
            fontSize: 12,
            color: 'var(--text-main)',
            boxShadow: '0 10px 30px rgba(0,0,0,0.5)'
          }}
        >
          <div style={{ fontSize: 10, textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--text-muted)', marginBottom: 6 }}>
            {selectedNode.group || 'Node'}
          </div>
          
          <div style={{ fontWeight: 600, fontSize: 14, marginBottom: 12, lineHeight: 1.4 }}>
            {selectedNode.label}
          </div>

          {selectedNode.properties && Object.keys(selectedNode.properties).length > 0 && (
            <div style={{ display: 'grid', gap: 8, marginBottom: 12 }}>
              {Object.entries(selectedNode.properties).map(([key, val]) => {
                 if (key === 'id' || key === 'title' || key === 'name') return null // Skip redundant info
                 // Format dates nicely
                 let displayVal = String(val)
                 if (key === 'date' || key === 'created_at') {
                   try { displayVal = new Date(val as string).toLocaleDateString() } catch {}
                 }
                 return (
                   <div key={key} style={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                     <span style={{ color: 'var(--text-muted)', fontSize: 10, textTransform: 'uppercase' }}>{key}</span>
                     <span style={{ color: 'var(--text-main)', fontFamily: 'monospace', fontSize: 11 }}>{displayVal}</span>
                   </div>
                 )
              })}
            </div>
          )}

          <div style={{ fontSize: 11, color: 'var(--text-dim)', borderTop: '1px solid var(--border-light)', paddingTop: 8, marginTop: 8 }}>
            Double-click to center. Drag to move.
          </div>
        </div>
      )}
      </div>
    </div>
  )
}

function getNodeColor(group: string) {
  switch (group) {
    case 'Patient': return '#00f2ea' // Cyan
    case 'Condition': return '#ef4444' // Red
    case 'Medication': return '#10b981' // Green
    case 'Document': return '#64748b' // Slate-500 (less visually heavy than Gray)
    case 'Event': return '#eab308' // Yellow
    case 'Lab': return '#8b5cf6' // Violet
    default: return '#6366f1' // Purple
  }
}

