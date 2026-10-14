import { useState } from 'react'
import type { ReactNode } from 'react'
import type { Seat } from '../room/layout'
import { InteractionContext } from './useInteraction'

export function InteractionProvider({ children }: { children: ReactNode }) {
  const [seat, setSeat] = useState<Seat | null>(null)
  const [nearby, setNearby] = useState<Seat | null>(null)
  const sit = (target: Seat) => {
    document.exitPointerLock?.()
    setSeat(target)
  }
  return <InteractionContext.Provider value={{ seat, nearby, sit, stand: () => setSeat(null), setNearby }}>
    {children}
  </InteractionContext.Provider>
}
