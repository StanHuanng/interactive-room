import { Suspense } from 'react'
import { Chair, Desk, Mac, Sofa } from './models/Furniture'
import { RoomShell } from './models/RoomShell'
import { roomLayout } from './layout'

export function Room() {
  return (
    <Suspense fallback={null}>
      <group>
        <RoomShell />
        <group position={roomLayout.desk}>
          <Desk />
          <Mac position={[0, roomLayout.deskHeight, 0]} />
        </group>
        <Chair position={roomLayout.chair} rotation={[0, Math.PI, 0]} />
        <Sofa position={roomLayout.sofa} />
      </group>
    </Suspense>
  )
}
