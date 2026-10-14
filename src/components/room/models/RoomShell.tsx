import { roomLayout } from '../layout'
import { Model } from './Model'

export function RoomShell() {
  return <Model asset="room" scale={roomLayout.shellScale} />
}
