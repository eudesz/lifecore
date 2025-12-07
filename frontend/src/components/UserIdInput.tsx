import { useRouter } from 'next/router'
import { useEffect, useState } from 'react'

export default function UserIdInput() {
  const router = useRouter()
  const [value, setValue] = useState('')

  useEffect(() => {
    const q = router.query?.user_id
    if (typeof q === 'string') setValue(q)
  }, [router.query?.user_id])

  const apply = () => {
    const query = { ...(router.query || {}) }
    if (value) (query as any).user_id = value
    else delete (query as any).user_id
    router.push({ pathname: router.pathname, query }, undefined, { shallow: true })
  }

  return (
    <div style={{ display: 'flex', gap: 8, alignItems: 'center', marginBottom: 12 }}>
      <label style={{ color: '#374151' }}>Usuario</label>
      <input value={value} onChange={e => setValue(e.target.value)} placeholder="user_id" style={{ padding: 6 }} />
      <button onClick={apply} style={{ padding: '6px 10px' }}>Aplicar</button>
    </div>
  )
}
