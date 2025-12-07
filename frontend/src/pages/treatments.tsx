import React, { useEffect, useState } from 'react'
import ProtectedRoute from '@/components/auth/ProtectedRoute'
import RequireApiKey from '@/components/RequireApiKey'
import { useAuth } from '@/context/AuthContext'
import { fetchTreatmentsAdherence, fetchTreatmentsList } from '@/lib/api'

type Treatment = {
  id: number
  name: string
  condition: string
  dosage: string
  frequency: string
  status: string
  start_date: string
  end_date?: string | null
}

export default function TreatmentsPage() {
  const { user } = useAuth()
  const userId = user?.id?.toString() || ''
  const [treatments, setTreatments] = useState<Treatment[]>([])
  const [adherence, setAdherence] = useState<{ scheduled: number; taken: number; adherence_pct: number } | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!userId) return
    const load = async () => {
      try {
        setLoading(true)
        setError(null)
        const data = await fetchTreatmentsList(userId)
        setTreatments(data.treatments || [])
        const d2 = await fetchTreatmentsAdherence(userId, 30)
        setAdherence(d2)
      } catch (e: any) {
        setError(e.message)
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [userId])

  return (
    <ProtectedRoute>
      <RequireApiKey>
      <main id="content" className="container" style={{ paddingTop: 'var(--space-lg)' }}>
        <h1>Treatments</h1>
        <p style={{ color: 'var(--text-muted)' }}>Current and historical treatments, with adherence.</p>

        <section className="card" style={{ marginTop: 16 }}>
          {loading && <div style={{ padding: 16, color: '#6b7280' }}>Loading treatments…</div>}
          {error && <div style={{ padding: 16, color: '#b91c1c' }}>Error: {error}</div>}
          {!loading && !error && (
            <>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(240px, 1fr))', gap: 12 }}>
                {treatments.map(t => (
                  <div key={t.id} className="card" style={{ padding: 12 }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline' }}>
                      <h3 style={{ margin: 0 }}>{t.name}</h3>
                      <span className="muted">{t.status}</span>
                    </div>
                    <div style={{ marginTop: 8, color: '#374151' }}>
                      <div><strong>Condición:</strong> {t.condition}</div>
                      <div><strong>Dosis:</strong> {t.dosage}</div>
                      <div><strong>Frecuencia:</strong> {t.frequency}</div>
                      <div><strong>Inicio:</strong> {new Date(t.start_date).toLocaleDateString()}</div>
                      {t.end_date && <div><strong>Fin:</strong> {new Date(t.end_date).toLocaleDateString()}</div>}
                    </div>
                  </div>
                ))}
              </div>

              <div className="card" style={{ marginTop: 16, padding: 12 }}>
                <h3 style={{ marginTop: 0 }}>Adherence (last 30 days)</h3>
                {adherence ? (
                  <div style={{ display: 'flex', gap: 16, alignItems: 'center', flexWrap: 'wrap' }}>
                    <div>Scheduled: <strong>{adherence.scheduled}</strong></div>
                    <div>Taken: <strong>{adherence.taken}</strong></div>
                    <div>Adherence: <strong>{adherence.adherence_pct}%</strong></div>
                  </div>
                ) : (
                  <div className="muted">No adherence data yet.</div>
                )}
              </div>
            </>
          )}
        </section>
      </main>
      </RequireApiKey>
    </ProtectedRoute>
  )
}


