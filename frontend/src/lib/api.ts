function getApiKey(): string | undefined {
  if (process.env.NEXT_PUBLIC_PLATFORM_API_KEY) return process.env.NEXT_PUBLIC_PLATFORM_API_KEY
  if (typeof window !== 'undefined') {
    const v = localStorage.getItem('PLATFORM_API_KEY')
    return v || undefined
  }
  return undefined
}

export async function fetchObservations(params: { user_id: string; code?: string; since?: string; until?: string }) {
  const qs = new URLSearchParams(params as any).toString()
  const key = getApiKey()
  const res = await fetch(`/api/lifecore/observations/list?${qs}`, {
    headers: key ? { Authorization: `Bearer ${key}` } : undefined,
  })
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  return res.json() as Promise<{ observations: any[] }>
}

export async function analyze(
  query: string,
  user_id: string,
  opts?: Partial<{ code: string; code1: string; code2: string; ma_window: number; z_threshold: number; since: string; until: string; conversation_id: string; context_filters: { conditions?: string[]; categories?: string[]; date_from?: string; date_to?: string } }>
) {
  const key = getApiKey()
  const body = { query, user_id, ...(opts || {}) }
  const res = await fetch('/api/agents/v2/analyze', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...(key ? { Authorization: `Bearer ${key}` } : {}),
    },
    body: JSON.stringify(body)
  })
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  return res.json()
}

export async function downloadReport(path: string, params: Record<string, string>) {
  const qs = new URLSearchParams(params).toString()
  const key = getApiKey()
  const res = await fetch(`${path}?${qs}`, {
    headers: key ? { Authorization: `Bearer ${key}` } : undefined,
  })
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  const blob = await res.blob()
  const url = window.URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = path.endsWith('.csv') ? 'observations.csv' : 'summary.md'
  document.body.appendChild(a)
  a.click()
  a.remove()
  window.URL.revokeObjectURL(url)
}

export async function createMoodCheckin(params: { user: string; score: number; note?: string }) {
  const key = getApiKey()
  const res = await fetch('/api/lifecore/mood', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...(key ? { Authorization: `Bearer ${key}` } : {}),
    },
    body: JSON.stringify(params),
  })
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  return res.json() as Promise<{ status: string; id: number }>
}

export async function listMood(params: { user_id: string; days?: number }) {
  const qs = new URLSearchParams({ user_id: params.user_id, ...(params.days ? { days: String(params.days) } : {}) }).toString()
  const key = getApiKey()
  const res = await fetch(`/api/lifecore/mood?${qs}`, {
    headers: key ? { Authorization: `Bearer ${key}` } : undefined,
  })
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  return res.json() as Promise<{ mood: { taken_at: string; score: number; note?: string }[] }>
}

export interface IntelligentPrompt {
  prompt: string
  category: string
  type: string
  priority: 'high' | 'medium' | 'low'
  emoji: string
  insight: string
  score: number
}

export interface DataCategory {
  code: string
  emoji: string
  label: string
  count: number
  status: 'good' | 'warning' | 'neutral'
  last_update: string | null
}

export interface IntelligentPromptsResponse {
  user_id: number
  username: string
  categories: DataCategory[]
  intelligent_prompts: IntelligentPrompt[]
  summary: {
    total_categories: number
    total_observations: number
    total_documents: number
  }
}

export async function getIntelligentPrompts(userId: string): Promise<IntelligentPromptsResponse> {
  const key = getApiKey()
  const res = await fetch(`/api/prompts/intelligent?user_id=${userId}`, {
    headers: key ? { Authorization: `Bearer ${key}` } : undefined,
  })
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  return res.json()
}

export async function fetchTimelineAdvanced(params: {
  user_id: string
  date_from?: string
  date_to?: string
  categories?: string[]
  conditions?: string[]
  severity?: string
}) {
  const qs = new URLSearchParams({ user_id: params.user_id })
  if (params.date_from) qs.set('date_from', params.date_from)
  if (params.date_to) qs.set('date_to', params.date_to)
  if (params.categories?.length) qs.set('categories', params.categories.join(','))
  if (params.conditions?.length) qs.set('conditions', params.conditions.join(','))
  if (params.severity) qs.set('severity', params.severity)
  const key = getApiKey()
  const res = await fetch(`/api/lifecore/timeline/advanced?${qs.toString()}`, {
    headers: key ? { Authorization: `Bearer ${key}` } : undefined,
  })
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  return res.json() as Promise<{ events: any[]; conditions?: Array<{ condition: { slug: string; name: string; color: string }; lanes: Array<{ category: string; events: any[] }> }>; total: number }>
}

export async function fetchTreatmentsList(user_id: string) {
  const qs = new URLSearchParams({ user_id }).toString()
  const key = getApiKey()
  const res = await fetch(`/api/lifecore/treatments/list?${qs}`, {
    headers: key ? { Authorization: `Bearer ${key}` } : undefined,
  })
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  return res.json() as Promise<{ treatments: any[] }>
}

export async function fetchTreatmentsAdherence(user_id: string, days: number = 30) {
  const qs = new URLSearchParams({ user_id, days: String(days) }).toString()
  const key = getApiKey()
  const res = await fetch(`/api/lifecore/treatments/adherence?${qs}`, {
    headers: key ? { Authorization: `Bearer ${key}` } : undefined,
  })
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  return res.json() as Promise<{ scheduled: number; taken: number; adherence_pct: number; days: number }>
}

export async function fetchConditionsList(user_id: string) {
  const key = getApiKey()
  const res = await fetch(`/api/lifecore/conditions/list?user_id=${user_id}`, {
    headers: key ? { Authorization: `Bearer ${key}` } : undefined,
  })
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  return res.json() as Promise<{ conditions: Array<{ slug: string; name: string; color: string; count: number }> }>
}

export async function fetchDocumentsList(user_id: string) {
  const key = getApiKey()
  const res = await fetch(`/api/lifecore/documents/list?user_id=${user_id}`, {
    headers: key ? { Authorization: `Bearer ${key}` } : undefined,
  })
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  return res.json() as Promise<{ documents: Array<{ id: number; title: string; content: string; source?: string; created_at?: string }> }>
}

