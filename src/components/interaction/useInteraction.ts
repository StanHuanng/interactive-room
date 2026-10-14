import { createContext, useContext } from 'react'
import type { Seat } from '../room/layout'

export type Focus = 'mac' | 'article'

export type InteractionState = {
  seat: Seat | null
  nearby: Seat | null
  sit: (seat: Seat) => void
  stand: () => void
  setNearby: (seat: Seat | null) => void
  focus: Focus | null
  returning: boolean
  openFocus: (focus: Focus) => void
  closeFocus: () => void
  finishReturn: () => void
}
export const InteractionContext = createContext<InteractionState | null>(null)

export function useInteraction() {
  const context = useContext(InteractionContext)
  if (!context) throw new Error('InteractionProvider is required')
  return context
}
