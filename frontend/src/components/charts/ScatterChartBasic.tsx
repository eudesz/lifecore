import React from 'react'

let Recharts: any = null
try {
  // eslint-disable-next-line @typescript-eslint/no-var-requires
  const mod = require('recharts')
  Recharts = mod && mod.default ? mod.default : mod
} catch {}

export default function ScatterChartBasic({ x, y, title }: { x: number[]; y: number[]; title?: string }) {
  const Lib = Recharts
  if (!Lib || !Lib.ScatterChart || !Lib.ResponsiveContainer) return <div style={{ color: '#6b7280' }}>Gráfico no disponible (instalar recharts)</div>
  const { ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } = Lib
  const n = Math.min(x.length, y.length)
  const data = Array.from({ length: n }).map((_, i) => ({ x: x[i], y: y[i] }))
  return (
    <div style={{ height: 260 }}>
      <ResponsiveContainer width="100%" height="100%">
        <ScatterChart margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
          <CartesianGrid />
          <XAxis type="number" dataKey="x" />
          <YAxis type="number" dataKey="y" />
          <Tooltip cursor={{ strokeDasharray: '3 3' }} />
          <Scatter data={data} fill="#7c3aed" />
        </ScatterChart>
      </ResponsiveContainer>
    </div>
  )
}
