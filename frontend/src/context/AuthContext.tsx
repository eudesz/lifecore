import React, { createContext, useContext, useState, useEffect, type ReactNode } from 'react'

/**
 * Very lightweight auth context used mainly to provide a "current user"
 * for dashboards, chat and timeline pages.
 *
 * In this demo setup we keep the state purely on the client and
 * persist the last selected user id in localStorage so that it
 * survives reloads.
 */

export interface AuthUser {
  id: number
  name?: string
}

interface AuthContextValue {
  user: AuthUser | null
  setUser: (user: AuthUser | null) => void
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUserState] = useState<AuthUser | null>(null)

  useEffect(() => {
    if (typeof window === 'undefined') return
    try {
      const stored = window.localStorage.getItem('quantia_current_user')
      if (stored) {
        const parsed = JSON.parse(stored) as AuthUser
        if (parsed && typeof parsed.id === 'number') {
          setUserState(parsed)
          return
        }
      }
      // Default demo user
      setUserState({ id: 1, name: 'Demo user' })
    } catch {
      setUserState({ id: 1, name: 'Demo user' })
    }
  }, [])

  const setUser = (next: AuthUser | null) => {
    setUserState(next)
    if (typeof window === 'undefined') return
    try {
      if (next) {
        window.localStorage.setItem('quantia_current_user', JSON.stringify(next))
      } else {
        window.localStorage.removeItem('quantia_current_user')
      }
    } catch {
      // ignore storage errors
    }
  }

  return (
    <AuthContext.Provider value={{ user, setUser }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext)
  if (!ctx) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return ctx
}


