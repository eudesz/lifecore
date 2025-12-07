import React, { useState } from 'react'
import ProtectedRoute from '@/components/auth/ProtectedRoute'

type TestResult = {
  scenario: string
  avg_score: number
  scores: Record<string, number>
}

export default function TestingPage() {
  const [running, setRunning] = useState(false)
  const [results, setResults] = useState<TestResult[] | null>(null)
  const [error, setError] = useState<string | null>(null)

  const runTests = async () => {
    try {
      setRunning(true)
      setError(null)
      setResults(null)
      // Placeholder: En una implementación real, esto llamaría a un endpoint backend
      // que orquesta la suite de regresión con LLM y retorna resultados.
      await new Promise(res => setTimeout(res, 1200))
      setResults([
        { scenario: 'Diagnóstico inicial de diabetes', avg_score: 8.2, scores: { coherence: 8, accuracy: 8, continuity: 9, tone: 8 } },
        { scenario: 'Evolución de tratamiento', avg_score: 7.9, scores: { coherence: 8, accuracy: 8, continuity: 8, tone: 7 } },
      ])
    } catch (e: any) {
      setError(e.message)
    } finally {
      setRunning(false)
    }
  }

  return (
    <ProtectedRoute>
      <main id="content" className="container" style={{ paddingTop: 'var(--space-lg)' }}>
        <h1>Testing Conversacional (LLM)</h1>
        <p className="muted">Ejecuta pruebas automáticas de conversación y evalúa respuestas con LLM.</p>
        <div className="card" style={{ padding: 16, marginTop: 12 }}>
          <button className="btn" onClick={runTests} disabled={running}>
            {running ? 'Ejecutando…' : 'Run Tests'}
          </button>
        </div>
        {error && <div style={{ color: '#b91c1c', marginTop: 12 }}>Error: {error}</div>}
        {results && (
          <section className="card" style={{ marginTop: 16 }}>
            <h3 style={{ margin: '12px 16px' }}>Resultados</h3>
            <table className="table">
              <thead>
                <tr>
                  <th>Escenario</th>
                  <th>Promedio</th>
                  <th>Coherencia</th>
                  <th>Precisión</th>
                  <th>Continuidad</th>
                  <th>Tono</th>
                </tr>
              </thead>
              <tbody>
                {results.map((r, idx) => (
                  <tr key={idx}>
                    <td>{r.scenario}</td>
                    <td>{r.avg_score}</td>
                    <td>{r.scores.coherence}</td>
                    <td>{r.scores.accuracy}</td>
                    <td>{r.scores.continuity}</td>
                    <td>{r.scores.tone}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </section>
        )}
      </main>
    </ProtectedRoute>
  )
}


