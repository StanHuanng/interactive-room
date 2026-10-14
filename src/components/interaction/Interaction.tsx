import { useCallback, useEffect, useState } from 'react'
import type { ReactNode } from 'react'
import type { Seat } from '../room/layout'
import { InteractionContext } from './useInteraction'
import type { Focus } from './useInteraction'

export function InteractionProvider({ children }: { children: ReactNode }) {
  const [seat, setSeat] = useState<Seat | null>(null)
  const [nearby, setNearby] = useState<Seat | null>(null)
  const [focus, setFocus] = useState<Focus | null>(null)
  const [returning, setReturning] = useState(false)
  const openFocus = useCallback((target: Focus) => {
    document.exitPointerLock?.()
    setReturning(false)
    setFocus(target)
  }, [])
  const closeFocus = useCallback(() => {
    setFocus(null)
    setReturning(true)
  }, [])
  const finishReturn = useCallback(() => setReturning(false), [])
  const sit = useCallback((target: Seat) => {
    document.exitPointerLock?.()
    setSeat(target)
  }, [])
  const stand = useCallback(() => setSeat(null), [])

  useEffect(() => {
    const escape = (event: KeyboardEvent) => {
      if (event.code === 'Escape' && focus) {
        event.preventDefault()
        closeFocus()
      }
    }
    window.addEventListener('keydown', escape)
    return () => window.removeEventListener('keydown', escape)
  }, [focus, closeFocus])

  return <InteractionContext.Provider value={{ seat, nearby, sit, stand, setNearby,
    focus, returning, openFocus, closeFocus, finishReturn }}>
    {children}
  </InteractionContext.Provider>
}
