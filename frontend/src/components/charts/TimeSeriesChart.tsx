import React from 'react'

let Recharts: any = null
try {
  // eslint-disable-next-line @typescript-eslint/no-var-requires
  const mod = require('recharts')
  Recharts = mod && mod.default ? mod.default : mod
} catch {}

export default function TimeSeriesChart({ data, xKey = 'taken_at', yKey = 'value', title }: { data: any[]; xKey?: string; yKey?: string; title?: string }) {
  const Lib = Recharts
  if (!Lib || !Lib.LineChart || !Lib.ResponsiveContainer) {
    return <div style={{ color: '#6b7280' }}>Gráfico no disponible (instalar recharts)</div>
  }
  const { LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid, ResponsiveContainer } = Lib
  const mapped = (data || []).map(d => ({ ...d, taken_at: new Date(d[xKey]).toLocaleDateString() }))
  return (
    <div style={{ height: 260 }}>
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={mapped} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="taken_at" />
          <YAxis />
          <Tooltip />
          <Line type="monotone" dataKey={yKey} stroke="#7c3aed" dot={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}
